# Reproducing the completed study

The release review on 11 November 2026 checked a separate checkout, a new Python environment and fresh read-only warehouse calculations. It preserved measurement contract v1, the accepted figures and every earlier execution receipt. This was a separate reproduction by the same analyst; it does not claim an external human review.

The [release receipt](../reports/evidence/release-receipt-20261111.json) records software versions, native execution times, displayed scan sizes, hashed job references, model fingerprints, comparisons and the clean-checkout result. The [release findings](../reports/milestone_6_findings.md) explain the decisions.

## Reproduce Python analysis without cloud access

Start from a clean clone, using Python 3.12.14. These commands work from the repository root; activate the isolated environment using the command appropriate to your shell.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-analysis.txt
.venv/Scripts/python.exe tests/run_project_validation.py
.venv/Scripts/python.exe src/analyse_funnel.py
.venv/Scripts/python.exe src/assess_opportunity.py
.venv/Scripts/python.exe src/plotting/build_report.py --output private/release-report
.venv/Scripts/python.exe tests/check_report_render.py private/release-report
.venv/Scripts/python.exe tests/check_release_evidence.py
git status --porcelain
```

The analysis and scenario commands regenerate tracked aggregate summaries. An unchanged accepted checkout should remain clean. The figure build writes into ignored `private/`; review all four PNGs for labels, overlaps, clipping and meaning. Numeric plotting data must match. Image bytes may differ across operating systems or font environments; do not replace accepted assets merely to make platform-specific hashes match. See [report reproduction](report_reproduction.md).

The release reproduction used clean commit `1b5db0ea5eddf5ea6cb31658b9c0c8c06d18eb70`, a newly created environment and the pinned requirements. All 57 tests then present passed, both summaries regenerated without tracked changes and all eight PNG/SVG files matched the published assets byte for byte on Windows. The final release adds nine regression tests, bringing the suite to 66. The statsmodels comparison is recorded separately in [the experiment proposal](experiment_proposal.md); it is not required to plot the report or rerun the dependency-free planning arithmetic.

## Reproduce the warehouse evidence

Use authorised access to an existing US BigQuery Sandbox. Keep the project ID and rendered SQL under ignored `private/`. No credentials are required by the renderer, and it executes nothing:

```powershell
python src/render_release_checks.py --project your-project-id --dataset ecommerce_v1_build --output private/release-checks
```

The 13 statements are read-only. Execute one at a time in Console. Confirm Sandbox and inspect each validator estimate before Run; stop above the 3 GiB review ceiling. Keep billing unchanged. The displayed estimate is a review control, not a configured per-job maximum. Billed bytes in the receipt reflect free-quota consumption, not a calculated cash charge.

| Statements | Reproduction boundary |
|---|---|
| 01–08 | Recompute every model against its declared input and compare row counts and order-independent content checksums with the accepted physical tables. Staging rereads all 92 fixed public-source dates. |
| 09 | Run the existing warehouse assertions and reconcile the full aggregate output. |
| 10 | Check all eight base tables, their expiry and absence of date partitions. |
| 11 | Reread public-source recording coverage and timing diagnostics. |
| 12–13 | Recalculate daily funnel, contexts and timing/population alternatives; independently work backwards through the primary device/date cells. |

Download only the aggregate `audit_json` result. Keep original job metadata and rendered configuration private. Verify nonzero processing for accepted fresh runs; a cached result alone is insufficient. The release initially received a cached funnel result, excluded it from acceptance, then reran with distinct query text and observed 1.61 GB processed. The receipt retains both attempts.

This method does not build a second set of physical tables. Recomputing staging from the source, matching it to the retained staging table and recomputing each downstream model checks the dependency chain while avoiding another copy against Sandbox storage limits. If the existing tables have expired, use the [first-build instructions](sql_workflow.md), inspect available quota and execute the same bounded build and checks. The accepted eight tables expire on 5 January 2027; GitHub retains the SQL and reviewed aggregate evidence.

## Comparison rules and reviewed differences

All eight model row counts and checksums match. Fresh mart assertions pass 995 source checks, and the funnel plus separate reverse calculation pass 4,682 checks across all 93 primary device/date cells. Source-event counts, purchase coverage, eligibility, unresolved outcomes, all funnel counts and the inventory agree with accepted evidence.

Two approximate duration diagnostics differ: median observed span is 13.983463 seconds versus 13.990649 previously; the approximate 95th percentile is 1,187.774929 versus 1,191.705366 seconds. Both use `APPROX_QUANTILES` in source SQL. Google's [approximate aggregate documentation](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/approximate_aggregate_functions) describes the statistical uncertainty of these functions. With identical staged content checksums and exact remaining source checks, the observed differences are consistent with approximate computation. No finding, eligibility rule or decision threshold uses these two diagnostics. Keep both runs visible in [the fresh coverage output](../reports/evidence/release-source-coverage-20261111.json) and the receipt. No broad numeric tolerance was introduced.

The funnel input-fingerprint array also returned in a different order. Compare its three unique entries by model name; do not treat array position as model identity. Daily/date/device arrays and their counts remain exact. The release checker reconstructs the observed fingerprint order and verifies the native result hash. It permits exceptions only for the two named approximate diagnostics, then requires exact equality everywhere else.

Do not revise earlier receipts or relax counting rules to make a mismatch pass. Investigate any new difference and document its effect before accepting another release.

## Public release checks

Public files contain original analysis and reviewed aggregates. See [source attribution and publication scope](source_publication.md). Inspect tracked paths and content for raw records, identifiers, private project IDs, secrets and career material. Check local Markdown targets, image alternative text, exact chart values and consistency between README, report, decision memo and portfolio. Review the portfolio at desktop and mobile widths and confirm its live page and four image links after publication.

The two existing GitHub workflows remain unchanged. Analytical validation discovers the additional release tests; the figure workflow regenerates all four figures and retains the eight files plus its manifest. Both use read-only repository permissions, retain artifacts for 30 days and have no warehouse credentials or commit step. CI validates saved reviewed native evidence; it does not rerun BigQuery. Final commit, workflow, deployment and live-page evidence is recorded in [issue #6](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6).
