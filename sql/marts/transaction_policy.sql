WITH purchases AS (
 SELECT *,
   (SELECT SUM(i.item_revenue) FROM UNNEST(items) i) AS item_revenue,
   (SELECT SUM(i.quantity) FROM UNNEST(items) i) AS item_quantity,
   (SELECT COUNTIF(i.item_revenue IS NULL OR IS_NAN(i.item_revenue) OR IS_INF(i.item_revenue)) FROM UNNEST(items) i) AS missing_or_nonfinite_item_values,
   TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(i) FROM UNNEST(items) i ORDER BY TO_JSON_STRING(i))) AS canonical_items,
   TO_JSON_STRING(ARRAY(SELECT TO_JSON_STRING(STRUCT(i.item_id,i.item_name,i.item_variant,i.quantity,i.price,i.price_in_usd,i.item_revenue,i.item_revenue_in_usd,i.item_refund,i.item_refund_in_usd)) FROM UNNEST(items) i ORDER BY TO_JSON_STRING(STRUCT(i.item_id,i.item_name,i.item_variant,i.quantity,i.price,i.price_in_usd,i.item_revenue,i.item_revenue_in_usd,i.item_refund,i.item_refund_in_usd)))) AS canonical_core_items
 FROM `{{dataset}}.stg_events` WHERE event_name='purchase'
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
  FROM purchases WHERE transaction_id IS NOT NULL GROUP BY transaction_id
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
)
SELECT * FROM policies
