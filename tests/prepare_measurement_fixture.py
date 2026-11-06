"""Exercise the actual acceptance SQL with declared synthetic journey outcomes."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE='`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`'


def prepare():
    (ROOT/'private').mkdir(parents=True,exist_ok=True)
    # One ordinary journey; a replay straddling checkout; two orders in one visit;
    # missing ID; item disagreement; no purchase; timestamp ties; cross-midnight;
    # a >24h journey; and a conflicting ID whose other observation is in January.
    cases=[
        ('normal',[0,1,2,3,4],10,'2020-12-15 12:00:00+00'),
        ('replay',[0,1,2,3,2,4],10,'2020-12-15 12:00:00+00'),
        ('two_orders',[0,1,2,3,4,5],10,'2020-12-15 12:00:00+00'),
        ('missing',[0,1,2,3,4],10,'2020-12-15 12:00:00+00'),
        ('disagree',[0,1,2,3,4],8,'2020-12-15 12:00:00+00'),
        ('no_purchase',[0,1,2,3],10,'2020-12-15 12:00:00+00'),
        ('ties',[0,1,1,1,1],10,'2020-12-15 12:00:00+00'),
        ('midnight',[0,1,2,3,4],10,'2020-12-15 23:59:58+00'),
        ('long',[0,1,2,3,90000],10,'2020-12-15 12:00:00+00'),
        ('conflict_dec',[0,1,2,3,4],10,'2020-12-15 12:00:00+00'),
        ('conflict_jan',[0,1,2,3,4],10,'2021-01-15 12:00:00+00'),
    ]
    rows=[]
    for name,offsets,item_amount,start in cases:
        names=['session_start','view_item','add_to_cart','begin_checkout']+['purchase']*(len(offsets)-4)
        rows.append('STRUCT('+json.dumps(name)+' AS case_name,TIMESTAMP('+json.dumps(start)+') AS start_time,'
                    +str(item_amount)+' AS item_amount,['+','.join('STRUCT('+json.dumps(event)+' AS event_name,'+str(offset)+' AS seconds,'+str(i)+' AS position)' for i,(event,offset) in enumerate(zip(names,offsets)))+'] AS steps)')
    fixture='''fixture_cases AS (SELECT * FROM UNNEST([
'''+',\n'.join(rows)+'''
])), fixture_events AS (
  SELECT *,UNIX_MICROS(TIMESTAMP_ADD(start_time,INTERVAL seconds SECOND)) AS event_timestamp,
    CASE WHEN event_name!='purchase' OR case_name='missing' THEN NULL
      WHEN STARTS_WITH(case_name,'conflict') THEN 'shared-conflicting-id'
      WHEN case_name='two_orders' THEN CONCAT(case_name,CAST(position AS STRING))
      ELSE case_name END AS tx
  FROM fixture_cases CROSS JOIN UNNEST(steps)
), fixture_source AS (
  SELECT FORMAT_TIMESTAMP('%Y%m%d',TIMESTAMP_MICROS(event_timestamp),'UTC') AS _TABLE_SUFFIX,
    FORMAT_TIMESTAMP('%Y%m%d',TIMESTAMP_MICROS(event_timestamp),'UTC') AS event_date,
    event_timestamp,event_name,case_name AS user_pseudo_id,STRUCT('desktop' AS category) AS device,
    STRUCT('fixture' AS source,'fixture' AS medium) AS traffic_source,
    1 AS event_bundle_sequence_id,CAST(NULL AS INT64) AS event_previous_timestamp,
    CAST(NULL AS INT64) AS event_server_timestamp_offset,
    STRUCT(tx AS transaction_id,IF(event_name='purchase',10.0,NULL) AS purchase_revenue,
      IF(event_name='purchase',10.0,NULL) AS purchase_revenue_in_usd) AS ecommerce,
    ARRAY(SELECT AS STRUCT 'a' AS item_id,'a' AS item_name,'standard' AS item_variant,
      1 AS quantity,10.0 AS price,10.0 AS price_in_usd,CAST(item_amount AS FLOAT64) AS item_revenue,
      CAST(item_amount AS FLOAT64) AS item_revenue_in_usd,
      CAST(NULL AS FLOAT64) AS item_refund,CAST(NULL AS FLOAT64) AS item_refund_in_usd
      FROM UNNEST([1]) WHERE event_name='purchase') AS items,
    [STRUCT('ga_session_id' AS key,STRUCT(1 AS int_value,CAST(NULL AS STRING) AS string_value) AS value),
     STRUCT('currency',STRUCT(CAST(NULL AS INT64),'USD'))] AS event_params
  FROM fixture_events
), '''
    production=(ROOT/'sql/07_measurement_gate.sql').read_text()
    assert production.count(SOURCE)==1
    sql=production.replace('WITH source_rows AS (','WITH '+fixture+'source_rows AS (',1).replace(SOURCE,'fixture_source')
    (ROOT/'private/measurement_fixture.sql').write_text(sql,encoding='utf-8',newline='\n')
    expected={'linkage':{'keyed_sessions':11,'keyed_events':56,'keyed_purchase_events':12,
        'candidate_events':9,'linked_candidate_transactions':8,'linked_agreeing_transactions':7,
        'linked_agreeing_recorded_value':70,'missing_id_events':1,'rejected_id_events':2},
        'candidates':{'candidate_transactions':8,'native_complete_transactions':8,'agreeing_transactions':7,
            'agreeing_recorded_value':70,'candidate_events':9},
        'long_span_review':{'sessions':1,'events':5,'raw_purchase_events':1,'candidate_transactions':1,
            'anchored_sessions':1,'single_date_sessions':0},
        'scopes':{'all_keyed':(11,8,7,5,6,6),'anchored_interior':(11,8,7,5,6,6),
            'anchored_interior_single_date':(9,6,5,3,4,4)}}
    (ROOT/'private/measurement_fixture_expected.json').write_text(json.dumps(expected,indent=2)+'\n')
    print('Prepared 56 synthetic events covering 11 journeys; no public-source scan.')


if __name__=='__main__':
    prepare()
