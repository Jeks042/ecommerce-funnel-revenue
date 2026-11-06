-- GoogleSQL. Aggregate diagnostics only; candidate rules, not approved sales.
-- Confirm Sandbox and review estimate before Run. Fixed 92-day source window.
WITH purchases AS (
  SELECT _TABLE_SUFFIX AS source_suffix,event_timestamp,user_pseudo_id,device.category AS device,
    ecommerce,items,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_entries,
    (SELECT COUNTIF(p.value.int_value IS NOT NULL) FROM UNNEST(event_params) p
      WHERE p.key='ga_session_id') AS sid_int_entries,
    (SELECT MAX(p.value.int_value) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_candidate,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_entries,
    (SELECT MAX(p.value.string_value) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_candidate,
    (SELECT SUM(i.item_revenue) FROM UNNEST(items) i) AS item_revenue,
    (SELECT SUM(i.quantity) FROM UNNEST(items) i) AS item_quantity,
    (SELECT COUNTIF(i.item_revenue IS NULL OR IS_NAN(i.item_revenue) OR IS_INF(i.item_revenue))
      FROM UNNEST(items) i) AS missing_or_nonfinite_item_values
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131' AND event_name='purchase'
), normalized AS (
  SELECT *,
    CASE WHEN sid_entries=1 AND sid_int_entries=1 AND sid_candidate>0 THEN sid_candidate END AS session_id,
    CASE WHEN currency_entries=1 AND REGEXP_CONTAINS(currency_candidate,r'^[A-Z]{3}$')
      THEN currency_candidate END AS currency,
    CASE WHEN NULLIF(TRIM(ecommerce.transaction_id),'') IS NOT NULL
      AND TRIM(ecommerce.transaction_id) NOT IN ('<Other>','(not set)')
      THEN TRIM(ecommerce.transaction_id) END AS transaction_id,
    -- Sorting removes array-order differences but retains every row, including duplicates.
    TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(i) FROM UNNEST(items) i
      ORDER BY TO_JSON_STRING(i))) AS canonical_items,
    TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_id,i.item_name,i.item_variant,
      i.quantity,i.price,i.price_in_usd,i.item_revenue,i.item_revenue_in_usd,
      i.item_refund,i.item_refund_in_usd)) FROM UNNEST(items) i
      ORDER BY TO_JSON_STRING(STRUCT(i.item_id,i.item_name,i.item_variant,
      i.quantity,i.price,i.price_in_usd,i.item_revenue,i.item_revenue_in_usd,
      i.item_refund,i.item_refund_in_usd)))) AS canonical_core_items
  FROM purchases
), transaction_groups AS (
  SELECT transaction_id,COUNT(*) AS events,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(user_pseudo_id,session_id))) AS identity_variants,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(currency,ecommerce.purchase_revenue,
      ecommerce.purchase_revenue_in_usd,item_revenue,item_quantity))) AS summary_variants,
    COUNT(DISTINCT TO_JSON_STRING(ecommerce)) AS ecommerce_variants,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(ecommerce,items))) AS raw_payload_variants,
    COUNT(DISTINCT canonical_items) AS canonical_item_variants,
    COUNT(DISTINCT canonical_core_items) AS core_item_variants,
    COUNT(DISTINCT source_suffix) AS observed_dates,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(device))) AS device_variants,
    COUNTIF(NULLIF(TRIM(user_pseudo_id),'') IS NULL
      OR TRIM(user_pseudo_id) IN ('<Other>','(not set)') OR session_id IS NULL
      OR currency IS NULL OR currency!='USD') AS invalid_identity_currency_events,
    COUNTIF(ecommerce.purchase_revenue IS NULL OR IS_NAN(ecommerce.purchase_revenue)
      OR IS_INF(ecommerce.purchase_revenue) OR ecommerce.purchase_revenue<0) AS invalid_native_events,
    COUNTIF(ARRAY_LENGTH(items)=0 OR missing_or_nonfinite_item_values>0
      OR item_revenue IS NULL OR IS_NAN(item_revenue) OR IS_INF(item_revenue)
      OR ABS(ecommerce.purchase_revenue-item_revenue)>0.01) AS item_agreement_failure_events,
    MAX(ecommerce.purchase_revenue) AS candidate_native_amount
  FROM normalized WHERE transaction_id IS NOT NULL GROUP BY transaction_id
), classified AS (
  SELECT *,CASE
    WHEN identity_variants>1 OR summary_variants>1 THEN 'identity_or_summary_conflict'
    WHEN ecommerce_variants>1 THEN 'other_ecommerce_difference'
    WHEN core_item_variants>1 THEN 'item_identity_or_money_difference'
    WHEN canonical_item_variants>1 THEN 'item_metadata_difference'
    WHEN raw_payload_variants>1 THEN 'item_order_only_difference'
    WHEN events>1 THEN 'repeated_exact_payload'
    ELSE 'single_observation' END AS diagnostic_bucket,
    identity_variants=1 AND summary_variants=1 AND ecommerce_variants=1
      AND canonical_item_variants=1 AND observed_dates=1 AND device_variants=1
      AND invalid_identity_currency_events=0 AS conservative_id_candidate
  FROM transaction_groups
), policies AS (
  SELECT *,conservative_id_candidate AND invalid_native_events=0 AS native_complete_candidate,
    conservative_id_candidate AND invalid_native_events=0 AND item_agreement_failure_events=0
      AS native_item_agree_candidate
  FROM classified
), field_groups AS (
  SELECT n.transaction_id,f.field_path,COUNT(DISTINCT f.signature) AS variants
  FROM normalized n CROSS JOIN UNNEST([
    STRUCT('ecommerce.purchase_revenue' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.purchase_revenue AS value)) AS signature),
    STRUCT('ecommerce.purchase_revenue_in_usd' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.purchase_revenue_in_usd AS value)) AS signature),
    STRUCT('ecommerce.refund_value' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.refund_value AS value)) AS signature),
    STRUCT('ecommerce.refund_value_in_usd' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.refund_value_in_usd AS value)) AS signature),
    STRUCT('ecommerce.shipping_value' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.shipping_value AS value)) AS signature),
    STRUCT('ecommerce.shipping_value_in_usd' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.shipping_value_in_usd AS value)) AS signature),
    STRUCT('ecommerce.tax_value' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.tax_value AS value)) AS signature),
    STRUCT('ecommerce.tax_value_in_usd' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.tax_value_in_usd AS value)) AS signature),
    STRUCT('ecommerce.total_item_quantity' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.total_item_quantity AS value)) AS signature),
    STRUCT('ecommerce.transaction_id' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.transaction_id AS value)) AS signature),
    STRUCT('ecommerce.unique_items' AS field_path,TO_JSON_STRING(STRUCT(n.ecommerce.unique_items AS value)) AS signature),
    STRUCT('items.affiliation' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.affiliation AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.affiliation AS value)))) AS signature),
    STRUCT('items.coupon' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.coupon AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.coupon AS value)))) AS signature),
    STRUCT('items.creative_name' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.creative_name AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.creative_name AS value)))) AS signature),
    STRUCT('items.creative_slot' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.creative_slot AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.creative_slot AS value)))) AS signature),
    STRUCT('items.item_brand' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_brand AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_brand AS value)))) AS signature),
    STRUCT('items.item_category' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_category AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_category AS value)))) AS signature),
    STRUCT('items.item_category2' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_category2 AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_category2 AS value)))) AS signature),
    STRUCT('items.item_category3' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_category3 AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_category3 AS value)))) AS signature),
    STRUCT('items.item_category4' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_category4 AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_category4 AS value)))) AS signature),
    STRUCT('items.item_category5' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_category5 AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_category5 AS value)))) AS signature),
    STRUCT('items.item_id' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_id AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_id AS value)))) AS signature),
    STRUCT('items.item_list_id' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_list_id AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_list_id AS value)))) AS signature),
    STRUCT('items.item_list_index' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_list_index AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_list_index AS value)))) AS signature),
    STRUCT('items.item_list_name' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_list_name AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_list_name AS value)))) AS signature),
    STRUCT('items.item_name' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_name AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_name AS value)))) AS signature),
    STRUCT('items.item_refund' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_refund AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_refund AS value)))) AS signature),
    STRUCT('items.item_refund_in_usd' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_refund_in_usd AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_refund_in_usd AS value)))) AS signature),
    STRUCT('items.item_revenue' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_revenue AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_revenue AS value)))) AS signature),
    STRUCT('items.item_revenue_in_usd' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_revenue_in_usd AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_revenue_in_usd AS value)))) AS signature),
    STRUCT('items.item_variant' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_variant AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_variant AS value)))) AS signature),
    STRUCT('items.location_id' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.location_id AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.location_id AS value)))) AS signature),
    STRUCT('items.price' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.price AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.price AS value)))) AS signature),
    STRUCT('items.price_in_usd' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.price_in_usd AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.price_in_usd AS value)))) AS signature),
    STRUCT('items.promotion_id' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.promotion_id AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.promotion_id AS value)))) AS signature),
    STRUCT('items.promotion_name' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.promotion_name AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.promotion_name AS value)))) AS signature),
    STRUCT('items.quantity' AS field_path,TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.quantity AS value)) FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(STRUCT(i.quantity AS value)))) AS signature)
  ]) f WHERE n.transaction_id IS NOT NULL
  GROUP BY n.transaction_id,f.field_path
)
SELECT TO_JSON_STRING(STRUCT(
  (SELECT AS STRUCT COUNT(*) AS purchase_events,COUNTIF(transaction_id IS NULL) AS unusable_id_events
    FROM normalized) AS population,
  (SELECT AS STRUCT COUNT(*) AS id_groups,SUM(events) AS usable_id_events,
    COUNTIF(events>1) AS repeated_id_groups,COUNTIF(raw_payload_variants>1) AS raw_payload_difference_groups,
    COUNTIF(identity_variants>1 OR summary_variants>1) AS identity_or_summary_conflict_groups,
    COUNTIF(ecommerce_variants>1) AS ecommerce_difference_groups,
    COUNTIF(core_item_variants>1) AS core_item_difference_groups,
    COUNTIF(canonical_item_variants>1) AS canonical_item_difference_groups,
    COUNTIF(events>1 AND observed_dates>1) AS cross_date_repeated_groups,
    COUNTIF(events>1 AND observed_dates>1 AND (identity_variants>1 OR summary_variants>1))
      AS cross_date_identity_or_summary_conflicts,
    COUNTIF(conservative_id_candidate) AS conservative_id_candidates,
    SUM(IF(conservative_id_candidate,events,0)) AS conservative_candidate_events,
    COUNTIF(native_complete_candidate) AS native_complete_candidates,
    COUNTIF(native_item_agree_candidate) AS native_item_agree_candidates,
    SUM(IF(native_complete_candidate,candidate_native_amount,NULL)) AS diagnostic_native_amount,
    SUM(IF(native_item_agree_candidate,candidate_native_amount,NULL)) AS diagnostic_agreeing_native_amount
    FROM policies) AS group_checks,
  ARRAY(SELECT AS STRUCT diagnostic_bucket,COUNT(*) AS id_groups,SUM(events) AS purchase_events
    FROM policies GROUP BY diagnostic_bucket ORDER BY diagnostic_bucket) AS diagnostic_buckets,
  ARRAY(SELECT AS STRUCT field_path,COUNTIF(variants>1) AS differing_id_groups
    FROM field_groups GROUP BY field_path ORDER BY field_path) AS field_differences,
  ARRAY(SELECT AS STRUCT p.diagnostic_bucket,f.field_path,COUNT(*) AS differing_id_groups
    FROM field_groups f JOIN policies p USING(transaction_id) WHERE f.variants>1
    GROUP BY p.diagnostic_bucket,f.field_path ORDER BY p.diagnostic_bucket,f.field_path)
    AS field_differences_by_bucket,
  ARRAY(SELECT AS STRUCT source_suffix,device,COUNT(*) AS purchase_events,
    COUNTIF(n.transaction_id IS NULL) AS unusable_id_events,
    COUNTIF(p.conservative_id_candidate) AS conservative_candidate_events,
    COUNTIF(p.native_item_agree_candidate) AS native_item_agree_candidate_events
    FROM normalized n LEFT JOIN policies p USING(transaction_id)
    GROUP BY source_suffix,device ORDER BY source_suffix,device) AS coverage_by_date_device
)) AS audit_json;
