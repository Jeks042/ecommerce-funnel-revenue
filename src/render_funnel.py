"""Render read-only funnel SQL and bounded native edge-case checks."""
import hashlib
import html
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]


def render(destination):
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]\.ecommerce_v1_[A-Za-z0-9_]+',destination):
        raise ValueError('Use the existing dedicated contract-v1 dataset.')
    sys.path.insert(0,str(ROOT/'tests'))
    from prepare_mart_fixture import prepare_fixture
    base=prepare_fixture().split('WITH gate_scopes AS (',1)[0]
    assert base.count('CREATE TEMP TABLE')==9 and 'bigquery-public-data' not in base
    out=ROOT/'private/funnel_20261110';out.mkdir(parents=True,exist_ok=True)
    packet={}
    for path in sorted((ROOT/'sql/funnel').glob('*.sql')):
        template=path.read_text(encoding='utf-8')
        source=template.replace('{{dataset}}',destination)
        fixture=template
        for name in ['stg_events','fact_transactions','fact_visits']:
            fixture=fixture.replace('`{{dataset}}.'+name+'`',name)
        fixture=base+fixture
        assert '{{dataset}}' not in source+fixture and 'bigquery-public-data' not in fixture
        for label,query in [(path.stem,source),(path.stem+'_fixture',fixture)]:
            (out/(label+'.sql')).write_text(query,encoding='utf-8',newline='\n')
            packet[label]={'sql':query,'sha256':hashlib.sha256(query.encode()).hexdigest()}
    transfer=ROOT/'private/funnel_transfer';transfer.mkdir(exist_ok=True)
    (transfer/'packet.html').write_text('<!doctype html><h1>SQL review packet</h1><pre id="sql-packet">'+html.escape(json.dumps(packet))+'</pre>',encoding='utf-8',newline='\n')
    return packet


if __name__=='__main__':
    config=json.loads((ROOT/'private/marts_20261106/manifest.json').read_text())
    assert config['contract_version']==1 and config['analysis_month']=='202012'
    packet=render(config['destination'])
    print('Rendered four private read-only/temporary-table scripts. Nothing executed.')
