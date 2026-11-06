WITH gate_scopes AS (
  SELECT s.*,p.scope FROM `{{dataset}}.fact_visits` s CROSS JOIN UNNEST([
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
), checks AS (
  SELECT 'unique_visit_key' AS check_name,COUNT(*)=COUNT(DISTINCT TO_JSON_STRING(STRUCT(user_pseudo_id,session_id))) AS passed FROM `{{dataset}}.fact_visits`
  UNION ALL SELECT 'unique_transaction_id',COUNT(*)=COUNT(DISTINCT transaction_id) FROM `{{dataset}}.fact_transactions`
  UNION ALL SELECT 'unique_policy_id',COUNT(*)=COUNT(DISTINCT transaction_id) FROM `{{dataset}}.transaction_policy`
  UNION ALL SELECT 'unique_item_occurrence',COUNT(*)=COUNT(DISTINCT TO_JSON_STRING(STRUCT(transaction_id,item_row_number))) FROM `{{dataset}}.fact_transaction_items`
  UNION ALL SELECT 'event_key_partition',(SELECT SUM(events) FROM `{{dataset}}.audit_event_keys`)=(SELECT COUNT(*) FROM `{{dataset}}.stg_events`)
  UNION ALL SELECT 'keyed_events_to_visits',(SELECT SUM(events) FROM `{{dataset}}.fact_visits`)=(SELECT COUNT(*) FROM `{{dataset}}.stg_events` WHERE user_key_usable AND session_id IS NOT NULL)
  UNION ALL SELECT 'visit_exclusion_partition',(SELECT SUM(visits) FROM `{{dataset}}.audit_visit_exclusions`)=(SELECT COUNT(*) FROM `{{dataset}}.fact_visits`)
  UNION ALL SELECT 'missing_purchase_id_conservation',(SELECT SUM(missing_id_events) FROM `{{dataset}}.audit_purchase_coverage`)=(SELECT COUNT(*) FROM `{{dataset}}.stg_events` WHERE event_name='purchase' AND transaction_id IS NULL)
  UNION ALL SELECT 'policy_event_partition',(SELECT SUM(events) FROM `{{dataset}}.transaction_policy`)=(SELECT COUNT(*) FROM `{{dataset}}.stg_events` WHERE event_name='purchase' AND transaction_id IS NOT NULL)
  UNION ALL SELECT 'purchase_coverage_partition',COUNTIF(raw_purchase_events!=missing_id_events+rejected_id_events+candidate_events)=0 FROM `{{dataset}}.audit_purchase_coverage`
  UNION ALL SELECT 'purchase_coverage_complete',(SELECT SUM(raw_purchase_events) FROM `{{dataset}}.audit_purchase_coverage`)=(SELECT COUNT(*) FROM `{{dataset}}.stg_events` WHERE event_name='purchase')
  UNION ALL SELECT 'qualified_policy_count',(SELECT COUNT(*) FROM `{{dataset}}.fact_transactions`)=(SELECT COUNTIF(conservative_id_candidate) FROM `{{dataset}}.transaction_policy`)
  UNION ALL SELECT 'qualified_event_count',(SELECT SUM(recorded_events) FROM `{{dataset}}.fact_transactions`)=(SELECT SUM(candidate_events) FROM `{{dataset}}.audit_purchase_coverage`)
  UNION ALL SELECT 'qualified_visit_links',(SELECT SUM(candidate_transactions) FROM `{{dataset}}.fact_visits`)=(SELECT COUNT(*) FROM `{{dataset}}.fact_transactions`)
  UNION ALL SELECT 'selected_value_links',IFNULL((SELECT SUM(agreeing_recorded_value) FROM `{{dataset}}.fact_visits`),0)=IFNULL((SELECT SUM(supported_recorded_value) FROM `{{dataset}}.fact_transactions`),0)
  UNION ALL SELECT 'item_rows_preserve_multiplicity',(SELECT COUNT(*) FROM `{{dataset}}.fact_transaction_items`)=(SELECT SUM(ARRAY_LENGTH(items)) FROM `{{dataset}}.fact_transactions`) AND (SELECT COUNTIF(ARRAY_LENGTH(t.items)!=IFNULL(i.item_rows,0)) FROM `{{dataset}}.fact_transactions` t LEFT JOIN (SELECT transaction_id,COUNT(*) AS item_rows FROM `{{dataset}}.fact_transaction_items` GROUP BY transaction_id) i USING(transaction_id))=0
  UNION ALL SELECT 'selected_item_values_reconcile',COUNTIF(t.item_agree AND (i.item_value IS NULL OR ABS(t.supported_recorded_value-i.item_value)>0.01))=0
    FROM `{{dataset}}.fact_transactions` t LEFT JOIN (SELECT transaction_id,SUM(item_revenue) AS item_value FROM `{{dataset}}.fact_transaction_items` GROUP BY transaction_id) i USING(transaction_id)
  UNION ALL SELECT 'money_absent_when_unsupported',COUNTIF((NOT item_agree AND supported_recorded_value IS NOT NULL) OR (item_agree AND supported_recorded_value IS NULL))=0 FROM `{{dataset}}.fact_transactions`
  UNION ALL SELECT 'primary_flag_matches_reason',COUNTIF(IFNULL(is_primary_eligible,FALSE)!=(exclusion_reason='eligible_primary'))=0 FROM `{{dataset}}.fact_visits`
  UNION ALL SELECT 'nested_ordered_steps',COUNTIF(strict_candidate_sessions>strict_checkout_sessions OR strict_checkout_sessions>strict_cart_sessions OR strict_cart_sessions>entry_sessions OR entry_sessions>sessions OR strict_candidate_sessions>tied_candidate_sessions)=0 FROM scope_summary
), fingerprints AS (
SELECT 'stg_events' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.stg_events` t
UNION ALL
SELECT 'transaction_policy' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.transaction_policy` t
UNION ALL
SELECT 'fact_transactions' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.fact_transactions` t
UNION ALL
SELECT 'fact_transaction_items' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.fact_transaction_items` t
UNION ALL
SELECT 'fact_visits' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.fact_visits` t
UNION ALL
SELECT 'audit_event_keys' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.audit_event_keys` t
UNION ALL
SELECT 'audit_visit_exclusions' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.audit_visit_exclusions` t
UNION ALL
SELECT 'audit_purchase_coverage' AS model,COUNT(*) AS row_count,CAST(SUM(CAST(FARM_FINGERPRINT(TO_JSON_STRING(t)) AS BIGNUMERIC)) AS STRING) AS content_checksum FROM `{{dataset}}.audit_purchase_coverage` t
), payload AS (
  SELECT (SELECT AS STRUCT COUNT(*) AS events,COUNTIF(event_name='purchase') AS purchase_events,
    COUNTIF(NOT IFNULL(user_key_usable,FALSE) OR session_id IS NULL) AS unkeyed_events FROM `{{dataset}}.stg_events`) AS source,
    (SELECT AS STRUCT COUNT(*) AS id_groups,COUNTIF(conservative_id_candidate) AS qualified_ids,
      COUNTIF(native_item_agree_candidate) AS agreeing_ids FROM `{{dataset}}.transaction_policy`) AS transaction_policy,
    (SELECT AS STRUCT COUNT(*) AS transactions,SUM(recorded_events) AS recorded_events,
      SUM(ARRAY_LENGTH(items)) AS item_rows,SUM(supported_recorded_value) AS selected_recorded_value FROM `{{dataset}}.fact_transactions`) AS transactions,
    ARRAY(SELECT AS STRUCT * FROM scope_summary ORDER BY scope,cohort_month,session_device) AS scopes,
    ARRAY(SELECT AS STRUCT * FROM `{{dataset}}.audit_event_keys` ORDER BY source_date,device,key_status) AS event_key_coverage,
    ARRAY(SELECT AS STRUCT * FROM `{{dataset}}.audit_visit_exclusions` ORDER BY cohort_month,exclusion_reason) AS visit_exclusions,
    ARRAY(SELECT AS STRUCT * FROM `{{dataset}}.audit_purchase_coverage` ORDER BY source_date,device) AS purchase_coverage,
    ARRAY(SELECT AS STRUCT * FROM checks ORDER BY check_name) AS checks,
    ARRAY(SELECT AS STRUCT * FROM fingerprints ORDER BY model) AS fingerprints
)
SELECT IF((SELECT COUNTIF(NOT IFNULL(passed,FALSE)) FROM checks)=0,
  TO_JSON_STRING(p),ERROR('Mart reconciliation assertions failed; inspect the named checks before use.')) AS audit_json
FROM payload p
;
