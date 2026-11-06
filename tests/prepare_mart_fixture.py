"""Render production models as temporary tables over typed synthetic source rows."""
import json
from pathlib import Path
import sys
from prepare_measurement_fixture import prepare

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from render_marts import model_queries, MODELS, SOURCE


def prepare_fixture():
    prepare()
    old=(ROOT/'private/measurement_fixture.sql').read_text()
    prefix=old.split('WITH ',1)[1].split('source_rows AS (',1)[0]
    additions=[]
    for name,offsets in [('multi_item',[0,1,2,3,4,5]),('currency_conflict',[0,1,2,3,4,5]),
                         ('missing_key',[0,1,2,3,4]),('repeat_key',[0,1,2,3,4]),
                         ('out_of_order',[0,2,1,3,4]),('duplicate_lines',[0,1,2,3,4]),
                         ('metadata_change',[0,1,2,3,4,5])]:
        steps=[('session_start',offsets[0]),('view_item',offsets[1]),('add_to_cart',offsets[2]),('begin_checkout',offsets[3])]+[('purchase',t) for t in offsets[4:]]
        additions.append('STRUCT('+json.dumps(name)+' AS case_name,TIMESTAMP("2020-12-15 12:00:00+00") AS start_time,10 AS item_amount,['+','.join('STRUCT('+json.dumps(event)+' AS event_name,'+str(t)+' AS seconds,'+str(i)+' AS position)' for i,(event,t) in enumerate(steps))+'] AS steps)')
    prefix=prefix.replace('\n])), fixture_events AS (',',\n'+',\n'.join(additions)+'\n])), fixture_events AS (',1)
    prefix=prefix.replace("IF(event_name='purchase',10.0,NULL)","IF(event_name='purchase',IF(case_name='multi_item',20.0,10.0),NULL)")
    start=prefix.index('    ARRAY(SELECT AS STRUCT')
    end=prefix.index(' AS items,',start)
    item_expression='''    ARRAY(SELECT AS STRUCT
      IF(case_name='multi_item',CONCAT('a',CAST(item_position AS STRING)),'a') AS item_id,
      'a' AS item_name,'standard' AS item_variant,1 AS quantity,
      amount AS price,amount AS price_in_usd,amount AS item_revenue,amount AS item_revenue_in_usd,
      CAST(NULL AS FLOAT64) AS item_refund,CAST(NULL AS FLOAT64) AS item_refund_in_usd,
      IF(case_name='metadata_change' AND position=5,'changed','baseline') AS promotion_name
      FROM UNNEST(CASE WHEN case_name='multi_item' THEN [8.0,12.0]
        WHEN case_name='duplicate_lines' THEN [5.0,5.0]
        ELSE [CAST(item_amount AS FLOAT64)] END) amount WITH OFFSET item_position
      WHERE event_name='purchase'
      ORDER BY IF(case_name='multi_item' AND position=5,-item_position,item_position))'''
    prefix=prefix[:start]+item_expression+prefix[end:]
    start=prefix.index("    [STRUCT('ga_session_id'")
    end=prefix.index(' AS event_params',start)
    prefix=prefix[:start]+'''    ARRAY_CONCAT(
      IF(case_name='missing_key',[],[STRUCT('ga_session_id' AS key,STRUCT(1 AS int_value,CAST(NULL AS STRING) AS string_value) AS value)]),
      IF(case_name='repeat_key',[STRUCT('ga_session_id' AS key,STRUCT(2 AS int_value,CAST(NULL AS STRING) AS string_value) AS value)],[]),
      [STRUCT('currency' AS key,STRUCT(CAST(NULL AS INT64) AS int_value,IF(case_name='currency_conflict' AND position=5,'EUR','USD') AS string_value) AS value)])'''+prefix[end:]
    queries=model_queries()
    def cte_refs(sql):
        for name in MODELS:sql=sql.replace('`{{dataset}}.'+name+'`',name)
        return sql
    validation=(ROOT/'sql/marts/validate.sql').read_text().strip().rstrip(';')
    script='CREATE TEMP TABLE fixture_source AS WITH '+prefix.rstrip().removesuffix(',')+' SELECT * EXCEPT(_TABLE_SUFFIX),_TABLE_SUFFIX AS fixture_table_suffix FROM fixture_source;\n'
    script+='\n'.join('CREATE TEMP TABLE '+name+' AS\n'+cte_refs(sql.replace(SOURCE,'fixture_source').replace('_TABLE_SUFFIX','fixture_table_suffix'))+';' for name,sql in queries.items())
    script+='\n'+cte_refs(validation)+';\n'
    assert 'bigquery-public-data' not in script and '{{dataset}}' not in script
    assert script.count('CREATE TEMP TABLE')==9
    (ROOT/'private/mart_fixture_materialized.sql').write_text(script,encoding='utf-8',newline='\n')
    expected={'source':{'events':94,'purchase_events':22,'unkeyed_events':10},
        'transaction_policy':{'id_groups':16,'qualified_ids':11,'agreeing_ids':10},
        'transactions':{'transactions':11,'recorded_events':13,'item_rows':13,'selected_recorded_value':110},
        'primary':{'sessions':13,'candidate_transactions':9,'candidate_purchase_sessions':8,
            'strict_candidate_sessions':5,'last_time_candidate_sessions':6,'tied_candidate_sessions':6,
            'agreeing_transactions':8,'agreeing_recorded_value':90,'raw_purchase_events':17,
            'missing_id_events':1,'rejected_id_events':5,'candidate_events':11}}
    (ROOT/'private/mart_fixture_expected.json').write_text(json.dumps(expected,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Prepared 94 source-free events across 18 journeys, including malformed keys and item multiplicity.')
    return script


if __name__=='__main__':
    prepare_fixture()
