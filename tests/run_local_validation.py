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
    out=ROOT/'reports/validation';out.mkdir(exist_ok=True)
    report={'status':'passed','fixture_integrity_checks':len(fixture),'source_and_contract_checks':len(source),
            'earlier_baseline_checks':len(baseline),'reproduction_and_inventory_checks':reproduced,'native_execution':'Saved reviewed evidence only; CI has no warehouse credentials.',
            'sql_template_sha256':manifest}
    (out/'ci-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Credential-free evidence validation passed; wrote reports/validation/ci-validation.json.')


if __name__=='__main__':
    main()
