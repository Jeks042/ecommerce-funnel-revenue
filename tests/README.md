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

## Materialized analytical tables

See the [SQL workflow](../docs/sql_workflow.md). `prepare_mart_fixture.py` generates a materialized temporary-table script over 94 synthetic events. The single-input SELECT validates at zero source bytes; the full temporary-table script has no complete dry-run estimate and its table reads process/bill bytes within the existing Sandbox quota. It never reads the public source or writes permanent targets.

The fixture aggregate passes 66 checks against independently declared counts. The source aggregate passes 995 checks, including all accepted scope cells. Twenty native assertions cover unique grains, conservation, joins, item multiplicity per transaction, selected item values and ordered populations. Eight read-only recomputations match stored model row counts and content checksums. The local regression suite has 32 tests.

Run `python tests/run_project_validation.py` for the same credential-free validation used on GitHub. It calls the accepted historical runner unchanged, then reproduces the prospective scenarios and sample-size illustrations and checks their code/input/output hashes. Historical validation compares inventory/recomputation evidence and checks that SQL, renderer and regenerated fixture hashes match their native receipts. CI uploads only the small public validation report, never private configuration or source records.

For milestone 4, `test_opportunity.py` covers absolute-versus-relative changes, no downstream gain, downside cases, impossible/nonnested populations, invalid inputs, sample-size sensitivity, two-sided symmetry and independent statsmodels reference values. The scenario generator uses only Python 3.12 standard-library arithmetic. Statistical-library checks were run separately with statsmodels 0.15.0 and SciPy 1.18.1; CI validates against the saved reference rather than claiming to rerun that library.

Regenerate scenarios with `python src/assess_opportunity.py`. Assumptions are versioned in `reports/evidence/scenario-assumptions-v1.json`. A changed assumption requires regenerated outputs, review and an updated planning receipt; it must not silently alter the accepted historical evidence. No trial outcomes or live experiment are present.

## Commercial report and figure reproduction

The existing test-discovery command now also runs `test_report_evidence.py`: complete 92-date/device coverage, missing/null counts, duplicate cells, all 15 scenario cases, decimal display labels and report/source/asset/document reconciliation. The historical and opportunity runners remain unchanged so their execution-receipt hashes retain their meaning.

`python tests/check_report_evidence.py` checks the report and plotting data without chart dependencies. Install `requirements-analysis.txt`, run `python src/plotting/build_report.py --output private/report-build`, then `python tests/check_report_render.py private/report-build` to regenerate and validate eight PNG/SVG files. The separate report workflow runs those commands and retains the regenerated figures and build manifest for 30 days, without credentials or commits. See [report reproduction](../docs/report_reproduction.md).
