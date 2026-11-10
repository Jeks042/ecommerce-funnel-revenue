"""Conditional visit scenarios and prospective, visitor-level power illustrations."""
from decimal import Decimal,localcontext
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

ROOT=Path(__file__).resolve().parents[1]
NORMAL=NormalDist()


def planning_power(baseline,effect,n_per_arm,alpha=.05):
    """Two independent proportions: pooled null and unpooled alternative variance."""
    if not all(math.isfinite(x) for x in [baseline,effect,alpha]):
        raise ValueError('Finite probabilities required')
    if not 0<baseline<1 or not 0<baseline+effect<1 or not 0<alpha<1:
        raise ValueError('Probabilities must be interior to (0,1)')
    if type(n_per_arm) is not int or n_per_arm<1:raise ValueError('Positive integer sample per arm required')
    p1=baseline+effect;pooled=(baseline+p1)/2
    null_sd=math.sqrt(2*pooled*(1-pooled))
    alternative_sd=math.sqrt(baseline*(1-baseline)+p1*(1-p1))
    cutoff=NORMAL.inv_cdf(1-alpha/2)*null_sd
    signal=effect*math.sqrt(n_per_arm)
    # The two tails both contribute to rejection in the proposed two-sided test.
    return NORMAL.cdf((signal-cutoff)/alternative_sd)+NORMAL.cdf((-signal-cutoff)/alternative_sd)


def sample_size(baseline,effect,power=.8,alpha=.05):
    if not math.isfinite(power) or not alpha<power<1 or effect==0:
        raise ValueError('Nonzero effect and target power above alpha required')
    lo,hi=0,16
    while planning_power(baseline,effect,hi,alpha)<power:
        hi*=2
        if hi>100_000_000:raise ValueError('Planning grid exceeds supported sample size')
    while hi-lo>1:
        middle=(hi+lo)//2
        if planning_power(baseline,effect,middle,alpha)>=power:hi=middle
        else:lo=middle
    return hi


def visit_scenario(entries,carts,completions,absolute_change,multiplier):
    if not all(type(x) is int for x in [entries,carts,completions]) or not 0<=completions<=carts<=entries or entries==0 or carts==0:
        raise ValueError('Positive observed denominators and nested integer counts required')
    delta,m=Decimal(str(absolute_change)),Decimal(str(multiplier))
    if not delta.is_finite() or not m.is_finite() or not 0<=m<=1:
        raise ValueError('Finite change and multiplier in [0,1] required')
    with localcontext() as ctx:
        ctx.prec=40
        new_rate=Decimal(carts)/entries+delta
        if not 0<=new_rate<=1:raise ValueError('Scenario cart rate falls outside [0,1]')
        extra_carts=Decimal(entries)*delta
        extra_completions=extra_carts*Decimal(completions)/carts*m
        if not 0<=Decimal(completions)+extra_completions<=Decimal(carts)+extra_carts:
            raise ValueError('Hypothetical completion/cart counts are not nested')
        def display(x):return str((x if x else Decimal(0)).quantize(Decimal('0.000001')))
        return {'assumed_absolute_cart_rate_change':str(delta),
            'assumed_marginal_downstream_multiplier':str(m),
            'hypothetical_cart_rate':display(new_rate),
            'additional_cart_visit_equivalents':display(extra_carts),
            'additional_qualified_completion_visit_equivalents':display(extra_completions),
            'hypothetical_total_completions':display(Decimal(completions)+extra_completions)}


def assess(summary,assumptions):
    if assumptions['version']!=1 or summary['contract_version']!=1:
        raise ValueError('Only accepted version 1 inputs are supported')
    p=summary['scopes']['primary']
    observed={k:p[k] for k in ['sessions','entry_sessions','strict_cart_sessions','strict_checkout_sessions',
        'strict_candidate_sessions','candidate_purchase_sessions','candidate_transactions','unresolved_sessions']}
    scenarios=[]
    for case in assumptions['cart_rate_changes']:
        for m in assumptions['marginal_downstream_multipliers']:
            scenarios.append({'name':case['name'],**visit_scenario(p['entry_sessions'],p['strict_cart_sessions'],
                p['strict_candidate_sessions'],case['absolute_change'],m)})
    settings=assumptions['power_planning'];grid=[]
    for p0 in settings['baseline_probabilities_assumed']:
        for effect in settings['absolute_effects_assumed']:
            n=sample_size(p0,effect,settings['target_power'],settings['alpha_two_sided'])
            grid.append({'assumed_visitor_baseline':p0,'assumed_absolute_effect':effect,
                'visitors_per_arm':n,'total_visitors':2*n,
                'normal_approximation_power':round(planning_power(p0,effect,n,settings['alpha_two_sided']),12),
                'previous_integer_power':round(planning_power(p0,effect,n-1,settings['alpha_two_sided']),12)})
    return {'version':1,'observed_period':summary['period'],'observed_visit_counts':observed,
        'scenarios':scenarios,'visitor_power_illustrations':grid,
        'interpretation':'Conditional arithmetic, not forecast validation or a measured treatment effect. Visit scenarios and visitor power are different units.',
        'financial_return':None,'live_experiment_started':False,'launch_ready':False,'calendar_duration':None}


def generate():
    paths=['reports/evidence/funnel-analysis-20261110.json','reports/evidence/scenario-assumptions-v1.json']
    values=[json.loads((ROOT/p).read_text(encoding='utf-8')) for p in paths]
    output=assess(*values)
    output['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    (ROOT/'reports/evidence/opportunity-analysis-20261110.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Generated 15 conditional visit scenarios and 9 separate visitor-level power illustrations.')
    return output


if __name__=='__main__':generate()
