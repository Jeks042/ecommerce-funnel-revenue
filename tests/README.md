# Purchase-reconciliation validation

`prepare_purchase_fixture.py` replaces the public-source reference in the actual reconciliation SQL with eleven synthetic events. It retains the production extraction, grouping and classification logic. The generated query reads literal fixtures only; the validated scan estimate is zero bytes.

Run `python tests/prepare_purchase_fixture.py` from the repository root. Open the resulting ignored `private/purchase_fixture.sql` in BigQuery, validate it, and execute. Save the returned inner `audit_json` object privately. Check it with `python tests/check_purchase_result.py private/fixture-result.json --expected private/purchase_fixture_expected.json`.

The fixtures cover repeated identical financial records, multi-item purchases without event multiplication, identity conflicts, changed monetary summaries, missing purchase value, missing transaction ID, an observed tax difference, and changed individual item values that preserve the same total. Expected values are declared independently from the production classification logic.

For real-data results, run `python tests/check_purchase_result.py reports/evidence/purchase-reconciliation-20261106.json`. This checks reconciliation, not whether records are genuine commercial orders or whether the source is suitable for every proposed measure.

The native fixture run passed thirteen scalar expectations and four bucket expectations on 5 November 2026. See the purchase-reconciliation receipt for query hashes and execution evidence. No credentialed execution runs automatically on GitHub pushes.

Run the credential-free validator regression checks with `python -m unittest discover -s tests -p "test_*.py"`. These check that corrupted bucket counts, dropped missing-ID events, double-counted conflict groups and inconsistent monetary-difference counts are rejected. They complement the native SQL fixture; they do not replace warehouse execution.

## Complete purchase-detail comparison

Run `python tests/prepare_purchase_detail_fixture.py`. Execute the generated ignored `private/purchase_detail_fixture.sql` in BigQuery after confirming its zero-byte scan estimate. The 29 synthetic events exercise the production detail SQL, including basket order, metadata changes, duplicate item-row multiplicity, matching totals with different lines, missing values, placeholder customers and cross-date/device repeats. Expected results are declared independently.

Export the result as local JSON, parse the outer row's `audit_json`, and save that inner object privately. Run `python tests/check_purchase_detail_result.py private/purchase_detail_fixture_result.json --expected private/purchase_detail_fixture_expected.json`. Run the same checker without `--expected` against `reports/evidence/purchase-detail-diagnostics-20261106.json` for the source result. It checks event/group partitions, nested candidate populations, daily device coverage and overlapping field/bucket reconciliation. See the [method](../docs/purchase_counting_review.md) and [receipt](../reports/evidence/purchase-detail-receipt-20261106.json).

The credential-free regression suite also rejects dropped date/device coverage, inflated candidate populations, inconsistent field/bucket attribution and nonfinite diagnostic amounts. These checks validate evidence integrity; they do not certify real orders or sales.

## Tracking, ordering and population sensitivity

Run `python tests/prepare_tracking_fixture.py` and execute the generated `private/tracking_fixture.sql` after confirming its zero-byte estimate. It uses 78 synthetic events and checks expected chain levels and flags for 15 keyed journeys, plus an unkeyed journey. See the [method](../docs/tracking_timing_review.md) for the edge cases.

Parse the downloaded result's inner `audit_json`, then run `python tests/check_tracking_result.py private/tracking_fixture_result.json --expected private/tracking_fixture_expected.json`. The native fixture passed 81 checks. Check the published source result with `python tests/check_tracking_result.py reports/evidence/tracking-timing-20261106.json`; it passes 58 checks, including nested chains, scope exclusions and daily/device coverage. The [receipt](../reports/evidence/tracking-timing-receipt-20261106.json) records execution and hashes.

Regenerate the coverage summary using the command in the method document. The local regression suite also rejects dropped daily rows, broken start/edge partitions, strict chains larger than the tied sensitivity and unsupported ordering-field counts. No authenticated warehouse execution runs automatically on GitHub.

## Final purchase/visit linkage and accepted scope

See the [measurement-gate method](../docs/measurement_gate.md) for commands. `prepare_measurement_fixture.py` replaces SQL 07's source with 56 typed synthetic events across eleven journeys. Independent expected scope counts distinguish two orders from one buying visit, earliest from replay timing, and cross-month ID conflict from an eligible December transaction. The final native fixture passes 93 checks; the real aggregate passes 525; 268 comparisons to earlier audit evidence also pass. The full local regression suite contains 22 passing tests.

Regenerate `reports/evidence/measurement-scope-20261106.json` using `src/build_measurement_summary.py` and compare it byte-for-byte. No source identifiers, credentials or full native job references are needed for these local checks.
