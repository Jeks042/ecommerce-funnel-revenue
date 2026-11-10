-- Independent backward existence test from staged events, not stored forward-step flags.
WITH eligible AS (
 SELECT user_pseudo_id,session_id,session_device AS device,visit_date
 FROM `{{dataset}}.fact_visits` WHERE is_primary_eligible
), event_arrays AS (
 SELECT e.user_pseudo_id,e.session_id,
  ARRAY_AGG(IF(event_name='view_item',event_timestamp,NULL) IGNORE NULLS) AS views,
  ARRAY_AGG(IF(event_name='add_to_cart',event_timestamp,NULL) IGNORE NULLS) AS carts,
  ARRAY_AGG(IF(event_name='begin_checkout',event_timestamp,NULL) IGNORE NULLS) AS checkouts,
  MAX(IF(event_name='purchase',event_timestamp,NULL)) AS last_raw_purchase
 FROM `{{dataset}}.stg_events` e JOIN eligible USING(user_pseudo_id,session_id)
 WHERE event_name IN ('view_item','add_to_cart','begin_checkout','purchase')
 GROUP BY e.user_pseudo_id,e.session_id
), purchase_times AS (
 SELECT t.user_pseudo_id,t.session_id,COUNT(*) AS qualified_transactions,
  MAX(IF(unusable_purchase_times=0,first_purchase_ts,NULL)) AS last_qualified_first_time
 FROM `{{dataset}}.fact_transactions` t JOIN eligible USING(user_pseudo_id,session_id)
 GROUP BY t.user_pseudo_id,t.session_id
), final_steps AS (
 SELECT v.*,IFNULL(a.views,ARRAY<INT64>[]) AS views,IFNULL(a.carts,ARRAY<INT64>[]) AS carts,
  IFNULL(a.checkouts,ARRAY<INT64>[]) AS checkouts,
  IFNULL(p.qualified_transactions,0) AS qualified_transactions,
  (SELECT MAX(t) FROM UNNEST(a.carts) t) AS last_cart,
  (SELECT MAX(t) FROM UNNEST(a.checkouts) t) AS last_checkout,
  (SELECT MAX(t) FROM UNNEST(a.checkouts) t WHERE t<p.last_qualified_first_time) AS strict_purchase_checkout,
  (SELECT MAX(t) FROM UNNEST(a.checkouts) t WHERE t<=p.last_qualified_first_time) AS tied_purchase_checkout,
  (SELECT MAX(t) FROM UNNEST(a.checkouts) t WHERE t<a.last_raw_purchase) AS raw_purchase_checkout
 FROM eligible v LEFT JOIN event_arrays a USING(user_pseudo_id,session_id)
 LEFT JOIN purchase_times p USING(user_pseudo_id,session_id)
), earlier_carts AS (
 SELECT *,
  (SELECT MAX(t) FROM UNNEST(carts) t WHERE t<last_checkout) AS strict_checkout_cart,
  (SELECT MAX(t) FROM UNNEST(carts) t WHERE t<=last_checkout) AS tied_checkout_cart,
  (SELECT MAX(t) FROM UNNEST(carts) t WHERE t<strict_purchase_checkout) AS strict_purchase_cart,
  (SELECT MAX(t) FROM UNNEST(carts) t WHERE t<=tied_purchase_checkout) AS tied_purchase_cart,
  (SELECT MAX(t) FROM UNNEST(carts) t WHERE t<raw_purchase_checkout) AS raw_purchase_cart
 FROM final_steps
), flags AS (
 SELECT *,ARRAY_LENGTH(views)>0 AS entry,
  EXISTS(SELECT 1 FROM UNNEST(views) t WHERE t<last_cart) AS strict_cart,
  EXISTS(SELECT 1 FROM UNNEST(views) t WHERE t<=last_cart) AS tied_cart,
  EXISTS(SELECT 1 FROM UNNEST(views) t WHERE t<strict_checkout_cart) AS strict_checkout,
  EXISTS(SELECT 1 FROM UNNEST(views) t WHERE t<=tied_checkout_cart) AS tied_checkout,
  EXISTS(SELECT 1 FROM UNNEST(views) t WHERE t<strict_purchase_cart) AS strict_candidate,
  EXISTS(SELECT 1 FROM UNNEST(views) t WHERE t<=tied_purchase_cart) AS tied_candidate,
  EXISTS(SELECT 1 FROM UNNEST(views) t WHERE t<raw_purchase_cart) AS strict_raw_purchase
 FROM earlier_carts
)
SELECT TO_JSON_STRING(STRUCT(ARRAY(
 SELECT AS STRUCT visit_date,device,COUNT(*) AS sessions,COUNTIF(entry) AS entry_sessions,
  COUNTIF(strict_cart) AS strict_cart_sessions,COUNTIF(tied_cart) AS tied_cart_sessions,
  COUNTIF(strict_checkout) AS strict_checkout_sessions,COUNTIF(tied_checkout) AS tied_checkout_sessions,
  COUNTIF(strict_candidate) AS strict_candidate_sessions,COUNTIF(tied_candidate) AS tied_candidate_sessions,
  COUNTIF(strict_raw_purchase) AS strict_raw_purchase_sessions,
  COUNTIF(qualified_transactions>0) AS candidate_purchase_sessions,SUM(qualified_transactions) AS candidate_transactions
 FROM flags GROUP BY visit_date,device ORDER BY visit_date,device
) AS daily_independent)) AS audit_json;
