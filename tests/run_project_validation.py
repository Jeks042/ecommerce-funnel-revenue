"""Extend accepted historical validation without rewriting its execution receipt."""
import json
from pathlib import Path
import subprocess
import sys
from check_opportunity_result import check
ROOT=Path(__file__).resolve().parents[1]


if __name__=='__main__':
    subprocess.run([sys.executable,'tests/run_local_validation.py'],cwd=ROOT,check=True)
    planning=check()
    path=ROOT/'reports/validation/ci-validation.json'
    result=json.loads(path.read_text(encoding='utf-8'));result.update(planning)
    path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prospective scenarios and planning evidence validated; retained with historical checks.')
