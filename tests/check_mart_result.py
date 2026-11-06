"""Validate aggregate mart evidence and compare every scope cell with the accepted gate."""
import argparse
import json
import math
from pathlib import Path


def check(r,expected=None,gate=None):
    checks=[]
    def require(test,label):
        if not test:raise AssertionError(label)
        checks.append(label)
    require(len(r['checks'])==20 and len({c['check_name'] for c in r['checks']})==20,'twenty distinct warehouse assertions')
    require(all(c['passed'] is True for c in r['checks']),'warehouse assertions pass')
    fp={s['model']:s for s in r['fingerprints']}
    names={'stg_events','transaction_policy','fact_transactions','fact_transaction_items','fact_visits','audit_event_keys','audit_visit_exclusions','audit_purchase_coverage'}
    require(set(fp)==names and len(r['fingerprints'])==8,'eight distinct model fingerprints')
    require(fp['stg_events']['row_count']==r['source']['events'],'event grain')
    require(fp['transaction_policy']['row_count']==r['transaction_policy']['id_groups'],'policy grain')
    require(fp['fact_transactions']['row_count']==r['transactions']['transactions']==r['transaction_policy']['qualified_ids'],'transaction grain')
    require(fp['fact_transaction_items']['row_count']==r['transactions']['item_rows'],'item occurrence grain')
    require(sum(x['events'] for x in r['event_key_coverage'])==r['source']['events'],'event key ledger')
    require(sum(x['events'] for x in r['event_key_coverage'] if x['key_status']!='keyed_event')==r['source']['unkeyed_events'],'unkeyed events retained')
    require(sum(x['visits'] for x in r['visit_exclusions'])==fp['fact_visits']['row_count'],'disjoint visit ledger')
    require(sum(x['events'] for x in r['visit_exclusions'])==r['source']['events']-r['source']['unkeyed_events'],'keyed event conservation')
    require(sum(x['raw_purchase_events'] for x in r['purchase_coverage'])==r['source']['purchase_events'],'purchase coverage conservation')
    for x in r['purchase_coverage']:
        require(x['raw_purchase_events']==sum(x[k] for k in ['missing_id_events','rejected_id_events','candidate_events']),'purchase outcome partition')
    require(sum(x['candidate_events'] for x in r['purchase_coverage'])==r['transactions']['recorded_events'],'qualified event count')
    require(r['transactions']['selected_recorded_value'] is None or math.isfinite(r['transactions']['selected_recorded_value']),'finite selected value')
    scopes={}
    for s in r['scopes']:
        key=(s['scope'],s['cohort_month'],s['session_device'])
        require(key not in scopes,'unique scope cell');scopes[key]=s
        require(0<=s['strict_candidate_sessions']<=s['strict_checkout_sessions']<=s['strict_cart_sessions']<=s['entry_sessions']<=s['sessions'],'nested ordered population')
        require(s['strict_candidate_sessions']<=s['tied_candidate_sessions']<=s['candidate_purchase_sessions']<=s['candidate_transactions']<=s['candidate_events'],'timing and grain bounds')
        require(s['raw_purchase_events']==s['missing_id_events']+s['rejected_id_events']+s['candidate_events'],'scope purchase partition')
    allrows=[x for x in r['scopes'] if x['scope']=='all_keyed']
    require(sum(x['sessions'] for x in allrows)==fp['fact_visits']['row_count'],'visit scope conservation')
    require(sum(x['candidate_transactions'] for x in allrows)==r['transactions']['transactions'],'transaction visit conservation')
    primary=[x for x in r['scopes'] if x['scope']=='anchored_interior_single_date' and x['cohort_month']=='202012']
    require(sum(x['sessions'] for x in primary)==sum(x['visits'] for x in r['visit_exclusions'] if x['exclusion_reason']=='eligible_primary'),'primary eligibility ledger')
    if expected:
        for section in ['source','transaction_policy','transactions']:
            for k,v in expected[section].items():require(r[section][k]==v,'fixture '+section+'/'+k)
        for k,v in expected['primary'].items():require(sum(x[k] or 0 for x in primary)==v,'fixture primary/'+k)
    if gate:
        previous={(s['scope'],s['cohort_month'],s['session_device']):s for s in gate['scopes']}
        require(set(scopes)==set(previous),'accepted scope cells retained')
        for key,s in scopes.items():
            for k,v in previous[key].items():require(s[k]==v,'accepted scope '+str(key)+'/'+k)
        require(r['source']['events']==gate['linkage']['keyed_events'] and r['source']['unkeyed_events']==0,'accepted source events')
        require(r['transactions']['transactions']==gate['candidates']['candidate_transactions'],'accepted transactions')
        require(r['transactions']['selected_recorded_value']==gate['candidates']['agreeing_recorded_value'],'accepted selected value')
    return checks


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--expected',type=Path);p.add_argument('--gate',type=Path);a=p.parse_args()
    read=lambda f:json.loads(f.read_text()) if f else None
    print(f'{len(check(read(a.result),read(a.expected),read(a.gate)))} mart evidence checks passed.')
