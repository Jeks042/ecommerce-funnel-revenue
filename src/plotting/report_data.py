"""Chart data at explicit grains; no plotting dependencies or raw identifiers."""
from collections import defaultdict
from datetime import date,timedelta
from decimal import Decimal,ROUND_HALF_UP
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from analyse_funnel import blueprint


def coverage_data(tracking):
    rows=tracking['daily_device_coverage']
    days=[(date(2020,11,1)+timedelta(days=i)).strftime('%Y%m%d') for i in range(92)]
    expected={(d,v) for d in days for v in ['desktop','mobile','tablet']}
    keys=[(r['source_suffix'],r['device']) for r in rows]
    if len(keys)!=len(set(keys)) or set(keys)!=expected:
        raise ValueError('Daily recording evidence must cover all 92 dates and three devices exactly once')
    counts=defaultdict(lambda:{k:0 for k in ['events','cart_events','checkout_events','purchase_events']})
    for r in rows:
        for k in counts[r['source_suffix']]:
            if type(r[k]) is not int or r[k]<0:raise ValueError('Missing or invalid event count')
            counts[r['source_suffix']][k]+=r[k]
    if sum(r['events'] for r in counts.values())!=tracking['population']['events']:
        raise ValueError('Daily event total does not reconcile')
    return {'grain':'All source events by UTC source date; not visits, orders or conversion rates',
        'daily':[{'date':date.fromisoformat(d[:4]+'-'+d[4:6]+'-'+d[6:]).isoformat(),**counts[d]} for d in days],
        'zero_cart_dates':[d for d in days if counts[d]['cart_events']==0],
        'primary_period':['2020-12-01','2020-12-31']}


def scenario_data(opportunity):
    rows=opportunity['scenarios'];names=['downside','no_change','low','base','high'];multipliers=['0','0.5','1']
    index={(r['name'],r['assumed_marginal_downstream_multiplier']):r for r in rows}
    if len(index)!=len(rows) or set(index)!={(n,m) for n in names for m in multipliers}:
        raise ValueError('All 15 distinct scenario cells required')
    out=[]
    def display(value):return str(Decimal(value).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
    for n in names:
        row=[index[n,m] for m in multipliers]
        if len({r['additional_cart_visit_equivalents'] for r in row})!=1 or len({r['assumed_absolute_cart_rate_change'] for r in row})!=1:
            raise ValueError('Cart assumption changes across downstream cases')
        out.append({'name':n,'absolute_cart_rate_change':row[0]['assumed_absolute_cart_rate_change'],
            'additional_carts':row[0]['additional_cart_visit_equivalents'],
            'additional_carts_display':display(row[0]['additional_cart_visit_equivalents']),
            'completion_values':[r['additional_qualified_completion_visit_equivalents'] for r in row],
            'completion_display':[display(r['additional_qualified_completion_visit_equivalents']) for r in row]})
    return {'grain':'Hypothetical visit equivalents; not sales or a prediction interval',
        'reference_entries':opportunity['observed_visit_counts']['entry_sessions'],
        'downstream_multipliers':multipliers,'rows':out}


def build():
    def read(name):return json.loads((ROOT/'reports/evidence'/name).read_text(encoding='utf-8'))
    return {'version':1,'coverage':coverage_data(read('tracking-timing-20261106.json')),
        'journey_and_devices':blueprint(read('funnel-analysis-20261110.json')),
        'scenarios':scenario_data(read('opportunity-analysis-20261110.json'))}
