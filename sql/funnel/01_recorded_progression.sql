-- GoogleSQL. Read-only reviewed aggregates; measurement contract v1.
-- Qualify purchases over the full source before December cohort selection.
WITH scopes AS (
 SELECT v.*,p.scope FROM `{{dataset}}.fact_visits` v CROSS JOIN UNNEST([
 STRUCT('all_keyed' AS scope,TRUE AS included),
 STRUCT('anchored_interior',is_anchored_interior),
 STRUCT('primary',is_primary_eligible)
 ]) p WHERE cohort_month='202012' AND p.included
), daily_device AS (
 SELECT scope,visit_date,session_device AS device,
COUNT(*) AS sessions,
COUNTIF(first_view IS NOT NULL) AS entry_sessions,
COUNTIF(strict_cart IS NOT NULL) AS strict_cart_sessions,
COUNTIF(strict_checkout IS NOT NULL) AS strict_checkout_sessions,
COUNTIF(strict_transactions>0) AS strict_candidate_sessions,
COUNTIF(tied_cart IS NOT NULL) AS tied_cart_sessions,
COUNTIF(tied_checkout IS NOT NULL) AS tied_checkout_sessions,
COUNTIF(tied_transactions>0) AS tied_candidate_sessions,
COUNTIF(strict_purchase IS NOT NULL) AS strict_raw_purchase_sessions,
COUNTIF(tied_purchase IS NOT NULL) AS tied_raw_purchase_sessions,
COUNTIF(view_events>0 AND cart_events>0) AS unordered_cart_sessions,
COUNTIF(view_events>0 AND cart_events>0 AND checkout_events>0) AS unordered_checkout_sessions,
COUNTIF(view_events>0 AND cart_events>0 AND checkout_events>0 AND candidate_transactions>0) AS unordered_candidate_sessions,
COUNTIF(candidate_transactions>0) AS candidate_purchase_sessions,
SUM(candidate_transactions) AS candidate_transactions,
SUM(purchase_events) AS raw_purchase_events,
SUM(missing_id_events) AS missing_id_events,SUM(rejected_id_events) AS rejected_id_events,
COUNTIF(missing_id_events+rejected_id_events>0) AS unresolved_sessions,
COUNTIF(first_view IS NOT NULL AND missing_id_events+rejected_id_events>0) AS entry_unresolved_sessions,
COUNTIF(strict_checkout IS NOT NULL AND missing_id_events+rejected_id_events>0) AS checkout_unresolved_sessions,
COUNTIF(candidate_transactions>0 AND missing_id_events+rejected_id_events>0) AS mixed_outcome_sessions,
COUNTIF(strict_purchase IS NOT NULL AND strict_transactions=0) AS raw_only_completion_sessions,
COUNTIF(strict_purchase IS NOT NULL AND strict_transactions=0 AND missing_id_events+rejected_id_events>0) AS raw_only_with_unresolved_ids_sessions
 FROM scopes GROUP BY scope,visit_date,device
), context_summary AS (
 SELECT first_user_source,first_user_medium,
 first_user_source IS NOT NULL AND first_user_medium IS NOT NULL AND LOWER(TRIM(first_user_source)) NOT IN ('','<other>','(not set)') AND LOWER(TRIM(first_user_medium)) NOT IN ('','<other>','(not set)') AS interpretable_context,
COUNT(*) AS sessions,
COUNTIF(first_view IS NOT NULL) AS entry_sessions,
COUNTIF(strict_cart IS NOT NULL) AS strict_cart_sessions,
COUNTIF(strict_checkout IS NOT NULL) AS strict_checkout_sessions,
COUNTIF(strict_transactions>0) AS strict_candidate_sessions,
COUNTIF(tied_cart IS NOT NULL) AS tied_cart_sessions,
COUNTIF(tied_checkout IS NOT NULL) AS tied_checkout_sessions,
COUNTIF(tied_transactions>0) AS tied_candidate_sessions,
COUNTIF(strict_purchase IS NOT NULL) AS strict_raw_purchase_sessions,
COUNTIF(tied_purchase IS NOT NULL) AS tied_raw_purchase_sessions,
COUNTIF(view_events>0 AND cart_events>0) AS unordered_cart_sessions,
COUNTIF(view_events>0 AND cart_events>0 AND checkout_events>0) AS unordered_checkout_sessions,
COUNTIF(view_events>0 AND cart_events>0 AND checkout_events>0 AND candidate_transactions>0) AS unordered_candidate_sessions,
COUNTIF(candidate_transactions>0) AS candidate_purchase_sessions,
SUM(candidate_transactions) AS candidate_transactions,
SUM(purchase_events) AS raw_purchase_events,
SUM(missing_id_events) AS missing_id_events,SUM(rejected_id_events) AS rejected_id_events,
COUNTIF(missing_id_events+rejected_id_events>0) AS unresolved_sessions,
COUNTIF(first_view IS NOT NULL AND missing_id_events+rejected_id_events>0) AS entry_unresolved_sessions,
COUNTIF(strict_checkout IS NOT NULL AND missing_id_events+rejected_id_events>0) AS checkout_unresolved_sessions,
COUNTIF(candidate_transactions>0 AND missing_id_events+rejected_id_events>0) AS mixed_outcome_sessions,
COUNTIF(strict_purchase IS NOT NULL AND strict_transactions=0) AS raw_only_completion_sessions,
COUNTIF(strict_purchase IS NOT NULL AND strict_transactions=0 AND missing_id_events+rejected_id_events>0) AS raw_only_with_unresolved_ids_sessions
 FROM scopes WHERE scope='primary' GROUP BY first_user_source,first_user_medium
), admitted_contexts AS (
 -- Fixed size rules; select by entry volume, never by highest observed conversion.
 SELECT first_user_source,first_user_medium FROM context_summary
 WHERE interpretable_context AND entry_sessions>=500 AND strict_candidate_sessions>=30
 AND entry_sessions-strict_candidate_sessions>=30
 ORDER BY entry_sessions DESC,first_user_source,first_user_medium LIMIT 2
), daily_context AS (
 SELECT visit_date,first_user_source,first_user_medium,
COUNT(*) AS sessions,
COUNTIF(first_view IS NOT NULL) AS entry_sessions,
COUNTIF(strict_cart IS NOT NULL) AS strict_cart_sessions,
COUNTIF(strict_checkout IS NOT NULL) AS strict_checkout_sessions,
COUNTIF(strict_transactions>0) AS strict_candidate_sessions,
COUNTIF(tied_cart IS NOT NULL) AS tied_cart_sessions,
COUNTIF(tied_checkout IS NOT NULL) AS tied_checkout_sessions,
COUNTIF(tied_transactions>0) AS tied_candidate_sessions,
COUNTIF(strict_purchase IS NOT NULL) AS strict_raw_purchase_sessions,
COUNTIF(tied_purchase IS NOT NULL) AS tied_raw_purchase_sessions,
COUNTIF(view_events>0 AND cart_events>0) AS unordered_cart_sessions,
COUNTIF(view_events>0 AND cart_events>0 AND checkout_events>0) AS unordered_checkout_sessions,
COUNTIF(view_events>0 AND cart_events>0 AND checkout_events>0 AND candidate_transactions>0) AS unordered_candidate_sessions,
COUNTIF(candidate_transactions>0) AS candidate_purchase_sessions,
SUM(candidate_transactions) AS candidate_transactions,
SUM(purchase_events) AS raw_purchase_events,
SUM(missing_id_events) AS missing_id_events,SUM(rejected_id_events) AS rejected_id_events,
COUNTIF(missing_id_events+rejected_id_events>0) AS unresolved_sessions,
COUNTIF(first_view IS NOT NULL AND missing_id_events+rejected_id_events>0) AS entry_unresolved_sessions,
COUNTIF(strict_checkout IS NOT NULL AND missing_id_events+rejected_id_events>0) AS checkout_unresolved_sessions,
COUNTIF(candidate_transactions>0 AND missing_id_events+rejected_id_events>0) AS mixed_outcome_sessions,
COUNTIF(strict_purchase IS NOT NULL AND strict_transactions=0) AS raw_only_completion_sessions,
COUNTIF(strict_purchase IS NOT NULL AND strict_transactions=0 AND missing_id_events+rejected_id_events>0) AS raw_only_with_unresolved_ids_sessions
 FROM scopes JOIN admitted_contexts USING(first_user_source,first_user_medium)
 WHERE scope='primary' GROUP BY visit_date,first_user_source,first_user_medium
)
SELECT TO_JSON_STRING(STRUCT(
 ARRAY(SELECT AS STRUCT * FROM daily_device ORDER BY scope,visit_date,device) AS daily_device,
 ARRAY(SELECT AS STRUCT * FROM context_summary ORDER BY entry_sessions DESC,first_user_source,first_user_medium) AS context_summary,
 ARRAY(SELECT AS STRUCT * FROM daily_context ORDER BY visit_date,first_user_source,first_user_medium) AS daily_context,
 ARRAY(SELECT AS STRUCT * FROM admitted_contexts ORDER BY first_user_source,first_user_medium) AS admitted_contexts,
 ARRAY(SELECT AS STRUCT * FROM (
SELECT 'stg_events' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.stg_events` t
UNION ALL
SELECT 'fact_transactions' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.fact_transactions` t
UNION ALL
SELECT 'fact_visits' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.fact_visits` t
 )) AS input_fingerprints
)) AS audit_json;
