-- GoogleSQL. Metadata only; no event rows or identifiers returned.
-- Confirm Sandbox and review validator estimate before Run.
WITH fields AS (
  SELECT table_name, field_path, data_type
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`
  WHERE STARTS_WITH(field_path,'ecommerce.') OR STARTS_WITH(field_path,'items.')
  UNION ALL
  SELECT table_name, column_name AS field_path, data_type
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.INFORMATION_SCHEMA.COLUMNS`
  WHERE column_name IN ('event_bundle_sequence_id','event_server_timestamp_offset',
    'event_previous_timestamp','batch_event_index','batch_ordering_id','batch_page_id')
)
SELECT TO_JSON_STRING(STRUCT(ARRAY(
  SELECT AS STRUCT field_path,data_type,COUNT(DISTINCT table_name) AS tables_with_field
  FROM fields
  WHERE table_name BETWEEN 'events_20201101' AND 'events_20210131'
    AND REGEXP_CONTAINS(table_name,r'^events_[0-9]{8}$')
  GROUP BY field_path,data_type ORDER BY field_path
) AS field_coverage)) AS audit_json;
