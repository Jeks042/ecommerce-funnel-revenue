"""Descriptive journey analysis from reviewed, identifier-free BigQuery aggregates."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RATES={
    'view_to_cart':('strict_cart_sessions','entry_sessions'),
    'cart_to_checkout':('strict_checkout_sessions','strict_cart_sessions'),
    'checkout_to_purchase':('strict_candidate_sessions','strict_checkout_sessions'),
    'view_to_purchase':('strict_candidate_sessions','entry_sessions'),
}
METRICS=['sessions','entry_sessions','strict_cart_sessions','strict_checkout_sessions',
    'strict_candidate_sessions','tied_cart_sessions','tied_checkout_sessions','tied_candidate_sessions',
    'strict_raw_purchase_sessions','tied_raw_purchase_sessions','unordered_cart_sessions',
    'unordered_checkout_sessions','unordered_candidate_sessions','candidate_purchase_sessions',
    'candidate_transactions','raw_purchase_events','missing_id_events','rejected_id_events',
    'unresolved_sessions','entry_unresolved_sessions','checkout_unresolved_sessions','mixed_outcome_sessions',
    'raw_only_completion_sessions','raw_only_with_unresolved_ids_sessions']


def total(rows):
    return {k:sum(int(r[k]) for r in rows) for k in METRICS}


def admitted(success,denominator):
    return denominator>=500 and success>=30 and denominator-success>=30


def rate(success,denominator):
    if not 0<=success<=denominator:raise ValueError('Non-nested numerator/denominator')
    return success/denominator if denominator else None


def comparable(a,b,numerator,denominator):
    """Both groups use pooled daily denominator weights on common observed days."""
    def index(rows):
        out={r['visit_date']:r for r in rows}
        if len(out)!=len(rows):raise ValueError('Duplicate daily group')
        return out
    ai,bi=index(a),index(b)
    days=sorted(d for d in ai.keys()&bi.keys() if ai[d][denominator]>0 and bi[d][denominator]>0)
    counts=[]
    for rows in (a,b):
        counts.append({'successes':sum(r[numerator] for r in rows),
                       'denominator':sum(r[denominator] for r in rows)})
    retained=[]
    for ix in (ai,bi):
        retained.append({'successes':sum(ix[d][numerator] for d in days),
                         'denominator':sum(ix[d][denominator] for d in days)})
    result={'all_counts':counts,'common_counts':retained,'common_dates':days,
            'crude_rates':None,'standardized_rates':None,'standardized_gap_pp':None,
            'crude_gap_pp':None,'leave_one_day_out_gap_pp':None,'admissible_omissions':0}
    if all(admitted(x['successes'],x['denominator']) for x in counts):
        result['crude_rates']=[rate(x['successes'],x['denominator']) for x in counts]
        result['crude_gap_pp']=100*(result['crude_rates'][1]-result['crude_rates'][0])
    def weighted(selected):
        denom=sum(ai[d][denominator]+bi[d][denominator] for d in selected)
        return [sum((ai[d][denominator]+bi[d][denominator])/denom*
                    rate(ix[d][numerator],ix[d][denominator]) for d in selected) for ix in (ai,bi)]
    if days and all(admitted(x['successes'],x['denominator']) for x in retained):
        result['standardized_rates']=weighted(days)
        result['standardized_gap_pp']=100*(result['standardized_rates'][1]-result['standardized_rates'][0])
        gaps=[]
        for omitted in days:
            selected=[d for d in days if d!=omitted]
            if selected and all(admitted(sum(ix[d][numerator] for d in selected),sum(ix[d][denominator] for d in selected)) for ix in (ai,bi)):
                r=weighted(selected);gaps.append(100*(r[1]-r[0]))
        result['admissible_omissions']=len(gaps)
        if gaps:result['leave_one_day_out_gap_pp']=[min(gaps),max(gaps)]
    return result


def analyse(data):
    rows=data['daily_device']
    scopes={s:total([r for r in rows if r['scope']==s]) for s in ['all_keyed','anchored_interior','primary']}
    primary=[r for r in rows if r['scope']=='primary']
    devices={str(d):total([r for r in primary if r['device']==d]) for d in sorted({r['device'] for r in primary},key=str)}
    # Select comparison by entry volume, independently of rates.
    selected=sorted(devices,key=lambda d:(-devices[d]['entry_sessions'],d))[:2]
    comparisons={k:comparable([r for r in primary if str(r['device'])==selected[0]],
                             [r for r in primary if str(r['device'])==selected[1]],n,d)
                 for k,(n,d) in RATES.items()} if len(selected)==2 else {}
    contexts=data['admitted_contexts']
    context_order=sorted(contexts,key=lambda c:-next(r['entry_sessions'] for r in data['context_summary']
        if (r['first_user_source'],r['first_user_medium'])==(c['first_user_source'],c['first_user_medium'])))
    context_comparisons={}
    if len(context_order)==2:
        cr=[[r for r in data['daily_context'] if all(r[k]==c[k] for k in ['first_user_source','first_user_medium'])] for c in context_order]
        context_comparisons={k:comparable(cr[0],cr[1],n,d) for k,(n,d) in RATES.items()}
    return {'period':'December 2020','contract_version':1,'scopes':scopes,'devices':devices,
        'device_order':selected,'device_comparisons':comparisons,
        'context_order':context_order,'context_comparisons':context_comparisons,
        'context_coverage':{'interpretable_sessions':sum(r['sessions'] for r in data['context_summary'] if r['interpretable_context']),
                            'sessions':scopes['primary']['sessions']},
        'uncertainty':'Definition, population and leave-one-date-out sensitivities; no confidence interval or significance claim.'}


def blueprint(summary):
    p=summary['scopes']['primary']
    keys=['entry_sessions','strict_cart_sessions','strict_checkout_sessions','strict_candidate_sessions']
    return {'journey_counts':[p[k] for k in keys],
        'device_order':summary['device_order'],'device_comparisons':summary['device_comparisons'],
        'period':summary['period'],'contract_version':summary['contract_version']}


if __name__=='__main__':
    data=json.loads((ROOT/'reports/evidence/funnel-20261110.json').read_text())
    output=analyse(data)
    (ROOT/'reports/evidence/funnel-analysis-20261110.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print('Reproduced descriptive analysis from reviewed daily aggregates.')
