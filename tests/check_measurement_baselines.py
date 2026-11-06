"""Compare new linkage against independently saved purchase and tracking audits."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def check():
    def read(name):return json.loads((ROOT/'reports/evidence'/name).read_text())
    gate=read('measurement-gate-20261106.json');purchase=read('purchase-detail-diagnostics-20261106.json');tracking=read('tracking-timing-20261106.json')
    checks=[]
    def require(test,label):
        if not test:raise AssertionError(label)
        checks.append(label)
    g=purchase['group_checks'];c=gate['candidates'];link=gate['linkage']
    for new,old in [('candidate_transactions','conservative_id_candidates'),('candidate_events','conservative_candidate_events'),
                    ('native_complete_transactions','native_complete_candidates'),('agreeing_transactions','native_item_agree_candidates'),
                    ('agreeing_recorded_value','diagnostic_agreeing_native_amount')]:
        require(c[new]==g[old],'purchase baseline '+new)
    require(link['keyed_sessions']==tracking['session_checks']['keyed_sessions'],'session population')
    require(link['keyed_events']==tracking['population']['events'],'event population')
    scopes={s['scope']:s for s in tracking['scope_sensitivity']}
    for gate_scope,old_scope in [('all_keyed','all_keyed'),('anchored_interior','anchored_candidate_interior'),('anchored_interior_single_date','anchored_candidate_interior_single_date')]:
        rows=[s for s in gate['scopes'] if s['scope']==gate_scope]
        for k in ['sessions','entry_sessions','strict_cart_sessions','strict_checkout_sessions','raw_purchase_events']:
            prior='view_sessions' if k=='entry_sessions' else k
            require(sum(s[k] for s in rows)==scopes[old_scope][prior],'scope baseline '+gate_scope+'/'+k)
    daily={}
    for row in tracking['daily_device_coverage']:
        key=(row['source_suffix'],row['device']);daily[key]=row
    for row in gate['purchase_coverage']:
        key=(row['source_suffix'],row['device'])
        require(row['raw_purchase_events']==daily[key]['purchase_events'],'date/device purchase coverage')
    require(gate['long_span_review']['sessions']==tracking['session_checks']['observed_spans_over_24_hours'],'long-span groups')
    return checks


if __name__=='__main__':
    print(f'{len(check())} comparisons with previous evidence passed.')
