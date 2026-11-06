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

## Focused purchase follow-up

After the broad profile, run [03_purchase_reconciliation.sql](../sql/03_purchase_reconciliation.sql) using the same fixed window and Sandbox/scan-review controls. First generate and run its native synthetic [fixture](../tests/README.md). The source query returns only aggregate partitions, conflict overlap and monetary-field diagnostics. Reconcile it to the previous purchase-event, missing-ID, native-revenue and difference counts; investigate any drift.

The complete e-commerce/item payload comparison is order-sensitive and includes item metadata. It is an investigation flag, not a decision that a sale is duplicated or financially different. Do not use its diagnostic buckets as approved orders or revenue.

## Field-level purchase review

Run [04_purchase_field_inventory.sql](../sql/04_purchase_field_inventory.sql) and check the actual available fields before testing [05_purchase_detail_diagnostics.sql](../sql/05_purchase_detail_diagnostics.sql). Use the same Sandbox and scan-review controls. The [method](purchase_counting_review.md) defines the complete-item multiset comparison, overlapping field differences and candidate counting sensitivity. First generate and execute its literal-only fixture; validate the saved inner JSON against the independent expected results. Then run the bounded source query, use Console's local JSON download and validate the parsed aggregate before publication. Do not export source event rows or identifiers.

The detail query returns daily device coverage at purchase-event grain. Its candidate counts and amount sums are diagnostics. Passing those tests does not freeze the metric contract or establish commercial order/revenue truth.

## Tracking, timing and boundary sensitivity

Generate the literal-only fixture for [06_tracking_timing_sensitivity.sql](../sql/06_tracking_timing_sensitivity.sql) with `python tests/prepare_tracking_fixture.py`. Validate its zero-byte estimate, execute it and check the saved inner JSON against `private/tracking_fixture_expected.json`. After those checks pass, run the unchanged production SQL with the fixed 92-day window and existing Sandbox/scan controls. The [method](tracking_timing_review.md) defines the six overlapping populations, strict/tied event chains and daily event coverage.

Save the aggregate through Console's local JSON download, reconcile it to the earlier event/session/purchase totals and regenerate the Python coverage summary. Publish the [findings](../reports/tracking_timing_findings.md), [aggregate](../reports/evidence/tracking-timing-20261106.json) and [receipt](../reports/evidence/tracking-timing-receipt-20261106.json). Raw purchase events in this query do not inherit the complete transaction-candidate policy. Do not present this sensitivity as approved order conversion or infer the cause of missing events.
