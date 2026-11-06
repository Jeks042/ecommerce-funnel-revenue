# Measurement acceptance and reproduction

[SQL 07](../sql/07_measurement_gate.sql) combines the previously audited purchase qualification and visit/timing CTEs. It adds one row per qualified ID, a purchase-event membership table and a one-row-per-visit outcome table. Only aggregate counts, coverage and selected monetary sums are returned. No source identifiers leave the warehouse.

## Implementation review

- The source selection explicitly includes the wildcard table suffix, which `SELECT *` does not expose. All source branches retain the fixed 92-day bounds.
- Purchase qualification precedes cohort selection and preserves the complete-item multiset and full e-commerce comparison from SQL 05. Repeated records do not multiply the transaction or visit tables.
- A qualified ID supplies one consistent customer/session identity. `MIN` selects that proven identical identity, not an arbitrary way to settle conflicts. Earliest purchase time is canonical; latest time is a sensitivity.
- The outer visit joins preserve no-purchase visits. Missing/rejected-ID events are counted separately; their presence is not a known zero financial outcome. The selected-value sum stays null when a visit has no item-agreeing value.
- Visit membership and start/edge rules match SQL 06. Device assignment uses the sole device value for eligible groups; broader diagnostics do not make mixed-device groups eligible.
- Counts use the visit's first observed UTC month. Daily purchase coverage uses the purchase event's source date. Those are different grains: December has 2,434 source-date purchase events, but 2,433 in all groups whose first event is in December. Do not force those subtotals to match.

## Native fixture

From the repository root:

```powershell
python tests/prepare_measurement_fixture.py
```

Run the generated ignored `private/measurement_fixture.sql` in the existing authenticated BigQuery Sandbox after confirming **0 B** in the validator. The eleven declared cases cover an ordinary chain, a repeated purchase straddling checkout, two orders in one visit, missing ID, item disagreement, no purchase, timestamp ties, crossing midnight, a >24-hour group and conflicting observations of one ID in different months. The source SQL remains intact; only its input is replaced with typed literals. Earlier fixtures exercise the detailed payload, identifier, timing and malformed-key cases.

Use Console's local JSON download. Parse the outer row's `audit_json` string without filling nulls or changing values. Save the inner object privately, then run:

```powershell
python tests/check_measurement_result.py private/measurement_fixture_result.json --expected private/measurement_fixture_expected.json
```

The published fixture aggregate is also available as `reports/evidence/measurement-fixture-20261106.json`. All 93 checks pass, including independently declared counts for each scope. The replay case distinguishes earliest from latest timing; two orders remain two transactions and one buying visit; a conflict in January still rejects its December observation.

## Source run

Run the unchanged SQL 07 against the fixed source bounds. Confirm Sandbox and review the estimate; stop above 3 GiB. The review ceiling is not an enforced per-job bytes setting. Sandbox's free query quota is the no-paid-billing boundary. Do not provision billing, change projects or publish private project/account/job references.

Export only the single aggregate row using the same JSON procedure. Run:

```powershell
python tests/check_measurement_result.py reports/evidence/measurement-gate-20261106.json
python tests/check_measurement_baselines.py
python -m unittest discover -s tests -p "test_*.py"
python src/build_measurement_summary.py reports/evidence/measurement-gate-20261106.json reports/evidence/tracking-timing-20261106.json private/rebuilt-measurement-scope.json
```

Compare the regenerated scope JSON byte-for-byte with `reports/evidence/measurement-scope-20261106.json`. Validation checks linkage, disjoint purchase-event partitions, nested ordered populations, visit/order grains, monetary coverage, unique output groups, daily/device purchase coverage and all three scope totals against the earlier audits. Local regression checks reject missing links, hidden missing-ID events, inflated chain counts and duplicated output groups.

The [receipt](../reports/evidence/measurement-gate-receipt-20261106.json) records canonical SQL/output hashes and hashed native job references. Formatting in Console may differ; the executed text was checked against the canonical query after whitespace normalization. No credentialed query runs automatically on GitHub pushes. Milestone 2 must add appropriate credential-free workflow validation without bot-authored commits.
