"""Render the production detail query against synthetic, fully typed source rows."""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`'


def literal(value, kind):
    if value is None:
        return f'CAST(NULL AS {kind})'
    if kind == 'STRING':
        return json.dumps(value)
    return f'CAST({value} AS {kind})'


def item(sku='a', amount=10, quantity=1, **changes):
    return dict(item_id=sku, item_name=sku, item_variant='standard', quantity=quantity,
                price=amount, price_in_usd=amount, item_revenue=amount,
                item_revenue_in_usd=amount, item_category='original', **changes)


def prepare():
    fields = json.loads((ROOT/'reports/evidence/purchase-field-inventory-20261106.json').read_text())['field_coverage']
    schemas = {prefix: [(r['field_path'].split('.')[1], r['data_type']) for r in fields
                       if r['field_path'].startswith(prefix+'.')]
               for prefix in ('ecommerce', 'items')}

    def struct(values, prefix):
        return 'STRUCT('+','.join(f'{literal(values.get(name),kind)} AS {name}'
                                 for name, kind in schemas[prefix])+')'

    rows = []

    def event(tx, *, lines=None, native=10, user=None, sid=1, date='20201101',
              device='desktop', currency='USD', **ecommerce_changes):
        lines = lines if lines is not None else [item(amount=native)]
        ecom = dict(transaction_id=tx, purchase_revenue=native,
                    purchase_revenue_in_usd=native, tax_value=0)
        ecom.update(ecommerce_changes)
        rows.append(dict(tx=tx, user=user or 'user-'+str(tx), sid=sid, date=date,
                         device=device, currency=currency, ecom=ecom, lines=deepcopy(lines)))

    # Order-only changes must match; labels and equal totals must not conceal differences.
    lines = [item('a',8), item('b',12)]
    event('a',native=20,lines=lines); event('a',native=20,lines=lines[::-1])
    event('b'); changed=item(); changed['item_category']='changed'; event('b',lines=[changed])
    event('c',lines=[item('a',3),item('b',7)])
    event('c',lines=[item('a',4),item('b',6)])
    event('d'); event('d')
    # Multiplicity is significant, even for zero-valued, zero-quantity synthetic lines.
    event('e',native=0,lines=[item(amount=0,quantity=0)]*2)
    event('e',native=0,lines=[item(amount=0,quantity=0)])
    event('f',user='one'); event('f',user='two')
    event('g',native=None,lines=[item(amount=None)]); event('g',native=None,lines=[item(amount=None)])
    event('h',native=5); event(None)
    event('j'); event('j',tax_value=2)
    event('k'); event('k',date='20201102')
    event('l'); event('l',device='mobile')
    event('m',sid=-1)
    event('n',native=10,lines=[item(amount=8)])
    event('o'); changed=item(); changed['item_name']='changed'; event('o',lines=[changed])
    event('p'); event('p',currency='EUR')
    event('q',user='<Other>')

    sql_rows = []
    for timestamp, row in enumerate(rows,1):
        params = "[STRUCT('ga_session_id' AS key, STRUCT("+literal(row['sid'],'INT64')+" AS int_value, CAST(NULL AS STRING) AS string_value) AS value), STRUCT('currency' AS key, STRUCT(CAST(NULL AS INT64) AS int_value,"+literal(row['currency'],'STRING')+" AS string_value) AS value)]"
        sql_rows.append('STRUCT('+literal(row['date'],'STRING')+' AS _TABLE_SUFFIX,'
                        "'purchase' AS event_name,"+str(timestamp)+' AS event_timestamp,'
                        +literal(row['user'],'STRING')+' AS user_pseudo_id, STRUCT('
                        +literal(row['device'],'STRING')+' AS category) AS device,'
                        +struct(row['ecom'],'ecommerce')+' AS ecommerce, ['
                        +','.join(struct(line,'items') for line in row['lines'])
                        +'] AS items,'+params+' AS event_params)')
    production = (ROOT/'sql/05_purchase_detail_diagnostics.sql').read_text(encoding='utf-8')
    assert production.count(SOURCE) == 1 and production.count('WITH purchases AS (') == 1
    fixture = production.replace(SOURCE,'fixture_source').replace('WITH purchases AS (',
        'WITH fixture_source AS (SELECT * FROM UNNEST([\n'+',\n'.join(sql_rows)+'\n])), purchases AS (',1)
    assert 'bigquery-public-data' not in fixture
    (ROOT/'private').mkdir(exist_ok=True)
    (ROOT/'private/purchase_detail_fixture.sql').write_text(fixture,encoding='utf-8',newline='\n')
    expected = {
        'population': {'purchase_events':29,'unusable_id_events':1},
        'group_checks': {'id_groups':16,'usable_id_events':28,'repeated_id_groups':12,
            'raw_payload_difference_groups':6,'identity_or_summary_conflict_groups':2,
            'ecommerce_difference_groups':1,'core_item_difference_groups':3,
            'canonical_item_difference_groups':4,'cross_date_repeated_groups':1,
            'cross_date_identity_or_summary_conflicts':0,'conservative_id_candidates':5,
            'conservative_candidate_events':8,'native_complete_candidates':4,
            'native_item_agree_candidates':3,'diagnostic_native_amount':45,
            'diagnostic_agreeing_native_amount':35},
        'buckets': {'identity_or_summary_conflict':(2,4),'other_ecommerce_difference':(1,2),
            'item_identity_or_money_difference':(3,6),'item_metadata_difference':(1,2),
            'item_order_only_difference':(1,2),'repeated_exact_payload':(4,8),'single_observation':(4,4)}
    }
    (ROOT/'private/purchase_detail_fixture_expected.json').write_text(json.dumps(expected,indent=2)+'\n')
    print(f'Prepared {len(rows)} synthetic events: production SQL retained, no public-source scan.')


if __name__ == '__main__':
    prepare()
