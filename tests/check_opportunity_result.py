"""Reproduce prospective planning arithmetic without statistical dependencies."""
import hashlib
import json
from pathlib import Path
import sys
from decimal import Decimal
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from assess_opportunity import assess
ROOT=Path(__file__).resolve().parents[1]


def check():
    def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
    saved=read('reports/evidence/opportunity-analysis-20261110.json')
    computed=assess(read('reports/evidence/funnel-analysis-20261110.json'),read('reports/evidence/scenario-assumptions-v1.json'))
    for key in computed:
        assert saved[key]==computed[key],'Scenario/power output does not reproduce: '+key
    p=saved['observed_visit_counts'];checks=0
    # Recalculate through the two separate downstream stages with rational arithmetic.
    for r in saved['scenarios']:
        carts=Fraction(p['entry_sessions'])*Fraction(r['assumed_absolute_cart_rate_change'])
        completed=carts*Fraction(p['strict_checkout_sessions'],p['strict_cart_sessions'])*Fraction(p['strict_candidate_sessions'],p['strict_checkout_sessions'])*Fraction(r['assumed_marginal_downstream_multiplier'])
        def within_rounding(text,rational):
            return abs(Fraction(Decimal(text))-rational)<=Fraction(1,2_000_000)
        assert within_rounding(r['additional_cart_visit_equivalents'],carts)
        assert within_rounding(r['additional_qualified_completion_visit_equivalents'],completed)
        checks+=2
    reference=read('reports/evidence/power-reference-20261110.json')
    settings=read('reports/evidence/scenario-assumptions-v1.json')['power_planning']
    assert reference['alpha_two_sided']==settings['alpha_two_sided']
    assert reference['allocation']==settings['allocation']=='1:1'
    assert len(reference['cases'])==len(saved['visitor_power_illustrations'])
    for r,g in zip(reference['cases'],saved['visitor_power_illustrations']):
        assert (r['baseline'],r['effect'],r['visitors_per_arm'])==(g['assumed_visitor_baseline'],g['assumed_absolute_effect'],g['visitors_per_arm'])
        assert r['previous_integer']==g['visitors_per_arm']-1
        assert r['power']>=settings['target_power']>r['previous_power']
        assert abs(r['power']-g['normal_approximation_power'])<=1e-12
        assert abs(r['previous_power']-g['previous_integer_power'])<=1e-12
    receipt=read('reports/evidence/opportunity-receipt-20261110.json')
    for group in ['inputs_sha256','code_sha256','outputs_sha256']:
        for path,expected in receipt[group].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Stale planning evidence: '+path
            checks+=1
    for path,expected in saved['input_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Scenario input changed: '+path
        checks+=1
    assert receipt['historical_measurement_contract_version']==1
    assert saved['financial_return'] is None and not saved['launch_ready'] and not saved['live_experiment_started']
    return {'planning_scenarios_reproduced':len(saved['scenarios']),'power_illustrations_reproduced':len(saved['visitor_power_illustrations']),
        'planning_integrity_checks':checks,'statistical_reference_power_evaluations_reconciled':18,
        'prospective_design_version':1,'live_experiment_started':False}


if __name__=='__main__':print(check())
