-- Disjoint reasons in a declared order; do not sum overlapping quality flags.
SELECT cohort_month,exclusion_reason,COUNT(*) AS visits,SUM(events) AS events,
  SUM(purchase_events) AS raw_purchase_events,SUM(candidate_transactions) AS candidate_transactions
FROM `{{dataset}}.fact_visits`
GROUP BY cohort_month,exclusion_reason
