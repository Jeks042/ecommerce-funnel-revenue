WITH keyed AS (
  SELECT * FROM `{{dataset}}.stg_events` WHERE user_key_usable AND session_id IS NOT NULL
), sessions AS (
  SELECT user_pseudo_id,session_id,COUNT(*) AS events,MIN(device) AS session_device,MIN(first_user_source) AS first_user_source,MIN(first_user_medium) AS first_user_medium,
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
      IGNORE NULLS ORDER BY event_timestamp),ARRAY<INT64>[]) AS cart_times,
    IFNULL(ARRAY_AGG(IF(event_name='begin_checkout' AND timestamp_usable,event_timestamp,NULL)
      IGNORE NULLS ORDER BY event_timestamp),ARRAY<INT64>[]) AS checkout_times,
    IFNULL(ARRAY_AGG(IF(event_name='purchase' AND timestamp_usable,event_timestamp,NULL)
      IGNORE NULLS ORDER BY event_timestamp),ARRAY<INT64>[]) AS purchase_times
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

), purchase_membership AS (
  SELECT n.user_pseudo_id,n.session_id,COUNT(*) AS raw_purchase_events,
    COUNTIF(n.transaction_id IS NULL) AS missing_id_events,
    COUNTIF(n.transaction_id IS NOT NULL AND NOT p.conservative_id_candidate) AS rejected_id_events,
    COUNTIF(p.conservative_id_candidate) AS candidate_events
  FROM `{{dataset}}.stg_events` n LEFT JOIN `{{dataset}}.transaction_policy` p USING(transaction_id)
  WHERE n.event_name='purchase' GROUP BY n.user_pseudo_id,n.session_id
), linked_outcomes AS (
  SELECT c.user_pseudo_id,c.session_id,COUNT(*) AS candidate_transactions,
    COUNTIF(c.native_complete) AS native_complete_transactions,
    COUNTIF(c.item_agree) AS agreeing_transactions,
    SUM(c.supported_recorded_value) AS agreeing_recorded_value,
    COUNTIF(c.unusable_purchase_times=0 AND c.first_purchase_ts>s.strict_checkout) AS strict_transactions,
    COUNTIF(c.unusable_purchase_times=0 AND c.last_purchase_ts>s.strict_checkout) AS last_time_transactions,
    COUNTIF(c.unusable_purchase_times=0 AND c.first_purchase_ts>=s.tied_checkout) AS tied_transactions
  FROM `{{dataset}}.fact_transactions` c JOIN purchase_step s USING(user_pseudo_id,session_id)
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
)
SELECT *,DATE(SAFE.TIMESTAMP_MICROS(first_ts),'UTC') AS visit_date,
  anchored_candidate AND NOT touches_window_edge AS is_anchored_interior,
  anchored_candidate AND NOT touches_window_edge AND observed_dates=1 AND cohort_month='202012' AS is_primary_eligible,
  CASE WHEN start_events=0 THEN 'without_start'
    WHEN start_events>1 THEN 'repeated_start'
    WHEN start_ts IS NULL OR start_ts!=first_ts THEN 'start_not_first'
    WHEN unusable_timestamp_events>0 THEN 'unusable_timestamp'
    WHEN date_inconsistent_events>0 THEN 'date_inconsistent'
    WHEN device_variants!=1 THEN 'mixed_device'
    WHEN context_variants!=1 THEN 'mixed_first_user_context'
    WHEN touches_window_edge THEN 'source_edge'
    WHEN observed_dates!=1 THEN 'cross_date'
    WHEN cohort_month IS NULL OR cohort_month!='202012' THEN 'outside_primary_month'
    ELSE 'eligible_primary' END AS exclusion_reason
FROM gate_sessions
