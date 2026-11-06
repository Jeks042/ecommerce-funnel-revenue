"""Test the production tracking SQL with explicit per-journey expectations."""
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`'


def lit(value,kind='STRING'):
    if value is None:
        return f'CAST(NULL AS {kind})'
    return json.dumps(value) if kind=='STRING' else f'CAST({value} AS {kind})'


def prepare():
    normal=[('session_start',0),('view_item',1),('add_to_cart',2),('begin_checkout',3),('purchase',4)]
    # Expectations describe the cases, not a second implementation of the SQL.
    cases=[
        ('a',normal,3,3,True,False,True),
        ('b',[('session_start',0),('view_item',1),('add_to_cart',1),('begin_checkout',1),('purchase',1)],0,3,True,False,True),
        ('c',[('session_start',0),('view_item',2),('add_to_cart',1),('add_to_cart',3),('begin_checkout',2),('begin_checkout',4),('purchase',3),('purchase',5)],3,3,True,False,True),
        ('d',[('session_start',0),('view_item',1),('begin_checkout',2),('purchase',3)],0,0,True,False,True),
        ('e',normal[1:],3,3,False,False,True),
        ('f',[normal[0]]+normal,3,3,False,False,True),
        ('g',normal,3,3,True,False,False),
        ('h',normal,3,3,True,True,True),
        ('i',normal,3,3,True,True,True),
        ('j',[('view_item',0),('session_start',1),('add_to_cart',2),('begin_checkout',3),('purchase',4)],3,3,False,False,True),
        ('k',normal,3,3,False,False,True),  # No session parameter: excluded from keyed journeys.
        ('l',normal,3,3,False,False,True),  # Device changes.
        ('m',normal,3,3,False,False,False), # Source date conflicts with UTC timestamp.
        ('n',normal,0,0,False,False,True),  # Cart has no timestamp.
        ('o',normal,3,3,False,False,True),  # First-user context changes.
        ('p',[('session_start',0)],0,0,True,False,True), # Positive ID is not a usable Unix time.
    ]
    rows=[]; expectations=[]
    for name,layout,strict,tied,anchored,edge,single_date in cases:
        start={'g':'2020-11-15T23:59:58','h':'2020-11-01T12:00:00','i':'2021-01-31T12:00:00'}.get(name,'2020-11-15T12:00:00')
        base=int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp())
        sid=9223372036854775807 if name=='p' else base
        user='fixture-'+name
        if name!='k':
            expectations.append(f"STRUCT({lit(user)} AS user_pseudo_id,{strict} AS strict_level,{tied} AS tied_level,{str(anchored).upper()} AS anchored_candidate,{str(edge).upper()} AS touches_window_edge,{str(single_date).upper()} AS single_date)")
        for event,offset in layout:
            timestamp=(base+offset)*1000000
            suffix=datetime.fromtimestamp(timestamp/1000000,timezone.utc).strftime('%Y%m%d')
            if name=='m' and event=='add_to_cart': suffix='20201116'
            if name=='n' and event=='add_to_cart': timestamp=None
            params="ARRAY<STRUCT<key STRING,value STRUCT<int_value INT64,string_value STRING>>>[]" if name=='k' else f"[STRUCT('ga_session_id' AS key, STRUCT({sid} AS int_value,CAST(NULL AS STRING) AS string_value) AS value)]"
            device='mobile' if name=='l' and event=='add_to_cart' else 'desktop'
            source='changed' if name=='o' and event=='add_to_cart' else 'fixture'
            bundle=2 if name=='c' and event=='begin_checkout' and offset==2 else 1
            rows.append(f"STRUCT({lit(suffix)} AS _TABLE_SUFFIX,{lit(suffix)} AS event_date,{lit(timestamp,'INT64')} AS event_timestamp,{lit(event)} AS event_name,{lit(user)} AS user_pseudo_id,STRUCT({lit(device)} AS category) AS device,STRUCT({lit(source)} AS source,'fixture' AS medium) AS traffic_source,{bundle} AS event_bundle_sequence_id,CAST(NULL AS INT64) AS event_previous_timestamp,CAST(NULL AS INT64) AS event_server_timestamp_offset,STRUCT({lit('fixture-order-'+name if event=='purchase' else None)} AS transaction_id) AS ecommerce,{params} AS event_params)")
    sql=(ROOT/'sql/06_tracking_timing_sensitivity.sql').read_text(encoding='utf-8')
    assert sql.count(SOURCE)==1 and sql.count('WITH raw AS (')==1
    sql=sql.replace(SOURCE,'fixture_source').replace('WITH raw AS (',
        'WITH fixture_source AS (SELECT * FROM UNNEST([\n'+',\n'.join(rows)+'\n])), raw AS (',1)
    # Per-case assertions reuse production CTEs and return only a mismatch count.
    assertion="""(SELECT COUNTIF(
      (IF(s.strict_cart IS NOT NULL,1,0)+IF(s.strict_checkout IS NOT NULL,1,0)+IF(s.strict_purchase IS NOT NULL,1,0))!=e.strict_level
      OR (IF(s.tied_cart IS NOT NULL,1,0)+IF(s.tied_checkout IS NOT NULL,1,0)+IF(s.tied_purchase IS NOT NULL,1,0))!=e.tied_level
      OR s.anchored_candidate!=e.anchored_candidate OR s.touches_window_edge!=e.touches_window_edge
      OR (s.observed_dates=1)!=e.single_date)
      FROM purchase_step s JOIN UNNEST(["""+','.join(expectations)+"""]) e USING(user_pseudo_id)) AS fixture_case_failures,
  """
    sql=sql.replace('SELECT TO_JSON_STRING(STRUCT(','SELECT TO_JSON_STRING(STRUCT(\n  '+assertion,1)
    assert 'bigquery-public-data' not in sql
    expected={'population':{'events':78,'source_days':4,'ineligible_key_events':5,'unusable_timestamp_events':1},
        'session_checks':{'keyed_sessions':15,'cross_date_sessions':2,'without_start':1,'repeated_starts':1,
            'repeated_start_same_timestamp':1,'single_start_after_first_event':1,'edge_sessions':2,
            'multiple_device_sessions':1,'multiple_first_user_context_sessions':1,'observed_spans_over_24_hours':0,
            'invalid_sid_timestamp_sessions':1,'sid_first_event_diff_over_60_seconds':0},
        'fixture_case_failures':0,
        'scopes':{'all_keyed':(15,73,11,12),'all_keyed_interior':(13,63,9,10),
            'one_start':(13,63,9,10),'anchored_candidate':(8,38,5,6),
            'anchored_candidate_interior':(6,28,3,4),'anchored_candidate_interior_single_date':(5,23,2,3)}}
    (ROOT/'private').mkdir(exist_ok=True)
    (ROOT/'private/tracking_fixture.sql').write_text(sql,encoding='utf-8',newline='\n')
    (ROOT/'private/tracking_fixture_expected.json').write_text(json.dumps(expected,indent=2)+'\n')
    print(f'Prepared {len(rows)} synthetic events and {len(expectations)} keyed journey assertions; source-free query.')


if __name__=='__main__':
    prepare()
