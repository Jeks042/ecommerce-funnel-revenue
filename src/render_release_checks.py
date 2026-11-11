"""Render read-only release checks; no credentials, DDL or automatic execution."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
from render_marts import ROOT,model_queries


def render(project,dataset,output):
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]',project) or not re.fullmatch(r'ecommerce_v1_[A-Za-z0-9_]+',dataset):
        raise ValueError('Use the existing dedicated contract-v1 warehouse namespace')
    output=Path(output).resolve()
    if not output.is_relative_to((ROOT/'private').resolve()):raise ValueError('Keep rendered configuration in private/')
    output.mkdir(parents=True,exist_ok=True);target=project+'.'+dataset;packet={}
    for i,(name,sql) in enumerate(model_queries().items(),1):
        query="SELECT TO_JSON_STRING(STRUCT('"+name+"' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum)) AS audit_json FROM (\n"+sql.replace('{{dataset}}',target)+") t;\n"
        packet[f'{i:02d}_{name}']=query
    packet['09_mart_validation']=(ROOT/'sql/marts/validate.sql').read_text(encoding='utf-8').replace('{{dataset}}',target)
    packet['10_inventory']=f"""SELECT TO_JSON_STRING(STRUCT(
 ARRAY(SELECT AS STRUCT table_name,table_type FROM `{target}.INFORMATION_SCHEMA.TABLES` ORDER BY table_name) AS tables,
 ARRAY(SELECT AS STRUCT table_name,option_name,option_value FROM `{target}.INFORMATION_SCHEMA.TABLE_OPTIONS` WHERE option_name='expiration_timestamp' ORDER BY table_name) AS expiration,
 (SELECT COUNTIF(is_partitioning_column='YES') FROM `{target}.INFORMATION_SCHEMA.COLUMNS`) AS partition_columns
)) AS audit_json;
"""
    packet['11_source_coverage']=(ROOT/'sql/06_tracking_timing_sensitivity.sql').read_text(encoding='utf-8')
    packet['12_funnel_profile']='-- Release reproduction v1: recheck the accepted journey totals.\n'+(ROOT/'sql/funnel/01_recorded_progression.sql').read_text(encoding='utf-8').replace('{{dataset}}',target)
    packet['13_reverse_funnel']='-- Release reproduction v1: recheck the accepted reverse calculation.\n'+(ROOT/'sql/funnel/02_independent_reverse_check.sql').read_text(encoding='utf-8').replace('{{dataset}}',target)
    result={}
    for name,query in packet.items():
        assert '{{dataset}}' not in query
        assert not re.search(r'\b(CREATE|INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|EXPORT)\b',re.sub(r'--[^\n]*','',query),re.I)
        (output/(name+'.sql')).write_text(query,encoding='utf-8',newline='\n')
        result[name]={'sql':query,'sha256':hashlib.sha256(query.encode()).hexdigest()}
    (output/'packet.html').write_text('<!doctype html><h1>Read-only release checks</h1><pre id="sql-packet">'+html.escape(json.dumps(result))+'</pre>',encoding='utf-8',newline='\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--dataset',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(f'Rendered {len(render(a.project,a.dataset,a.output))} read-only release statements; nothing executed.')
