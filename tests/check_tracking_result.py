"""Reconcile aggregate tracking/timing evidence without credentials."""
import argparse
import json
from pathlib import Path


def check(r,expected=None):
    passed=[]

    def require(ok,label):
        if not ok:
            raise ValueError(label)
        passed.append(label)

    p=r['population']; s=r['session_checks']; rows=r['daily_device_coverage']
    scopes={x['scope']:x for x in r['scope_sensitivity']}; all_rows=scopes['all_keyed']
    require(len(scopes)==len(r['scope_sensitivity'])==6,'six unique scopes')
    require(sum(x['events'] for x in rows)==p['events'],'daily event partition')
    require(sum(x['ineligible_key_events'] for x in rows)==p['ineligible_key_events'],'daily key partition')
    require(len({x['source_suffix'] for x in rows})==p['source_days'],'source day coverage')
    require(len({(x['source_suffix'],x['device']) for x in rows})==len(rows),'unique date/device rows')
    require(all_rows['events']+p['ineligible_key_events']==p['events'],'keyed/unkeyed event partition')
    require(all_rows['sessions']==s['keyed_sessions'],'session population')
    require(scopes['one_start']['sessions']+s['without_start']+s['repeated_starts']==s['keyed_sessions'],'start partition')
    require(scopes['all_keyed_interior']['sessions']+s['edge_sessions']==s['keyed_sessions'],'edge partition')
    require(s['repeated_start_same_timestamp']<=s['repeated_starts'],'repeated start bounds')
    require(all_rows['usable_id_purchase_events']<=all_rows['raw_purchase_events'],'purchase identifier bounds')
    require(sum(x['purchase_events'] for x in rows)>=all_rows['raw_purchase_events'],'raw purchase coverage')
    ordering={x['event_name']:x for x in r['ordering_field_coverage']}
    for event,key in [('view_item','view_events'),('add_to_cart','cart_events'),('begin_checkout','checkout_events'),('purchase','purchase_events')]:
        require(sum(x[key] for x in rows)>=ordering[event]['events'],'daily/keyed '+event)
        require(all(0<=ordering[event][col]<=ordering[event]['events'] for col in
                    ['bundle_populated','previous_populated','previous_positive','previous_not_before_current','offset_populated','offset_nonzero']), 'ordering field bounds '+event)
    require(ordering['purchase']['events']==all_rows['raw_purchase_events'],'ordering purchase partition')
    for scope,x in scopes.items():
        require(0<=x['strict_raw_purchase_sessions']<=x['strict_checkout_sessions']<=x['strict_cart_sessions']<=x['view_sessions']<=x['sessions'],'strict chain '+scope)
        require(0<=x['tied_raw_purchase_sessions']<=x['tied_checkout_sessions']<=x['tied_cart_sessions']<=x['view_sessions'],'tied chain '+scope)
        require(all(x[a]<=x[b] for a,b in [('strict_cart_sessions','tied_cart_sessions'),('strict_checkout_sessions','tied_checkout_sessions'),('strict_raw_purchase_sessions','tied_raw_purchase_sessions')]),'strict/tied sensitivity '+scope)
        require(x['tied_raw_purchase_sessions']<=x['unordered_all_steps']<=min(x['view_sessions'],x['cart_sessions'],x['checkout_sessions'],x['raw_purchase_sessions']),'membership bounds '+scope)
        require(x['raw_purchase_sessions']<=x['raw_purchase_events']<=x['events'],'purchase grain '+scope)
    for child,parent in [('all_keyed_interior','all_keyed'),('one_start','all_keyed'),('anchored_candidate','one_start'),('anchored_candidate_interior','anchored_candidate'),('anchored_candidate_interior_single_date','anchored_candidate_interior')]:
        require(all(v<=scopes[parent][k] for k,v in scopes[child].items() if k!='scope'),'scope nesting '+child)
    tie=r['tie_checks']
    require(all(0<=v<=tie['mixed_step_timestamp_groups'] for k,v in tie.items() if k!='mixed_step_timestamp_groups'),'tie field bounds')
    require(all(isinstance(v,int) and not isinstance(v,bool) and v>=0 for section in [p]+list(scopes.values()) for k,v in section.items() if k!='scope'),'nonnegative integer counts')
    if expected:
        require(r['fixture_case_failures']==expected['fixture_case_failures']==0,'per-journey fixture assertions')
        for section in ['population','session_checks']:
            for k,v in expected[section].items(): require(r[section][k]==v,'fixture '+k)
        for name,values in expected['scopes'].items():
            x=scopes[name]
            require(tuple(x[k] for k in ['sessions','events','strict_raw_purchase_sessions','tied_raw_purchase_sessions'])==tuple(values),'fixture scope '+name)
    return passed


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('result',type=Path)
    parser.add_argument('--expected',type=Path)
    args=parser.parse_args()
    checks=check(json.loads(args.result.read_text()),json.loads(args.expected.read_text()) if args.expected else None)
    print(f'{len(checks)} tracking/timing checks passed.')
