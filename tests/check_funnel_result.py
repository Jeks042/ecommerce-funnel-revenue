"""Reconcile daily aggregates, independent source calculation and accepted marts."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyse_funnel import METRICS,total,analyse
ROOT=Path(__file__).resolve().parents[1]


def check(data,reverse,fixture=False):
    checks=[]
    def require(ok,label):
        if not ok:raise AssertionError(label)
        checks.append(label)
    rows=data['daily_device']
    keys=[(r['scope'],r['visit_date'],r['device']) for r in rows]
    require(len(keys)==len(set(keys)),'Unique scope/date/device cells')
    for r in rows+data['context_summary']+data['daily_context']:
        require(all(type(r[k]) is int and r[k]>=0 for k in METRICS),'Nonnegative integer counts')
        for prefix in ['strict','tied','unordered']:
            counts=[r['sessions'],r['entry_sessions'],r[prefix+'_cart_sessions'],r[prefix+'_checkout_sessions'],r[prefix+'_candidate_sessions']]
            require(counts==sorted(counts,reverse=True),'Nested '+prefix+' chain')
        for step in ['cart','checkout','candidate']:
            require(r['strict_'+step+'_sessions']<=r['tied_'+step+'_sessions']<=r['unordered_'+step+'_sessions'],'Ordered/tied/presence containment')
        require(r['strict_candidate_sessions']<=r['strict_raw_purchase_sessions'],'Qualified chain is observed raw chain')
        require(r['candidate_purchase_sessions']<=r['candidate_transactions'],'Orders never fewer than buying visits')
        require(r['raw_only_with_unresolved_ids_sessions']<=r['raw_only_completion_sessions'],'Unresolved coverage containment')
    primary={(r['visit_date'],r['device']):r for r in rows if r['scope']=='primary'}
    independent={(r['visit_date'],r['device']):r for r in reverse['daily_independent']}
    require(len(independent)==len(reverse['daily_independent']),'Unique independent cells')
    require(primary.keys()==independent.keys(),'Complete independent date/device coverage')
    for key,r in independent.items():
        for metric,value in r.items():
            if metric not in ['visit_date','device']:
                require(primary[key][metric]==value,'Independent reverse calculation: '+str(key)+' '+metric)
    require(total(primary.values())==total(data['context_summary']),'Context totals reconcile to primary device totals')
    for c in data['admitted_contexts']:
        select=lambda r:all(r[k]==c[k] for k in ['first_user_source','first_user_medium'])
        require(total([r for r in data['daily_context'] if select(r)])==total([r for r in data['context_summary'] if select(r)]),'Context date coverage reconciles')
    if fixture:
        expected=dict(zip(METRICS,[13,13,11,11,5,12,12,6,10,11,13,13,8,8,9,17,1,5,4,4,4,0,5,4]))
        for k,v in expected.items():require(total(primary.values())[k]==v,'Known adversarial fixture: '+k)
        require(not data['admitted_contexts'] and not data['daily_context'],'Small fixture context not ranked')
    else:
        require(set(r['scope'] for r in rows)=={'primary','anchored_interior','all_keyed'},'All sensitivity scopes retained')
        require(set(r['visit_date'] for r in primary.values())=={'2020-12-'+str(d).zfill(2) for d in range(1,32)},'31 primary December dates')
        baseline=json.loads((ROOT/'reports/evidence/marts-20261106.json').read_text())
        for b in baseline['scopes']:
            if b['cohort_month']!='202012':continue
            scope='primary' if b['scope']=='anchored_interior_single_date' else b['scope']
            current=total([r for r in rows if r['scope']==scope and r['device']==b['session_device']])
            for k in current.keys()&b.keys():require(current[k]==b[k],'Accepted scope/device baseline '+b['scope']+' '+b['session_device']+' '+k)
            require(current['unresolved_sessions']==b['unresolved_purchase_sessions'],'Unresolved baseline')
        fingerprints=json.loads((ROOT/'reports/evidence/marts-reproduction-20261106.json').read_text())['models']
        for f in data['input_fingerprints']:
            prior=next(x for x in fingerprints if x['model']==f['model'])
            require(int(f['row_count'])==int(prior['row_count']) and f['content_checksum']==prior['content_checksum'],'Accepted input count and fingerprint '+f['model'])
        require({f['model'] for f in data['input_fingerprints']}=={'stg_events','fact_visits','fact_transactions'},'Three model fingerprints')
    return checks


def read(name):return json.loads((ROOT/'reports/evidence'/name).read_text())


if __name__=='__main__':
    f=check(read('funnel-fixture-20261110.json'),read('funnel-reverse-fixture-20261110.json'),True)
    s=check(read('funnel-20261110.json'),read('funnel-reverse-20261110.json'))
    assert analyse(read('funnel-20261110.json'))==read('funnel-analysis-20261110.json')
    print(f'Funnel validation passed: {len(f)} fixture and {len(s)} source/reconciliation checks; Python summary reproduced.')
