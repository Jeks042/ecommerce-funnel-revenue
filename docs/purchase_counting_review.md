# Purchase-detail comparison and candidate counting

Status: sensitivity method within milestone 1. The metric contract remains a draft.

## Source and schema

[04_purchase_field_inventory.sql](../sql/04_purchase_field_inventory.sql) checks every e-commerce and item subfield plus six named ordering candidates across the fixed 92-table window. The [result](../reports/evidence/purchase-field-inventory-20261106.json) contains 37 e-commerce/item field entries and three ordering fields, each present in all 92 tables. The checked `batch_event_index`, `batch_ordering_id` and `batch_page_id` fields are absent. Presence of bundle sequence, previous timestamp and server offset fields does not establish their completeness or ability to resolve tied funnel steps; that remains a separate test.

Google describes this as an obfuscated sample with limited internal consistency. Do not reconcile it to a separate Analytics demo account or interpret identifier consistency as confirmation of a real sale. Source: [Google's sample dataset documentation](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset).

## Comparisons

[05_purchase_detail_diagnostics.sql](../sql/05_purchase_detail_diagnostics.sql) extracts session and currency parameters through correlated subqueries and keeps one row per purchase event. Transaction IDs are trimmed; null, blank, `<Other>` and `(not set)` values are unusable. A valid session parameter occurs exactly once, contains an integer and is positive. Customer IDs must be nonblank and outside the same known placeholder set. Currency must occur once and match three uppercase letters; the candidate rule additionally requires USD.

For each usable transaction identifier, the query compares:

- Customer/session pairs and the earlier currency/native/USD/item-sum/quantity summaries.
- The complete e-commerce structure, including nulls, tax, shipping, quantities and refund fields.
- Original item-array contents and a sorted multiset of serialized complete item rows. Sorting permits a different array order while retaining duplicate rows and their multiplicity.
- A sorted multiset of item ID, name, variant, quantity, native/USD price, revenue and refund fields. This is the explicitly defined core product-and-money comparison; other item fields remain metadata for this diagnostic.
- Each of the 37 e-commerce/item fields independently, with item values also compared as multisets. These field counts overlap. A matching individual-field multiset does not establish that values are attached to the same products; the complete-row and core comparisons retain those associations.

Stored-value equality uses serialized values without rounding. The separate native/item agreement test allows an absolute difference of at most $0.01. No comparison treats missing money as zero.

The mutually exclusive bucket order is: identity/summary conflict, other e-commerce difference, core-item difference, metadata difference, array-order-only difference, repeated exact details, single observation. Overlapping field differences are returned separately, including their bucket membership. Empty buckets need not appear in the result.

## Candidate rule and amounts

One candidate per usable identifier requires one identity variant, one summary variant, one complete e-commerce variant and one complete item multiset, plus a single observed source date and device and valid customer/session/USD values. Source dates are used for coverage diagnostics; no session timezone or boundary policy is inferred. The device rule requires agreement, not a particular device label. This rule does not verify the source identity, the truth of a transaction, or the event sequence.

The native-complete subset further requires every observation to have a finite, nonnegative native purchase amount. The native/item-agreeing subset also requires a nonempty basket, all finite item revenue values and a purchase/item-sum difference within $0.01. Neither subset establishes tax/refund treatment, correct quantities or an accounting reconciliation. The once-per-identifier native sum is computed only after agreement within the group; it is a diagnostic, not approved revenue. No first/last record is selected to resolve a conflict.

Date/device coverage counts events joined to candidate groups, not distinct orders. They may be summed to the event population. Do not use those rows as conversion rates or sum raw usable identifier counts across dates. The customer/summary-conflict and cross-date groups were explicitly cross-tabulated rather than assumed equal from matching totals.

## Validation and reproduction

Confirm Sandbox and the validator estimate before every Run. Follow the 3 GiB review ceiling and other [source-audit controls](source_audit_workflow.md); no paid billing or per-job API cap was enabled. Generate the literal-only fixture with `python tests/prepare_purchase_detail_fixture.py`, run the ignored generated SQL in BigQuery, export its aggregate JSON and validate the inner `audit_json` using the checker and independent expected file. Only then run SQL 05 against the source.

The synthetic cases test item order, metadata changes, changed line values with unchanged totals, duplicate-row multiplicity, repeated identical records, identity/currency conflicts, missing native money, missing IDs, tax changes, cross-date/device repeats, invalid session IDs, placeholder customers and native/item disagreement. The production query is retained when substituting synthetic rows. These fixtures verify the implemented counting method, not commercial truth.

Save results through Console's local JSON download. Parse the exported outer row and then its `audit_json`; preserve nulls. Keep original downloaded exports and full job references private. Publish only the reviewed aggregate, SQL hashes and hashed job references. The [receipt](../reports/evidence/purchase-detail-receipt-20261106.json) records executions and checks; [findings](../reports/purchase_detail_findings.md) explain the decision.

Run `python tests/check_purchase_detail_result.py reports/evidence/purchase-detail-diagnostics-20261106.json` for partitions, candidate nesting, date/device coverage and field/bucket reconciliation. These checks and the original purchase-audit comparisons must pass before publication. Local regression tests check that inconsistent evidence is rejected. No credentialed source scan runs on a GitHub push.
