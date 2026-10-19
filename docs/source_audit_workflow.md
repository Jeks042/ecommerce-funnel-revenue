# Running the source audit

## Prerequisites and cost control

Use a Google Cloud project with BigQuery access and permission to query the public sample in the US location. Keep account and project settings private. The kickoff used an existing Sandbox project; no project, paid billing, capacity or scheduled query was provisioned.

In Sandbox, verify the Sandbox banner and review the query validator's estimated scan before each Run. Use the fixed date bounds below and stop if the estimate exceeds 3 GiB. Sandbox's enforced free quota is the cost boundary; that review ceiling is not a per-job API cap. For a billing-enabled project, explicitly set maximum bytes billed before execution; an estimate or LIMIT does not enforce a cost cap. No paid execution is authorised by these instructions.

## Query sequence

1. Run [01_source_inventory.sql](../sql/01_source_inventory.sql). Confirm the 92 expected dates and all 20 selected field/type entries. If the metadata differs, investigate before running the profile.
2. Run [02_source_profile.sql](../sql/02_source_profile.sql) unchanged for 1 November 2020. Check query validation first. The query returns one `audit_json` string containing aggregate diagnostics.
3. Review the pilot. To check the full sample, change the single predicate to `_TABLE_SUFFIX BETWEEN '20201101' AND '20210131'`. Keep all other query text unchanged and review the larger estimate before Run.
4. Save the aggregate JSON and execution details privately first. Do not export event rows or keys. Review the output before copying approved aggregates to `reports/evidence/`.
5. Confirm event-type totals and device totals equal the event count; currency purchase counts equal the purchase-event count; and valid-ID events plus unusable-ID events equal purchase events. Keep missing values as JSON null.
6. Record source dates, the canonical SQL hash, parameter changes, job outcome, displayed scan sizes and the run date. Private account, full job references and working project details belong in ignored `private/` material.

The SQL extracts repeated parameters and item summaries through correlated subqueries, keeping one row per source event. It does not cross join parameter and item arrays. Session and transaction identifiers are used inside BigQuery for diagnostics and omitted from the returned result.

## What the checks mean

The current key check requires a nonblank, nonplaceholder user identifier and exactly one positive integer session parameter. Currency checks accept one three-letter uppercase value; they do not validate exchange rates. Transaction IDs are trimmed, with blank, null, `<Other>` and `(not set)` values left unusable. Further placeholders can require a revised policy.

Repeated IDs are flagged when they appear in multiple purchase events. Identity conflicts compare user/session pairs, and monetary conflicts compare the currency, native/USD purchase value and item summaries. The two sets may overlap. The diagnostics do not select a deduplication rule or verify the complete purchase payload.

Item comparison counts use a $0.01 tolerance on events with both native purchase and item sums present. SUM ignores null items, so partial-item coverage is diagnosed separately. The count is not proof of an accounting error; tax treatment and obfuscation need checking.

The query measures mixed funnel-step timestamp groups rather than assuming their order. Cross-date sessions and absent start events are diagnostics, not automatic exclusion rules. Acquisition fields checked here describe first-user context, not session acquisition or causal marketing attribution.

Successful execution of the profile is not acceptance of the metric contract. See the [source audit](../reports/source_audit.md) for the outstanding work.
