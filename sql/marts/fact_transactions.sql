-- Only IDs whose globally compared payloads agree. One row per qualified ID.
SELECT n.transaction_id,MIN(n.user_pseudo_id) AS user_pseudo_id,MIN(n.session_id) AS session_id,
  MIN(n.event_timestamp) AS first_purchase_ts,MAX(n.event_timestamp) AS last_purchase_ts,
  MIN(n.source_date) AS purchase_date,MIN(n.device) AS device,
  COUNT(*) AS recorded_events,
  COUNTIF(NOT n.timestamp_usable) AS unusable_purchase_times,
  LOGICAL_AND(p.native_complete_candidate) AS native_complete,
  LOGICAL_AND(p.native_item_agree_candidate) AS item_agree,
  IF(LOGICAL_AND(p.native_item_agree_candidate),MAX(p.candidate_native_amount),NULL) AS supported_recorded_value,
  -- Sorted arrays are identical for qualified groups, including repeated rows.
  ANY_VALUE(ARRAY(SELECT AS STRUCT i.* FROM UNNEST(n.items) i ORDER BY TO_JSON_STRING(i))) AS items
FROM `{{dataset}}.stg_events` n JOIN `{{dataset}}.transaction_policy` p USING(transaction_id)
WHERE n.event_name='purchase' AND p.conservative_id_candidate
GROUP BY n.transaction_id
