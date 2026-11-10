"""Trace report figures and recommendations to reviewed, versioned evidence."""
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/plotting'))
from report_data import build


def check():
    def read(name):return json.loads((ROOT/'reports/evidence'/name).read_text(encoding='utf-8'))
    points=build();saved=read('report-plot-data-20261110.json')
    assert points==saved,'Report chart data does not reproduce'
    tracking=read('tracking-timing-receipt-20261106.json')
    run=next(r for r in tracking['runs'] if r['kind']=='source_tracking')
    assert hashlib.sha256((ROOT/'reports/evidence/tracking-timing-20261106.json').read_bytes()).hexdigest()==run['output_sha256']
    assert hashlib.sha256((ROOT/run['canonical_sql_file']).read_bytes()).hexdigest()==run['canonical_sql_sha256']
    summary=read('tracking-review-summary-20261106.json')
    assert saved['coverage']['zero_cart_dates']==summary['days_without_cart_events']
    assert len(saved['coverage']['zero_cart_dates'])==18
    for d in saved['coverage']['daily']:
        if d['date'].replace('-','') in saved['coverage']['zero_cart_dates']:
            assert d['checkout_events']>0 and d['purchase_events']>0
    receipt=read('report-receipt-20261110.json');checks=0
    for group in ['input_sha256','code_sha256','document_sha256','asset_sha256','output_sha256']:
        for path,expected in receipt[group].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Stale report evidence: '+path
            checks+=1
    for name in ['reports/commercial_report.md','reports/decision_memo.md']:
        text=(ROOT/name).read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if link.startswith(('http:','https:','#')):continue
            target=(ROOT/name).parent/link.split('#',1)[0]
            assert target.is_file(),'Broken report link '+link
    assert receipt['historical_contract_version']==1 and not receipt['live_experiment_started']
    return {'report_hash_checks':checks,'report_figures':4,'figure_files':8,'coverage_dates':92,'scenario_cells':15,'report_chart_data_reproduced':True}


if __name__=='__main__':print(check())
