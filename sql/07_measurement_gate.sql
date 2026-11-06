-- GoogleSQL. Aggregate measurement acceptance checks; no source identifiers returned.
-- Confirm Sandbox and stop if validator estimate exceeds 3 GiB. No billing changes.
-- Purchase qualification ALWAYS uses the full 92 days, before selecting a cohort.
WITH source_rows AS (
  SELECT _TABLE_SUFFIX AS _TABLE_SUFFIX,event_date,event_timestamp,event_name,user_pseudo_id,
    device,traffic_source,ecommerce,items,event_params,event_bundle_sequence_id,
    event_previous_timestamp,event_server_timestamp_offset
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
), purchases AS (
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
  FROM source_rows
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
), raw AS (
  SELECT _TABLE_SUFFIX AS source_suffix,event_date,event_timestamp,event_name,user_pseudo_id,
    device.category AS device,traffic_source.source AS first_user_source,
    traffic_source.medium AS first_user_medium,event_bundle_sequence_id,
    event_previous_timestamp,event_server_timestamp_offset,ecommerce.transaction_id AS raw_transaction_id,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_entries,
    (SELECT COUNTIF(p.value.int_value IS NOT NULL) FROM UNNEST(event_params) p
      WHERE p.key='ga_session_id') AS sid_int_entries,
    (SELECT MAX(p.value.int_value) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_candidate
  FROM source_rows
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
  SELECT user_pseudo_id,session_id,COUNT(*) AS events,MIN(device) AS session_device,
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

), candidate_links AS (
  SELECT n.transaction_id,MIN(n.user_pseudo_id) AS user_pseudo_id,
    MIN(n.session_id) AS session_id,MIN(n.event_timestamp) AS first_purchase_ts,
    MAX(n.event_timestamp) AS last_purchase_ts,
    COUNTIF(n.event_timestamp IS NULL OR n.event_timestamp<=0
      OR SAFE.TIMESTAMP_MICROS(n.event_timestamp) IS NULL) AS unusable_purchase_times,
    MIN(p.events) AS recorded_events,LOGICAL_AND(p.native_complete_candidate) AS native_complete,
    LOGICAL_AND(p.native_item_agree_candidate) AS item_agree,
    MAX(p.candidate_native_amount) AS recorded_value
  FROM normalized n JOIN policies p USING(transaction_id)
  WHERE p.conservative_id_candidate GROUP BY n.transaction_id
), purchase_membership AS (
  SELECT n.user_pseudo_id,n.session_id,COUNT(*) AS raw_purchase_events,
    COUNTIF(n.transaction_id IS NULL) AS missing_id_events,
    COUNTIF(n.transaction_id IS NOT NULL AND NOT p.conservative_id_candidate) AS rejected_id_events,
    COUNTIF(p.conservative_id_candidate) AS candidate_events
  FROM normalized n LEFT JOIN policies p USING(transaction_id)
  GROUP BY n.user_pseudo_id,n.session_id
), linked_outcomes AS (
  SELECT c.user_pseudo_id,c.session_id,COUNT(*) AS candidate_transactions,
    COUNTIF(c.native_complete) AS native_complete_transactions,
    COUNTIF(c.item_agree) AS agreeing_transactions,
    SUM(IF(c.item_agree,c.recorded_value,NULL)) AS agreeing_recorded_value,
    COUNTIF(c.unusable_purchase_times=0 AND c.first_purchase_ts>s.strict_checkout) AS strict_transactions,
    COUNTIF(c.unusable_purchase_times=0 AND c.last_purchase_ts>s.strict_checkout) AS last_time_transactions,
    COUNTIF(c.unusable_purchase_times=0 AND c.first_purchase_ts>=s.tied_checkout) AS tied_transactions
  FROM candidate_links c JOIN purchase_step s USING(user_pseudo_id,session_id)
  GROUP BY c.user_pseudo_id,c.session_id
), gate_sessions AS (
  SELECT s.*,FORMAT_TIMESTAMP('%Y%m',SAFE.TIMESTAMP_MICROS(s.first_ts),'UTC') AS cohort_month,
    IFNULL(m.missing_id_events,0) AS missing_id_events,
    IFNULL(m.rejected_id_events,0) AS rejected_id_events,
    IFNULL(m.candidate_events,0) AS candidate_events,
    IFNULL(o.candidate_transactions,0) AS candidate_transactions,
    IFNULL(o.native_complete_transactions,0) AS native_complete_transactions,
    IFNULL(o.agreeing_transactions,0) AS agreeing_transactions,
    o.agreeing_recorded_value,
    IFNULL(o.strict_transactions,0) AS strict_transactions,
    IFNULL(o.last_time_transactions,0) AS last_time_transactions,
    IFNULL(o.tied_transactions,0) AS tied_transactions
  FROM purchase_step s LEFT JOIN purchase_membership m USING(user_pseudo_id,session_id)
  LEFT JOIN linked_outcomes o USING(user_pseudo_id,session_id)
), gate_scopes AS (
  SELECT s.*,p.scope FROM gate_sessions s CROSS JOIN UNNEST([
    STRUCT('all_keyed' AS scope,TRUE AS include_scope),
    STRUCT('anchored_interior',anchored_candidate AND NOT touches_window_edge),
    STRUCT('anchored_interior_single_date',anchored_candidate AND NOT touches_window_edge AND observed_dates=1)
  ]) p WHERE p.include_scope
), scope_summary AS (
  SELECT scope,cohort_month,session_device,COUNT(*) AS sessions,
    COUNTIF(first_view IS NOT NULL) AS entry_sessions,
    COUNTIF(strict_cart IS NOT NULL) AS strict_cart_sessions,
    COUNTIF(strict_checkout IS NOT NULL) AS strict_checkout_sessions,
    COUNTIF(purchase_events>0) AS raw_purchase_sessions,
    COUNTIF(candidate_transactions>0) AS candidate_purchase_sessions,
    COUNTIF(strict_transactions>0) AS strict_candidate_sessions,
    COUNTIF(last_time_transactions>0) AS last_time_candidate_sessions,
    COUNTIF(tied_transactions>0) AS tied_candidate_sessions,
    SUM(purchase_events) AS raw_purchase_events,SUM(missing_id_events) AS missing_id_events,
    SUM(rejected_id_events) AS rejected_id_events,SUM(candidate_events) AS candidate_events,
    SUM(candidate_transactions) AS candidate_transactions,
    SUM(native_complete_transactions) AS native_complete_transactions,
    SUM(agreeing_transactions) AS agreeing_transactions,
    SUM(agreeing_recorded_value) AS agreeing_recorded_value,
    COUNTIF(missing_id_events+rejected_id_events>0) AS unresolved_purchase_sessions,
    COUNTIF(candidate_transactions>0 AND missing_id_events+rejected_id_events>0) AS mixed_outcome_sessions,
    COUNTIF(last_ts-first_ts>86400000000) AS long_sessions
  FROM gate_scopes GROUP BY scope,cohort_month,session_device
), purchase_coverage AS (
  SELECT n.source_suffix,n.device,COUNT(*) AS raw_purchase_events,
    COUNTIF(n.transaction_id IS NULL) AS missing_id_events,
    COUNTIF(n.transaction_id IS NOT NULL AND NOT p.conservative_id_candidate) AS rejected_id_events,
    COUNTIF(p.conservative_id_candidate) AS candidate_events,
    COUNT(DISTINCT IF(p.conservative_id_candidate,n.transaction_id,NULL)) AS candidate_transactions,
    COUNT(DISTINCT IF(p.native_item_agree_candidate,n.transaction_id,NULL)) AS agreeing_transactions
  FROM normalized n LEFT JOIN policies p USING(transaction_id)
  GROUP BY n.source_suffix,n.device
)
SELECT TO_JSON_STRING(STRUCT(
  (SELECT AS STRUCT COUNT(*) AS keyed_sessions,SUM(events) AS keyed_events,
    SUM(purchase_events) AS keyed_purchase_events,SUM(candidate_events) AS candidate_events,
    SUM(candidate_transactions) AS linked_candidate_transactions,
    SUM(agreeing_transactions) AS linked_agreeing_transactions,
    SUM(agreeing_recorded_value) AS linked_agreeing_recorded_value,
    SUM(missing_id_events) AS missing_id_events,SUM(rejected_id_events) AS rejected_id_events
    FROM gate_sessions) AS linkage,
  (SELECT AS STRUCT COUNT(*) AS candidate_transactions,COUNTIF(native_complete) AS native_complete_transactions,
    COUNTIF(item_agree) AS agreeing_transactions,SUM(IF(item_agree,recorded_value,NULL)) AS agreeing_recorded_value,
    SUM(recorded_events) AS candidate_events FROM candidate_links) AS candidates,
  (SELECT AS STRUCT COUNT(*) AS sessions,SUM(events) AS events,SUM(purchase_events) AS raw_purchase_events,
    SUM(candidate_transactions) AS candidate_transactions,
    COUNTIF(anchored_candidate) AS anchored_sessions,
    COUNTIF(observed_dates=1) AS single_date_sessions,
    MIN((last_ts-first_ts)/3600000000.0) AS minimum_span_hours,
    MAX((last_ts-first_ts)/3600000000.0) AS maximum_span_hours
    FROM gate_sessions WHERE last_ts-first_ts>86400000000) AS long_span_review,
  ARRAY(SELECT AS STRUCT * FROM scope_summary ORDER BY scope,cohort_month,session_device) AS scopes,
  ARRAY(SELECT AS STRUCT * FROM purchase_coverage ORDER BY source_suffix,device) AS purchase_coverage
)) AS audit_json;
