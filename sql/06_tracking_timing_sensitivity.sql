-- GoogleSQL. Read-only measurement diagnostics; raw purchase events are not orders.
-- Confirm Sandbox; inspect validator estimate and stop above the 3 GiB review ceiling.
WITH raw AS (
  SELECT _TABLE_SUFFIX AS source_suffix,event_date,event_timestamp,event_name,user_pseudo_id,
    device.category AS device,traffic_source.source AS first_user_source,
    traffic_source.medium AS first_user_medium,event_bundle_sequence_id,
    event_previous_timestamp,event_server_timestamp_offset,ecommerce.transaction_id AS raw_transaction_id,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_entries,
    (SELECT COUNTIF(p.value.int_value IS NOT NULL) FROM UNNEST(event_params) p
      WHERE p.key='ga_session_id') AS sid_int_entries,
    (SELECT MAX(p.value.int_value) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_candidate
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
), base AS (
  SELECT *,CASE WHEN sid_entries=1 AND sid_int_entries=1 AND sid_candidate>0
      THEN sid_candidate END AS session_id,
    NULLIF(TRIM(user_pseudo_id),'') IS NOT NULL
      AND TRIM(user_pseudo_id) NOT IN ('<Other>','(not set)') AS user_key_usable,
    CASE WHEN NULLIF(TRIM(raw_transaction_id),'') IS NOT NULL
      AND TRIM(raw_transaction_id) NOT IN ('<Other>','(not set)') THEN TRIM(raw_transaction_id) END AS transaction_id,
    event_timestamp IS NOT NULL AND event_timestamp>0
      AND SAFE.TIMESTAMP_MICROS(event_timestamp) IS NOT NULL AS timestamp_usable
  FROM raw
), keyed AS (
  SELECT * FROM base WHERE user_key_usable AND session_id IS NOT NULL
), sessions AS (
  SELECT user_pseudo_id,session_id,COUNT(*) AS events,
    COUNT(DISTINCT source_suffix) AS observed_dates,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(device))) AS device_variants,
    COUNT(DISTINCT TO_JSON_STRING(STRUCT(first_user_source,first_user_medium))) AS context_variants,
    COUNTIF(NOT timestamp_usable) AS unusable_timestamp_events,
    COUNTIF(event_date IS NULL OR source_suffix!=event_date
      OR FORMAT_TIMESTAMP('%Y%m%d',SAFE.TIMESTAMP_MICROS(event_timestamp),'UTC')!=event_date)
      AS date_inconsistent_events,
    MIN(IF(timestamp_usable,event_timestamp,NULL)) AS first_ts,
    MAX(IF(timestamp_usable,event_timestamp,NULL)) AS last_ts,
    COUNTIF(event_name='session_start') AS start_events,
    COUNT(DISTINCT IF(event_name='session_start',event_timestamp,NULL)) AS start_timestamps,
    MIN(IF(event_name='session_start' AND timestamp_usable,event_timestamp,NULL)) AS start_ts,
    COUNTIF(event_name='view_item') AS view_events,
    COUNTIF(event_name='add_to_cart') AS cart_events,
    COUNTIF(event_name='begin_checkout') AS checkout_events,
    COUNTIF(event_name='purchase') AS purchase_events,
    COUNTIF(event_name='purchase' AND transaction_id IS NOT NULL) AS usable_id_purchase_events,
    LOGICAL_OR(source_suffix IN ('20201101','20210131')) AS touches_window_edge,
    MIN(IF(event_name='view_item' AND timestamp_usable,event_timestamp,NULL)) AS first_view,
    IFNULL(ARRAY_AGG(IF(event_name='add_to_cart' AND timestamp_usable,event_timestamp,NULL)
      IGNORE NULLS),ARRAY<INT64>[]) AS cart_times,
    IFNULL(ARRAY_AGG(IF(event_name='begin_checkout' AND timestamp_usable,event_timestamp,NULL)
      IGNORE NULLS),ARRAY<INT64>[]) AS checkout_times,
    IFNULL(ARRAY_AGG(IF(event_name='purchase' AND timestamp_usable,event_timestamp,NULL)
      IGNORE NULLS),ARRAY<INT64>[]) AS purchase_times
  FROM keyed GROUP BY user_pseudo_id,session_id
), cart_step AS (
  SELECT *,
    (SELECT MIN(t) FROM UNNEST(cart_times) t WHERE t>first_view) AS strict_cart,
    (SELECT MIN(t) FROM UNNEST(cart_times) t WHERE t>=first_view) AS tied_cart
  FROM sessions
), checkout_step AS (
  SELECT *,
    (SELECT MIN(t) FROM UNNEST(checkout_times) t WHERE t>strict_cart) AS strict_checkout,
    (SELECT MIN(t) FROM UNNEST(checkout_times) t WHERE t>=tied_cart) AS tied_checkout
  FROM cart_step
), purchase_step AS (
  SELECT *,
    (SELECT MIN(t) FROM UNNEST(purchase_times) t WHERE t>strict_checkout) AS strict_purchase,
    (SELECT MIN(t) FROM UNNEST(purchase_times) t WHERE t>=tied_checkout) AS tied_purchase,
    start_events=1 AND start_ts=first_ts AND unusable_timestamp_events=0
      AND date_inconsistent_events=0 AND device_variants=1 AND context_variants=1 AS anchored_candidate
  FROM checkout_step
), scope_rows AS (
  SELECT s.*,p.scope FROM purchase_step s CROSS JOIN UNNEST([
    STRUCT('all_keyed' AS scope,TRUE AS include_scope),
    STRUCT('all_keyed_interior',NOT touches_window_edge),
    STRUCT('one_start',start_events=1),
    STRUCT('anchored_candidate',anchored_candidate),
    STRUCT('anchored_candidate_interior',anchored_candidate AND NOT touches_window_edge),
    STRUCT('anchored_candidate_interior_single_date',anchored_candidate AND NOT touches_window_edge AND observed_dates=1)
  ]) p WHERE p.include_scope
), timestamp_groups AS (
  SELECT user_pseudo_id,session_id,event_timestamp,COUNT(*) AS events,
    COUNT(DISTINCT event_name) AS step_types,
    COUNTIF(event_bundle_sequence_id IS NOT NULL) AS populated_bundles,
    COUNT(DISTINCT event_bundle_sequence_id) AS bundle_variants,
    COUNTIF(event_previous_timestamp IS NOT NULL AND event_previous_timestamp>0) AS populated_positive_previous,
    COUNTIF(event_server_timestamp_offset IS NOT NULL) AS populated_offsets
  FROM keyed WHERE event_name IN ('view_item','add_to_cart','begin_checkout','purchase')
  GROUP BY user_pseudo_id,session_id,event_timestamp
), daily AS (
  SELECT source_suffix,device,COUNT(*) AS events,
    COUNTIF(NOT user_key_usable OR session_id IS NULL) AS ineligible_key_events,
    COUNTIF(event_name='page_view') AS page_view_events,
    COUNTIF(event_name='session_start') AS start_events,
    COUNTIF(event_name='view_item') AS view_events,
    COUNTIF(event_name='add_to_cart') AS cart_events,
    COUNTIF(event_name='begin_checkout') AS checkout_events,
    COUNTIF(event_name='purchase') AS purchase_events,
    COUNTIF(event_name='purchase' AND transaction_id IS NOT NULL) AS usable_id_purchase_events
  FROM base GROUP BY source_suffix,device
)
SELECT TO_JSON_STRING(STRUCT(
  (SELECT AS STRUCT COUNT(*) AS events,COUNT(DISTINCT source_suffix) AS source_days,
    COUNTIF(NOT user_key_usable OR session_id IS NULL) AS ineligible_key_events,
    COUNTIF(NOT timestamp_usable) AS unusable_timestamp_events FROM base) AS population,
  (SELECT AS STRUCT COUNT(*) AS keyed_sessions,COUNTIF(observed_dates>1) AS cross_date_sessions,
    COUNTIF(start_events=0) AS without_start,COUNTIF(start_events>1) AS repeated_starts,
    COUNTIF(start_events>1 AND start_timestamps=1) AS repeated_start_same_timestamp,
    COUNTIF(start_events=1 AND start_ts!=first_ts) AS single_start_after_first_event,
    COUNTIF(touches_window_edge) AS edge_sessions,
    COUNTIF(device_variants>1) AS multiple_device_sessions,
    COUNTIF(context_variants>1) AS multiple_first_user_context_sessions,
    COUNTIF(last_ts-first_ts>86400000000) AS observed_spans_over_24_hours,
    COUNTIF(SAFE.TIMESTAMP_SECONDS(session_id) IS NULL) AS invalid_sid_timestamp_sessions,
    COUNTIF(ABS(SAFE_SUBTRACT(first_ts,SAFE_MULTIPLY(session_id,1000000)))>60000000)
      AS sid_first_event_diff_over_60_seconds,
    APPROX_QUANTILES(SAFE_DIVIDE(last_ts-first_ts,1000000),100)[OFFSET(50)] AS median_observed_span_seconds,
    APPROX_QUANTILES(SAFE_DIVIDE(last_ts-first_ts,1000000),100)[OFFSET(95)] AS p95_observed_span_seconds
    FROM sessions) AS session_checks,
  ARRAY(SELECT AS STRUCT scope,COUNT(*) AS sessions,SUM(events) AS events,
    COUNTIF(view_events>0) AS view_sessions,COUNTIF(cart_events>0) AS cart_sessions,
    COUNTIF(checkout_events>0) AS checkout_sessions,COUNTIF(purchase_events>0) AS raw_purchase_sessions,
    SUM(purchase_events) AS raw_purchase_events,SUM(usable_id_purchase_events) AS usable_id_purchase_events,
    COUNTIF(view_events>0 AND cart_events>0 AND checkout_events>0 AND purchase_events>0) AS unordered_all_steps,
    COUNTIF(strict_cart IS NOT NULL) AS strict_cart_sessions,
    COUNTIF(strict_checkout IS NOT NULL) AS strict_checkout_sessions,
    COUNTIF(strict_purchase IS NOT NULL) AS strict_raw_purchase_sessions,
    COUNTIF(tied_cart IS NOT NULL) AS tied_cart_sessions,
    COUNTIF(tied_checkout IS NOT NULL) AS tied_checkout_sessions,
    COUNTIF(tied_purchase IS NOT NULL) AS tied_raw_purchase_sessions
    FROM scope_rows GROUP BY scope ORDER BY scope) AS scope_sensitivity,
  (SELECT AS STRUCT COUNTIF(step_types>1) AS mixed_step_timestamp_groups,
    COUNTIF(step_types>1 AND populated_bundles=events) AS mixed_groups_all_bundles_populated,
    COUNTIF(step_types>1 AND bundle_variants>1) AS mixed_groups_different_bundles,
    COUNTIF(step_types>1 AND populated_positive_previous=events) AS mixed_groups_all_positive_previous,
    COUNTIF(step_types>1 AND populated_offsets=events) AS mixed_groups_all_offsets_populated
    FROM timestamp_groups) AS tie_checks,
  ARRAY(SELECT AS STRUCT event_name,COUNT(*) AS events,
    COUNTIF(event_bundle_sequence_id IS NOT NULL) AS bundle_populated,
    COUNTIF(event_previous_timestamp IS NOT NULL) AS previous_populated,
    COUNTIF(event_previous_timestamp>0) AS previous_positive,
    COUNTIF(event_previous_timestamp>=event_timestamp AND event_previous_timestamp>0) AS previous_not_before_current,
    COUNTIF(event_server_timestamp_offset IS NOT NULL) AS offset_populated,
    COUNTIF(event_server_timestamp_offset!=0) AS offset_nonzero
    FROM keyed WHERE event_name IN ('view_item','add_to_cart','begin_checkout','purchase')
    GROUP BY event_name ORDER BY event_name) AS ordering_field_coverage,
  ARRAY(SELECT AS STRUCT * FROM daily ORDER BY source_suffix,device) AS daily_device_coverage
)) AS audit_json;
