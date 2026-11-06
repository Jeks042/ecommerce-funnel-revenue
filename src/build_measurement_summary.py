"""Build a reviewed scope ledger from aggregate evidence only."""
import argparse
import json
from pathlib import Path


def summarize(gate,tracking):
    keys=[k for k in gate['scopes'][0] if k not in ['scope','cohort_month','session_device']]
    def total(scope):
        rows=[s for s in gate['scopes'] if s['scope']==scope and s['cohort_month']=='202012']
        return {k:(sum(s[k] for s in rows if s[k] is not None)
                   if any(s[k] is not None for s in rows) else None) for k in keys}
    allrows=total('all_keyed');anchored=total('anchored_interior');primary=total('anchored_interior_single_date')
    daily=tracking['daily_device_coverage']
    dec=[s for s in daily if s['source_suffix'].startswith('202012')]
    dates=sorted({s['source_suffix'] for s in dec})
    zero_cart=[d for d in dates if sum(s['cart_events'] for s in dec if s['source_suffix']==d)==0]
    return {'analysis_month':'2020-12','scope':'anchored_interior_single_date',
        'source_qualification_window':['2020-11-01','2021-01-31'],
        'selection_reason':'Complete calendar month without the zero-cart dates found in November; chosen on tracking coverage, not conversion performance.',
        'coverage':{'dates':len(dates),'zero_cart_dates':zero_cart},
        'scope_ledger':[{'scope':'all_keyed','sessions':allrows['sessions'],'removed_from_parent':0},
            {'scope':'anchored_interior','sessions':anchored['sessions'],'removed_from_parent':allrows['sessions']-anchored['sessions']},
            {'scope':'anchored_interior_single_date','sessions':primary['sessions'],'removed_from_parent':anchored['sessions']-primary['sessions']}],
        'primary':primary,'cross_date_sensitivity':anchored,'all_keyed_sensitivity':allrows,
        'primary_devices':[s for s in gate['scopes'] if s['scope']=='anchored_interior_single_date' and s['cohort_month']=='202012'],
        'unsupported':['total sales revenue','gross or net revenue','average order value','revenue per session','profit','causal uplift'],
        'value_label':'Recorded purchase value (USD), item-agreeing selected subset only'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('gate',type=Path);p.add_argument('tracking',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    result=summarize(json.loads(a.gate.read_text()),json.loads(a.tracking.read_text()))
    a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Wrote aggregate-only measurement scope ledger.')
