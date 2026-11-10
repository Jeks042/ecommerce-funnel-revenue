"""Credential-free validation and a small public CI evidence artifact."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from check_mart_result import check
from check_measurement_baselines import check as baseline_check
from check_mart_reproduction import check as reproduction_check
from prepare_mart_fixture import prepare_fixture
from check_funnel_result import check as funnel_check
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyse_funnel import analyse,blueprint

ROOT=Path(__file__).resolve().parents[1]


def read(name):return json.loads((ROOT/'reports/evidence'/name).read_text())


def main():
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py'],cwd=ROOT,check=True)
    prepare_fixture()
    expected=json.loads((ROOT/'private/mart_fixture_expected.json').read_text())
    fixture=check(read('marts-fixture-20261106.json'),expected=expected)
    source=check(read('marts-20261106.json'),gate=read('measurement-gate-20261106.json'))
    baseline=baseline_check()
    reproduced=reproduction_check()
    sql=list((ROOT/'sql/marts').glob('*.sql'))
    manifest={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sql)}
    receipt=read('marts-receipt-20261106.json')
    assert manifest==receipt['model_sql_sha256'],'Saved native evidence does not match the current SQL templates.'
    assert hashlib.sha256((ROOT/'src/render_marts.py').read_bytes()).hexdigest()==receipt['renderer_sha256'],'Renderer changed since native execution.'
    assert hashlib.sha256((ROOT/'private/mart_fixture_materialized.sql').read_bytes()).hexdigest()==receipt['fixture']['canonical_sql_sha256'],'Native fixture changed since execution.'
    funnel_fixture=funnel_check(read('funnel-fixture-20261110.json'),read('funnel-reverse-fixture-20261110.json'),True)
    funnel_source=funnel_check(read('funnel-20261110.json'),read('funnel-reverse-20261110.json'))
    summary=analyse(read('funnel-20261110.json'))
    assert summary==read('funnel-analysis-20261110.json'),'Funnel summary does not reproduce'
    figures=read('funnel-figures-20261110.json')
    assert blueprint(summary)==figures['plot_data'],'Chart points do not reconcile'
    for path,expected in (figures['files_sha256']|figures['source_sha256']).items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Stale chart asset or source: '+path
    fr=read('funnel-receipt-20261110.json')
    for path,expected in (fr['code_sha256']|fr['outputs_sha256']).items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Stale native funnel evidence: '+path
    from render_funnel import render as render_funnel
    rendered=render_funnel('example-project.ecommerce_v1_ci')
    for name,run in fr['runs'].items():
        if name.endswith('_fixture'):
            assert rendered[name]['sha256']==run['canonical_sql_sha256'],'Native funnel fixture changed'
    out=ROOT/'reports/validation';out.mkdir(exist_ok=True)
    report={'status':'passed','fixture_integrity_checks':len(fixture),'source_and_contract_checks':len(source),
            'earlier_baseline_checks':len(baseline),'reproduction_and_inventory_checks':reproduced,'native_execution':'Saved reviewed evidence only; CI has no warehouse credentials.',
            'sql_template_sha256':manifest}
    report.update(funnel_fixture_checks=len(funnel_fixture),funnel_source_checks=len(funnel_source),
                  funnel_analysis_reproduced=True,chart_points_reconciled=True,chart_asset_hashes_verified=True)
    (out/'ci-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Credential-free evidence validation passed; wrote reports/validation/ci-validation.json.')


if __name__=='__main__':
    main()
