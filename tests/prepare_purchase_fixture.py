"""Generate a warehouse-native fixture using the actual reconciliation SQL.

Run this file from the repository root. No credentials or external libraries needed.
The generated query reads synthetic literals only and is written under private/.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`"


def literal(value, kind):
    if value is None:
        return f"CAST(NULL AS {kind})"
    if kind == "STRING":
        return json.dumps(value)
    return f"CAST({value} AS {kind})"


def event(tx, user, sid, native, item_values, timestamp, tax=0):
    item_rows = ",".join(
        f"STRUCT('sku{i}' AS item_id, 1 AS quantity, {literal(v, 'FLOAT64')} AS item_revenue)"
        for i, v in enumerate(item_values)
    )
    return (
        "STRUCT('20201101' AS _TABLE_SUFFIX, 'purchase' AS event_name, "
        f"{timestamp} AS event_timestamp, {literal(user,'STRING')} AS user_pseudo_id, "
        f"STRUCT({literal(tx,'STRING')} AS transaction_id, {literal(native,'FLOAT64')} AS purchase_revenue, "
        f"{literal(native if native is not None else 5,'FLOAT64')} AS purchase_revenue_in_usd, "
        f"{literal(tax,'FLOAT64')} AS tax_value, CAST(NULL AS FLOAT64) AS shipping_value) AS ecommerce, "
        f"[{item_rows}] AS items, "
        f"[STRUCT('ga_session_id' AS key, STRUCT({sid} AS int_value, CAST(NULL AS STRING) AS string_value) AS value), "
        "STRUCT('currency' AS key, STRUCT(CAST(NULL AS INT64) AS int_value, 'USD' AS string_value) AS value)] AS event_params)"
    )


def prepare():
    # Expected groups are declared independently below; classification uses production SQL.
    rows = [
        event('a','u1',1,20,[8,12],1), event('a','u1',1,20,[8,12],2),
        event('b','u2',2,15,[15],3), event('b','u2',2,16,[16],4),
        event('c','u3',3,7,[7],5), event('c','u4',4,7,[7],6),
        event('d','u5',5,None,[None],7), event(None,'u6',6,5,[5],8),
        event('f','u7',7,10,[8],9,tax=2),
        event('g','u8',8,10,[3,7],10), event('g','u8',8,10,[4,6],11),
    ]
    production = (ROOT/'sql/03_purchase_reconciliation.sql').read_text(encoding='utf-8')
    assert production.count(SOURCE) == 1
    assert production.count('WITH purchases AS (') == 1
    fixture = production.replace(SOURCE, 'fixture_source').replace(
        'WITH purchases AS (', 'WITH fixture_source AS (SELECT * FROM UNNEST([\n' + ',\n'.join(rows) + '\n])), purchases AS (', 1
    )
    assert 'bigquery-public-data' not in fixture
    out = ROOT/'private/purchase_fixture.sql'
    out.parent.mkdir(exist_ok=True)
    out.write_text(fixture,encoding='utf-8',newline='\n')
    expected = {
        'purchase_events':11,'unusable_id_events':1,'missing_native_revenue_events':1,
        'native_item_mismatch_events':1,'mismatches_matching_observed_tax':1,
        'nonplaceholder_id_groups':6,'repeated_id_groups':4,'events_with_nonplaceholder_id':10,
        'identity_conflict_groups':1,'summary_conflict_groups':1,'overlapping_conflict_groups':0,
        'union_conflict_groups':2,'different_financial_payload_groups':2,
        'buckets':{'identity_or_summary_conflict':(2,4),
            'additional_financial_payload_difference':(1,2),
            'repeated_consistent_financial_payload':(1,2),'single_observation':(2,2)},
    }
    (ROOT/'private/purchase_fixture_expected.json').write_text(json.dumps(expected,indent=2),encoding='utf-8')
    print('Prepared eleven synthetic purchases using the production query; no public-source scan.')


if __name__ == '__main__':
    prepare()
