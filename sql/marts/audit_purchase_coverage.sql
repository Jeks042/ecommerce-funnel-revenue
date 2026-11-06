SELECT n.source_date,n.device,COUNT(*) AS raw_purchase_events,
  COUNTIF(n.transaction_id IS NULL) AS missing_id_events,
  COUNTIF(n.transaction_id IS NOT NULL AND NOT p.conservative_id_candidate) AS rejected_id_events,
  COUNTIF(p.conservative_id_candidate) AS candidate_events,
  COUNT(DISTINCT IF(p.conservative_id_candidate,n.transaction_id,NULL)) AS candidate_transactions,
  COUNT(DISTINCT IF(p.native_item_agree_candidate,n.transaction_id,NULL)) AS agreeing_transactions
FROM `{{dataset}}.stg_events` n LEFT JOIN `{{dataset}}.transaction_policy` p USING(transaction_id)
WHERE n.event_name='purchase'
GROUP BY n.source_date,n.device
