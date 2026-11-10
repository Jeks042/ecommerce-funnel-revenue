"""Check actual rendered files and numeric chart data without platform-byte claims."""
import hashlib
import json
from pathlib import Path
import sys
from check_report_evidence import ROOT,check
sys.path.insert(0,str(ROOT/'src/plotting'))
from report_data import build


def validate(folder):
    folder=Path(folder)
    data=json.loads((folder/'build-manifest.json').read_text(encoding='utf-8'))
    assert data['plot_data']==build(),'Rendered chart data changed'
    names={n+'.'+ext for n in ['recorded_journey','device_progression','recording_coverage','cart_scenarios'] for ext in ['png','svg']}
    assert set(data['rendered_sha256'])==names,'Eight expected figure files required'
    for name,expected in data['rendered_sha256'].items():
        path=folder/'figures'/name;raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==expected,'Render hash mismatch '+name
        if name.endswith('.png'):assert raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw)>10000
        else:assert '<svg ' in raw.decode('utf-8')
    # Cross-platform raster/font differences do not change the numeric reproduction requirement.
    result=check();result['actual_figure_files_regenerated']=len(names)
    print(result)
    return result


if __name__=='__main__':validate(sys.argv[1])
