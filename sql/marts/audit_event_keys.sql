SELECT source_date,device,
  CASE WHEN NOT IFNULL(user_key_usable,FALSE) THEN 'unusable_user_key'
    WHEN session_id IS NULL THEN 'unusable_session_key' ELSE 'keyed_event' END AS key_status,
  COUNT(*) AS events,COUNTIF(event_name='purchase') AS purchase_events
FROM `{{dataset}}.stg_events`
GROUP BY source_date,device,key_status
