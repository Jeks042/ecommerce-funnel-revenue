-- GoogleSQL. Aggregate diagnostics only; no identifiers leave the warehouse.
-- Fixed historical source window. Review estimated bytes and cost controls before Run.
WITH purchases AS (
  SELECT _TABLE_SUFFIX AS source_suffix, event_timestamp, user_pseudo_id,
    ecommerce, items,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_entries,
    (SELECT COUNTIF(p.value.int_value IS NOT NULL) FROM UNNEST(event_params) p
      WHERE p.key='ga_session_id') AS sid_int_entries,
    (SELECT MAX(p.value.int_value) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_candidate,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_entries,
    (SELECT MAX(p.value.string_value) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_candidate,
    (SELECT SUM(i.item_revenue) FROM UNNEST(items) i) AS item_revenue,
    (SELECT SUM(i.quantity) FROM UNNEST(items) i) AS item_quantity,
    (SELECT COUNTIF(i.item_revenue IS NULL) FROM UNNEST(items) i) AS missing_item_values
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name='purchase'
), normalized AS (
  SELECT *,
    CASE WHEN sid_entries=1 AND sid_int_entries=1 AND sid_candidate>0
      THEN sid_candidate END AS session_id,
    CASE WHEN currency_entries=1 AND REGEXP_CONTAINS(currency_candidate,r'^[A-Z]{3}$')
      THEN currency_candidate END AS currency,
    CASE WHEN NULLIF(TRIM(ecommerce.transaction_id),'') IS NOT NULL
      AND TRIM(ecommerce.transaction_id) NOT IN ('<Other>','(not set)')
      THEN TRIM(ecommerce.transaction_id) END AS transaction_id,
    ecommerce.purchase_revenue-item_revenue AS native_item_delta
  FROM purchases
), transaction_groups AS (
  SELECT transaction_id, COUNT(*) AS events,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(user_pseudo_id,session_id))) AS identity_variants,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(currency,ecommerce.purchase_revenue,
      ecommerce.purchase_revenue_in_usd,item_revenue,item_quantity))) AS summary_variants,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(ecommerce,items))) AS financial_payload_variants,
    COUNT(DISTINCT source_suffix) AS observed_dates,
    COUNT(DISTINCT event_timestamp) AS observed_timestamps
  FROM normalized WHERE transaction_id IS NOT NULL GROUP BY transaction_id
), classified AS (
  SELECT *, CASE
    WHEN identity_variants>1 OR summary_variants>1 THEN 'identity_or_summary_conflict'
    WHEN financial_payload_variants>1 THEN 'additional_financial_payload_difference'
    WHEN events>1 THEN 'repeated_consistent_financial_payload'
    ELSE 'single_observation' END AS diagnostic_bucket
  FROM transaction_groups
), daily AS (
  SELECT source_suffix,COUNT(*) AS purchase_events,
    COUNTIF(transaction_id IS NULL) AS unusable_id_events,
    COUNTIF(ecommerce.purchase_revenue IS NULL) AS missing_native_revenue_events
  FROM normalized GROUP BY source_suffix
)
SELECT TO_JSON_STRING(STRUCT(
  (SELECT AS STRUCT COUNT(*) AS purchase_events,
    COUNTIF(transaction_id IS NULL) AS unusable_id_events,
    COUNTIF(ecommerce.transaction_id IS NULL) AS null_id_events,
    COUNTIF(ecommerce.transaction_id IS NOT NULL AND TRIM(ecommerce.transaction_id)='') AS blank_id_events,
    COUNTIF(TRIM(ecommerce.transaction_id) IN ('<Other>','(not set)')) AS placeholder_id_events,
    COUNTIF(currency IS NULL OR currency!='USD') AS non_usd_or_unknown_currency_events,
    COUNTIF(ecommerce.purchase_revenue IS NULL) AS missing_native_revenue_events,
    COUNTIF(ecommerce.purchase_revenue_in_usd IS NULL) AS missing_usd_revenue_events,
    COUNTIF(ARRAY_LENGTH(items)=0) AS empty_item_events,
    COUNTIF(missing_item_values>0) AS partial_or_missing_item_value_events,
    COUNTIF(native_item_delta IS NOT NULL) AS comparable_native_item_events,
    COUNTIF(ABS(native_item_delta)>0.01) AS native_item_mismatch_events,
    COUNTIF(native_item_delta>0.01) AS native_above_item_events,
    COUNTIF(native_item_delta< -0.01) AS native_below_item_events,
    COUNTIF(ABS(native_item_delta)>0.01 AND ecommerce.tax_value IS NOT NULL
      AND ABS(native_item_delta-ecommerce.tax_value)<=0.01) AS mismatches_matching_observed_tax,
    COUNTIF(ecommerce.tax_value IS NULL) AS missing_tax_events,
    COUNTIF(ecommerce.shipping_value IS NULL) AS missing_shipping_events
    FROM normalized) AS purchase_checks,
  (SELECT AS STRUCT COUNT(*) AS nonplaceholder_id_groups,
    COUNTIF(events>1) AS repeated_id_groups,
    SUM(events) AS events_with_nonplaceholder_id,
    COUNTIF(identity_variants>1) AS identity_conflict_groups,
    COUNTIF(summary_variants>1) AS summary_conflict_groups,
    COUNTIF(identity_variants>1 AND summary_variants>1) AS overlapping_conflict_groups,
    COUNTIF(identity_variants>1 OR summary_variants>1) AS union_conflict_groups,
    COUNTIF(financial_payload_variants>1) AS different_financial_payload_groups,
    COUNTIF(events>1 AND observed_dates>1) AS repeated_id_groups_across_dates,
    COUNTIF(events>1 AND observed_timestamps>1) AS repeated_id_groups_across_timestamps
    FROM classified) AS transaction_checks,
  ARRAY(SELECT AS STRUCT diagnostic_bucket,COUNT(*) AS id_groups,SUM(events) AS purchase_events
    FROM classified GROUP BY diagnostic_bucket ORDER BY diagnostic_bucket) AS diagnostic_buckets,
  (SELECT AS STRUCT COUNT(*) AS days_with_purchases,
    COUNTIF(unusable_id_events=purchase_events) AS days_without_usable_ids,
    COUNTIF(missing_native_revenue_events>0) AS days_with_missing_native_revenue,
    MIN(source_suffix) AS first_purchase_date,MAX(source_suffix) AS last_purchase_date
    FROM daily) AS daily_purchase_checks,
  ARRAY(SELECT source_suffix FROM daily WHERE unusable_id_events=purchase_events
    ORDER BY source_suffix) AS dates_without_usable_ids
)) AS audit_json;
