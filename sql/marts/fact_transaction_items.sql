-- Child grain: one sorted item occurrence per qualified transaction, including duplicates.
-- Purchase-level value is deliberately absent: never sum it through a one-to-many join.
SELECT t.transaction_id,item_offset+1 AS item_row_number,t.user_pseudo_id,t.session_id,
  t.purchase_date,t.item_agree AS transaction_value_supported,i.*
FROM `{{dataset}}.fact_transactions` t CROSS JOIN UNNEST(t.items) i WITH OFFSET item_offset
