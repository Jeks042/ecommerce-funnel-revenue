-- GoogleSQL pilot. Read-only; output contains aggregate diagnostics only.
-- Start with one day. Replace BOTH literal bounds together after reviewing the pilot.
-- Inspect the validator estimate before Run; execute only in confirmed Sandbox.
WITH raw AS (
  SELECT _TABLE_SUFFIX AS source_suffix, event_date, event_timestamp, event_name,
    user_pseudo_id, device.category AS device_category,
    traffic_source.source AS first_user_source, traffic_source.medium AS first_user_medium,
    ecommerce,
    ARRAY_LENGTH(items) AS item_rows,
    (SELECT SUM(i.quantity) FROM UNNEST(items) i) AS item_quantity,
    (SELECT SUM(i.item_revenue) FROM UNNEST(items) i) AS item_revenue,
    (SELECT COUNTIF(i.item_revenue IS NULL) FROM UNNEST(items) i) AS item_revenue_nulls,
    (SELECT COUNTIF(i.quantity IS NULL) FROM UNNEST(items) i) AS item_quantity_nulls,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_entries,
    (SELECT COUNTIF(p.value.int_value IS NOT NULL) FROM UNNEST(event_params) p
      WHERE p.key='ga_session_id') AS sid_int_entries,
    (SELECT MAX(p.value.int_value) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_candidate,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_entries,
    (SELECT MAX(p.value.string_value) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_candidate
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20201101'
), base AS (
  SELECT *,
    CASE WHEN sid_entries=1 AND sid_int_entries=1 AND sid_candidate>0
      THEN sid_candidate END AS session_id,
    NULLIF(TRIM(user_pseudo_id),'') IS NOT NULL
      AND TRIM(user_pseudo_id) NOT IN ('<Other>','(not set)') AS user_key_usable,
    CASE WHEN currency_entries=1 AND REGEXP_CONTAINS(currency_candidate,r'^[A-Z]{3}$')
      THEN currency_candidate END AS currency,
    CASE WHEN NULLIF(TRIM(ecommerce.transaction_id),'') IS NOT NULL
      AND TRIM(ecommerce.transaction_id) NOT IN ('<Other>','(not set)')
      THEN TRIM(ecommerce.transaction_id) END AS transaction_id
  FROM raw
), sessions AS (
  SELECT user_pseudo_id, session_id, COUNT(*) AS events,
    COUNT(DISTINCT event_date) AS event_dates,
    COUNT(DISTINCT device_category) AS device_categories,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(first_user_source,first_user_medium))) AS first_user_contexts,
    COUNTIF(event_name='session_start') AS start_events,
    COUNTIF(event_name='purchase') AS purchase_events
  FROM base WHERE user_key_usable AND session_id IS NOT NULL
  GROUP BY user_pseudo_id, session_id
), transactions AS (
  SELECT transaction_id, COUNT(*) AS purchase_events,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(user_pseudo_id,session_id))) AS identity_variants,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(currency,ecommerce.purchase_revenue,
      ecommerce.purchase_revenue_in_usd,item_revenue,item_quantity))) AS monetary_variants
  FROM base WHERE event_name='purchase' AND transaction_id IS NOT NULL
  GROUP BY transaction_id
), timestamp_groups AS (
  SELECT user_pseudo_id, session_id, event_timestamp,
    COUNT(*) AS events, COUNT(DISTINCT event_name) AS step_types
  FROM base WHERE user_key_usable AND session_id IS NOT NULL
    AND event_name IN ('view_item','add_to_cart','begin_checkout','purchase')
  GROUP BY user_pseudo_id,session_id,event_timestamp
), reused_session_ids AS (
  SELECT session_id, COUNT(DISTINCT user_pseudo_id) AS users
  FROM base WHERE user_key_usable AND session_id IS NOT NULL GROUP BY session_id
)
SELECT TO_JSON_STRING(STRUCT(
  (SELECT AS STRUCT COUNT(*) AS events, COUNT(DISTINCT source_suffix) AS source_days,
    COUNT(DISTINCT event_date) AS event_dates,
    COUNTIF(source_suffix!=event_date OR event_date IS NULL) AS date_suffix_mismatch,
    COUNTIF(event_timestamp IS NULL) AS missing_timestamps,
    COUNTIF(FORMAT_TIMESTAMP('%Y%m%d',SAFE.TIMESTAMP_MICROS(event_timestamp),'UTC')!=event_date)
      AS utc_date_differs_from_event_date,
    COUNTIF(NOT user_key_usable) AS unusable_user_events,
    COUNTIF(session_id IS NULL) AS unusable_session_id_events,
    COUNTIF(NOT user_key_usable OR session_id IS NULL) AS ineligible_key_events,
    COUNTIF(sid_entries>1) AS repeated_session_parameter_events,
    COUNTIF(sid_entries=1 AND sid_int_entries=0) AS wrong_session_parameter_type_events,
    COUNTIF(currency_entries>1) AS repeated_currency_parameter_events
    FROM base) AS coverage,
  ARRAY(SELECT AS STRUCT event_name,COUNT(*) AS events,
    COUNTIF(NOT user_key_usable OR session_id IS NULL) AS ineligible_key_events
    FROM base GROUP BY event_name ORDER BY event_name) AS event_coverage,
  (SELECT AS STRUCT COUNT(*) AS eligible_composite_sessions,
    COUNTIF(event_dates>1) AS cross_event_date_sessions,
    COUNTIF(start_events=0) AS sessions_without_start,
    COUNTIF(start_events>1) AS sessions_with_repeated_start,
    COUNTIF(device_categories>1) AS sessions_with_multiple_devices,
    COUNTIF(first_user_contexts>1) AS sessions_with_multiple_first_user_contexts
    FROM sessions) AS session_checks,
  (SELECT AS STRUCT COUNTIF(events>1) AS tied_step_timestamp_groups,
    COUNTIF(step_types>1) AS tied_different_step_groups FROM timestamp_groups) AS ordering_checks,
  (SELECT COUNTIF(users>1) FROM reused_session_ids) AS session_ids_shared_by_users,
  (SELECT AS STRUCT COUNTIF(event_name='purchase') AS purchase_events,
    COUNTIF(event_name='purchase' AND transaction_id IS NULL) AS unusable_transaction_events,
    COUNTIF(event_name='purchase' AND currency IS NULL) AS missing_or_invalid_currency_events,
    COUNTIF(event_name='purchase' AND ecommerce.purchase_revenue IS NULL) AS missing_purchase_revenue_events,
    COUNTIF(event_name='purchase' AND ecommerce.purchase_revenue_in_usd IS NULL) AS missing_usd_revenue_events,
    COUNTIF(event_name='purchase' AND item_rows=0) AS purchase_events_without_items,
    COUNTIF(event_name='purchase' AND item_revenue_nulls>0) AS purchase_events_with_missing_item_revenue,
    COUNTIF(event_name='purchase' AND item_quantity_nulls>0) AS purchase_events_with_missing_item_quantity,
    COUNTIF(event_name='purchase' AND ecommerce.purchase_revenue IS NOT NULL AND item_revenue IS NOT NULL
      AND ABS(ecommerce.purchase_revenue-item_revenue)>0.01) AS event_item_revenue_mismatches,
    COUNTIF(event_name='purchase' AND ecommerce.tax_value IS NOT NULL) AS purchase_events_with_tax,
    COUNTIF(event_name='purchase' AND ecommerce.shipping_value IS NOT NULL) AS purchase_events_with_shipping,
    COUNTIF(event_name='refund') AS refund_events
    FROM base) AS purchase_checks,
  (SELECT AS STRUCT COUNT(*) AS distinct_nonplaceholder_transaction_ids,
    COUNTIF(purchase_events>1) AS repeated_transaction_ids,
    COUNTIF(identity_variants>1) AS transaction_ids_with_identity_conflicts,
    COUNTIF(monetary_variants>1) AS transaction_ids_with_monetary_conflicts,
    SUM(purchase_events) AS events_with_nonplaceholder_transaction_id
    FROM transactions) AS transaction_checks,
  ARRAY(SELECT AS STRUCT currency,COUNT(*) AS purchase_events,
    COUNTIF(ecommerce.purchase_revenue IS NOT NULL) AS events_with_revenue,
    SUM(ecommerce.purchase_revenue) AS candidate_event_revenue,
    SUM(item_revenue) AS candidate_item_revenue
    FROM base WHERE event_name='purchase' GROUP BY currency ORDER BY currency) AS currency_checks,
  ARRAY(SELECT AS STRUCT device_category,COUNT(*) AS events
    FROM base GROUP BY device_category ORDER BY device_category) AS device_coverage
)) AS audit_json;
