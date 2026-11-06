-- One row per retained source event. Arrays are not flattened.
WITH extracted AS (
  SELECT _TABLE_SUFFIX AS source_suffix,event_date,event_timestamp,event_name,user_pseudo_id,
    device.category AS device,traffic_source.source AS first_user_source,
    traffic_source.medium AS first_user_medium,ecommerce,items,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_entries,
    (SELECT COUNTIF(p.value.int_value IS NOT NULL) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_int_entries,
    (SELECT MAX(p.value.int_value) FROM UNNEST(event_params) p WHERE p.key='ga_session_id') AS sid_candidate,
    (SELECT COUNT(*) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_entries,
    (SELECT MAX(p.value.string_value) FROM UNNEST(event_params) p WHERE p.key='currency') AS currency_candidate
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
)
SELECT *,
  CASE WHEN sid_entries=1 AND sid_int_entries=1 AND sid_candidate>0 THEN sid_candidate END AS session_id,
  NULLIF(TRIM(user_pseudo_id),'') IS NOT NULL AND TRIM(user_pseudo_id) NOT IN ('<Other>','(not set)') AS user_key_usable,
  CASE WHEN currency_entries=1 AND REGEXP_CONTAINS(currency_candidate,r'^[A-Z]{3}$') THEN currency_candidate END AS currency,
  CASE WHEN NULLIF(TRIM(ecommerce.transaction_id),'') IS NOT NULL
    AND TRIM(ecommerce.transaction_id) NOT IN ('<Other>','(not set)') THEN TRIM(ecommerce.transaction_id) END AS transaction_id,
  event_timestamp IS NOT NULL AND event_timestamp>0 AND SAFE.TIMESTAMP_MICROS(event_timestamp) IS NOT NULL AS timestamp_usable,
  SAFE.PARSE_DATE('%Y%m%d',source_suffix) AS source_date
FROM extracted
