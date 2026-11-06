"""Render fixed-contract GoogleSQL without credentials or automatic execution."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MODELS = ['stg_events', 'transaction_policy', 'fact_transactions',
          'fact_transaction_items', 'fact_visits', 'audit_event_keys',
          'audit_visit_exclusions', 'audit_purchase_coverage']
SOURCE = '`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`'


def model_queries():
    return {name: (ROOT / 'sql/marts' / (name + '.sql')).read_text(encoding='utf-8').strip().rstrip(';')
            for name in MODELS}


def render(project, dataset, output):
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]', project):
        raise ValueError('Use a valid destination project ID.')
    if not re.fullmatch(r'ecommerce_v1_[A-Za-z0-9_]+', dataset):
        raise ValueError('Use the dedicated ecommerce_v1_ namespace.')
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT/'private').resolve()):
        raise ValueError('Rendered project configuration must stay in private/.')
    output.mkdir(parents=True, exist_ok=True)
    target = project + '.' + dataset
    schema = f"CREATE SCHEMA IF NOT EXISTS `{target}` OPTIONS(location='US', default_table_expiration_days=60, description='E-commerce measurement contract v1; private warehouse tables; aggregate publication only');\n"
    files = [('00_create_dataset.sql', schema)]
    queries = model_queries()
    for index, (name, sql) in enumerate(queries.items(), 1):
        sql = sql.replace('{{dataset}}', target)
        cluster = ' CLUSTER BY user_pseudo_id,session_id' if name in ['stg_events','fact_visits','fact_transactions'] else ''
        statement = f"CREATE TABLE `{target}.{name}`{cluster}\nOPTIONS(description='Contract v1; {name}; source 20201101-20210131; no total revenue approval')\nAS\n{sql};\n"
        files.append((f'{index:02d}_{name}.sql', statement))
    checks = (ROOT/'sql/marts/validate.sql').read_text(encoding='utf-8').replace('{{dataset}}', target)
    files.append(('09_validate.sql', checks))
    inventory = f"""SELECT TO_JSON_STRING(STRUCT(
  ARRAY(SELECT AS STRUCT table_name,table_type FROM `{target}.INFORMATION_SCHEMA.TABLES` ORDER BY table_name) AS tables,
  ARRAY(SELECT AS STRUCT table_name,option_name,option_value FROM `{target}.INFORMATION_SCHEMA.TABLE_OPTIONS` WHERE option_name='expiration_timestamp' ORDER BY table_name) AS expiration,
  (SELECT COUNTIF(is_partitioning_column='YES') FROM `{target}.INFORMATION_SCHEMA.COLUMNS`) AS partition_columns
)) AS audit_json;
"""
    files.append(('10_inventory.sql', inventory))
    # Read-only model recomputation: no second copy of staged data or quota-consuming rebuild.
    for index, (name, sql) in enumerate(queries.items(), 11):
        recompute = "SELECT '"+name+"' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM (\n"+sql.replace('{{dataset}}',target)+") t;\n"
        files.append((f'{index:02d}_recompute_{name}.sql', recompute))
    manifest = {'contract_version':1,'source':SOURCE.strip('`'),
                'source_start':'20201101','source_end':'20210131','analysis_month':'202012',
                'location':'US','destination':target,'write_mode':'CREATE TABLE; fail if present',
                'execution':'One reviewed statement at a time; validate only after all tables exist.',
                'files':[]}
    for name, text in files:
        (output/name).write_text(text,encoding='utf-8',newline='\n')
        manifest['files'].append({'file':name,'sha256':hashlib.sha256(text.encode()).hexdigest()})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    return manifest


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--dataset',required=True);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    result=render(a.project,a.dataset,a.output)
    print(f'Rendered {len(result["files"])} ordered files into ignored private configuration. Nothing executed.')
