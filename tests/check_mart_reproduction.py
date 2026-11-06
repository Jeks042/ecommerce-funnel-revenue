"""Check independently recomputed model contents and warehouse inventory."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def check():
    read=lambda n:json.loads((ROOT/'reports/evidence'/n).read_text())
    source=read('marts-20261106.json');reproduced=read('marts-reproduction-20261106.json');inventory=read('marts-inventory-20261106.json')
    original={x['model']:x for x in source['fingerprints']}
    repeat={x['model']:x for x in reproduced['models']}
    assert set(original)==set(repeat) and len(reproduced['models'])==8,'all eight recomputations required'
    for model,x in original.items():
        # Console JSON encodes INT64 cells as strings; counts remain exact integers.
        assert str(x['row_count'])==str(repeat[model]['row_count']),model+' row count'
        assert x['content_checksum']==repeat[model]['content_checksum'],model+' content checksum'
    assert {x['table_name'] for x in inventory['tables']}==set(original),'eight physical objects'
    assert all(x['table_type']=='BASE TABLE' for x in inventory['tables']),'physical tables required'
    assert inventory['partition_columns']==0,'historical date partitions must be absent in Sandbox'
    assert {x['table_name'] for x in inventory['expiration']}==set(original),'expiration for every table'
    return 21


if __name__=='__main__':
    print(f'{check()} reproduction and inventory checks passed.')
