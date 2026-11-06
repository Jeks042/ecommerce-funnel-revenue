"""Build a reproducible coverage review from approved warehouse aggregates."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


COUNTS=('events','page_view_events','start_events','view_events','cart_events',
        'checkout_events','purchase_events','usable_id_purchase_events')


def summarize(r):
    daily=defaultdict(lambda:{c:0 for c in COUNTS})
    months=defaultdict(lambda:{c:0 for c in COUNTS})
    devices=defaultdict(int)
    for row in r['daily_device_coverage']:
        for c in COUNTS:
            daily[row['source_suffix']][c]+=row[c]
            months[row['source_suffix'][:6]][c]+=row[c]
        devices[row['device']]+=row['events']
    scopes={x['scope']:x for x in r['scope_sensitivity']}
    without_cart=[d for d,x in sorted(daily.items()) if x['cart_events']==0]
    return {
        'grain':'Coverage counts are source events; scope counts are composite user/session groups. Purchase events are not orders.',
        'days_without_cart_events':without_cart,
        'days_without_cart_events_count':len(without_cart),
        'without_cart_days_with_checkout_and_purchase':sum(daily[d]['checkout_events']>0 and daily[d]['purchase_events']>0 for d in without_cart),
        'without_cart_day_totals':{c:sum(daily[d][c] for d in without_cart) for c in COUNTS},
        'days_checkout_events_exceed_cart_events':[d for d,x in sorted(daily.items()) if x['checkout_events']>x['cart_events']],
        'days_without_usable_purchase_ids':[d for d,x in sorted(daily.items()) if x['purchase_events']>0 and x['usable_id_purchase_events']==0],
        'monthly_event_coverage':[dict(source_month=m,**counts) for m,counts in sorted(months.items())],
        'device_event_coverage':[dict(device=d,events=v) for d,v in sorted(devices.items())],
        'scope_waterfall':[
            dict(scope='all_keyed',sessions=scopes['all_keyed']['sessions'],excluded_since_previous=0),
            dict(scope='one_start',sessions=scopes['one_start']['sessions'],excluded_since_previous=scopes['all_keyed']['sessions']-scopes['one_start']['sessions']),
            dict(scope='anchored_candidate',sessions=scopes['anchored_candidate']['sessions'],excluded_since_previous=scopes['one_start']['sessions']-scopes['anchored_candidate']['sessions']),
            dict(scope='anchored_candidate_interior',sessions=scopes['anchored_candidate_interior']['sessions'],excluded_since_previous=scopes['anchored_candidate']['sessions']-scopes['anchored_candidate_interior']['sessions'])],
        'additional_single_date_exclusion':scopes['anchored_candidate_interior']['sessions']-scopes['anchored_candidate_interior_single_date']['sessions'],
        'all_keyed_raw_purchase_chain_sensitivity':{
            'view_session_denominator':scopes['all_keyed']['view_sessions'],
            'strict_completion_sessions':scopes['all_keyed']['strict_raw_purchase_sessions'],
            'ties_allowed_completion_sessions':scopes['all_keyed']['tied_raw_purchase_sessions'],
            'additional_completion_sessions':scopes['all_keyed']['tied_raw_purchase_sessions']-scopes['all_keyed']['strict_raw_purchase_sessions']},
        'interpretation':{
            'zero_cart_days_establish_cause':False,
            'checkout_above_cart_proves_tracking_failure':False,
            'bundle_id_resolves_within_bundle_order':False,
            'session_id_used_as_start_timestamp':False,
            'raw_purchase_events_are_orders':False,
            'metric_contract_frozen':False}
    }


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    evidence=args.input.read_bytes()
    result=summarize(json.loads(evidence))
    result['input_sha256']=hashlib.sha256(evidence).hexdigest()
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Built aggregate coverage review; no raw records or credentials required.')
