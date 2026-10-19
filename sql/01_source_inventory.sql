-- GoogleSQL. Read-only metadata inspection; no event rows or identifiers returned.
-- Before execution: confirm Sandbox, inspect validator estimate and set a bytes cap.
WITH tables AS (
  SELECT table_name, table_type,
    SAFE.PARSE_DATE('%Y%m%d', SUBSTR(table_name, 8)) AS source_date
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.INFORMATION_SCHEMA.TABLES`
  WHERE REGEXP_CONTAINS(table_name, r'^events_[0-9]{8}$')
), expected AS (
  SELECT source_date FROM UNNEST(GENERATE_DATE_ARRAY('2020-11-01','2021-01-31')) AS source_date
), fields AS (
  SELECT table_name, column_name AS field_path, data_type
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.INFORMATION_SCHEMA.COLUMNS`
  WHERE column_name IN ('event_date','event_timestamp','event_name','user_pseudo_id')
  UNION ALL
  SELECT table_name, field_path, data_type
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`
  WHERE STRPOS(field_path, '.') > 0
), required AS (
  SELECT field_path, data_type, COUNT(DISTINCT table_name) AS tables_with_field
  FROM fields
  WHERE REGEXP_CONTAINS(table_name, r'^events_[0-9]{8}$')
    AND table_name BETWEEN 'events_20201101' AND 'events_20210131'
    AND field_path IN ('event_date','event_timestamp','event_name','user_pseudo_id',
      'event_params.key','event_params.value.int_value','event_params.value.string_value',
      'device.category','traffic_source.source','traffic_source.medium',
      'ecommerce.transaction_id','ecommerce.purchase_revenue','ecommerce.purchase_revenue_in_usd',
      'ecommerce.refund_value','ecommerce.tax_value','ecommerce.shipping_value',
      'items.item_id','items.quantity','items.item_revenue','items.item_revenue_in_usd')
  GROUP BY field_path, data_type
)
SELECT TO_JSON_STRING(STRUCT(
  (SELECT COUNT(*) FROM tables) AS daily_tables,
  (SELECT MIN(source_date) FROM tables) AS first_date,
  (SELECT MAX(source_date) FROM tables) AS last_date,
  (SELECT COUNT(*) FROM expected) AS expected_dates,
  ARRAY(SELECT e.source_date FROM expected e LEFT JOIN tables t USING(source_date)
    WHERE t.table_name IS NULL ORDER BY e.source_date) AS missing_dates,
  ARRAY(SELECT AS STRUCT field_path, data_type, tables_with_field FROM required ORDER BY field_path) AS schema_coverage
)) AS audit_json;
