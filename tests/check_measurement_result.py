"""Validate linkage, disjoint purchase partitions and nested scope/chain counts."""
import argparse
import json
import math
from pathlib import Path


def check(r,expected=None):
    checks=[]
    def require(test,label):
        if not test: raise AssertionError(label)
        checks.append(label)
    c=r['candidates']; link=r['linkage']
    require(c['candidate_transactions']==link['linked_candidate_transactions'],'no unmatched candidate IDs')
    require(c['agreeing_transactions']==link['linked_agreeing_transactions'],'agreeing-ID linkage')
    require(c['candidate_events']==link['candidate_events'],'candidate-event linkage')
    require(c['agreeing_recorded_value']==link['linked_agreeing_recorded_value'],'value linkage')
    require(link['keyed_purchase_events']==sum(link[k] for k in ['candidate_events','missing_id_events','rejected_id_events']),'purchase partition')
    require(0<=c['agreeing_transactions']<=c['native_complete_transactions']<=c['candidate_transactions']<=c['candidate_events'],'nested monetary populations')
    scopes={}
    for s in r['scopes']:
        key=(s['scope'],s['cohort_month'],s['session_device'])
        require(key not in scopes,'unique scope/cohort/device')
        scopes[key]=s
        require(0<=s['strict_candidate_sessions']<=s['strict_checkout_sessions']<=s['strict_cart_sessions']<=s['entry_sessions']<=s['sessions'],'nested chain '+str(key))
        require(s['strict_candidate_sessions']<=s['last_time_candidate_sessions']<=s['candidate_purchase_sessions']<=s['raw_purchase_sessions']<=s['sessions'],'earliest purchase sensitivity '+str(key))
        require(s['strict_candidate_sessions']<=s['tied_candidate_sessions']<=s['candidate_purchase_sessions'],'tie sensitivity '+str(key))
        require(s['candidate_purchase_sessions']<=s['candidate_transactions']<=s['candidate_events'],'order/visit grains '+str(key))
        require(s['raw_purchase_events']==sum(s[k] for k in ['missing_id_events','rejected_id_events','candidate_events']),'scope purchase partition '+str(key))
        require(s['mixed_outcome_sessions']<=s['unresolved_purchase_sessions']<=s['raw_purchase_sessions'],'unknown outcomes visible '+str(key))
        require(s['agreeing_transactions']<=s['native_complete_transactions']<=s['candidate_transactions'],'scope monetary coverage '+str(key))
        if s['agreeing_recorded_value'] is not None:
            require(math.isfinite(s['agreeing_recorded_value']) and s['agreeing_recorded_value']>=0,'finite selected value '+str(key))
        if s['scope']=='anchored_interior_single_date':require(s['long_sessions']==0,'long groups absent in single-date scope')
    for s in r['purchase_coverage']:
        require(s['raw_purchase_events']==sum(s[k] for k in ['missing_id_events','rejected_id_events','candidate_events']),'daily purchase partition')
    allrows=[s for s in r['scopes'] if s['scope']=='all_keyed']
    for k,out in [('sessions','keyed_sessions'),('raw_purchase_events','keyed_purchase_events'),('candidate_transactions','linked_candidate_transactions')]:
        require(sum(s[k] for s in allrows)==link[out],'all-keyed reconciliation '+k)
    require(sum(s['raw_purchase_events'] for s in r['purchase_coverage'])==link['keyed_purchase_events'],'all purchase events linked')
    for child,parent in [('anchored_interior','all_keyed'),('anchored_interior_single_date','anchored_interior')]:
        for key,s in scopes.items():
            if key[0]!=child:continue
            p=scopes[(parent,key[1],key[2])]
            require(all(s[k]<=p[k] for k in s if k not in ['scope','cohort_month','session_device','agreeing_recorded_value']),'scope nesting '+str(key))
    if expected:
        for section in ['linkage','candidates','long_span_review']:
            for k,v in expected[section].items():require(r[section][k]==v,'fixture '+section+'/'+k)
        for name,values in expected['scopes'].items():
            keys=['sessions','candidate_transactions','candidate_purchase_sessions','strict_candidate_sessions','last_time_candidate_sessions','tied_candidate_sessions']
            require(tuple(sum(s[k] for s in r['scopes'] if s['scope']==name) for k in keys)==tuple(values),'fixture scope '+name)
    return checks


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--expected',type=Path);a=p.parse_args()
    checks=check(json.loads(a.result.read_text()),json.loads(a.expected.read_text()) if a.expected else None)
    print(f'{len(checks)} measurement-gate checks passed.')
