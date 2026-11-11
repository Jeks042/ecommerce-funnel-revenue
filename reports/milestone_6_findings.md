# Reproduction and case-study release

11 November 2026 · Historical measurement contract v1.

The completed study supports an investigation of product view to cart across devices. Source reproduction, code checks and the final wording review preserve that conclusion. They do not turn a missing next-step record into a lost sale or establish a reason to redesign mobile.

## What reproduced

A clean checkout of accepted milestone 5 commit `1b5db0e`, with a new Python 3.12.14 environment and pinned analysis dependencies, passed all 57 tests then present. Analysis and scenario summaries regenerated without tracked changes. All four figures regenerated as eight PNG/SVG files with identical numeric data and byte-identical assets on Windows. Visual review covered all four regenerated PNGs; labels, counts, limits and scenario assumptions remain visible. The final release suite contains 66 tests, including rejection of missing models, changed fingerprints, reused native jobs, cached results, excess scans and unexplained differences.

Thirteen fresh read-only native warehouse queries checked the fixed source and the retained dependency chain. All eight model counts and content checksums agree. Mart validation passes 995 source checks; the recorded funnel and separate reverse calculation pass 4,682 checks across 93 primary date/device cells. Inventory confirms eight unpartitioned base tables expiring on 5 January 2027. The run creates no duplicate physical build or paid-billing change.

The [release receipt](evidence/release-receipt-20261111.json) records actual execution dates, scan displays, hashed native references, comparisons and versions. Each accepted query has observed nonzero processing. An initially cached funnel result was excluded and rerun; both attempts remain recorded. The largest reviewed scan estimate was 2.57 GB, below the 3 GiB per-statement review ceiling. Displayed billed bytes consume the existing Sandbox quota; no monetary cost or configured maximum-bytes cap is claimed.

## Differences reviewed

Two approximate duration summaries shifted slightly: median observed span from 13.990649 to 13.983463 seconds, and the 95th percentile from 1,191.705366 to 1,187.774929 seconds. Both are `APPROX_QUANTILES` diagnostics. All other coverage values and the staged content fingerprint agree. These approximate summaries do not enter cohort eligibility, the funnel, charts or the recommendation. The [new source output](evidence/release-source-coverage-20261111.json) preserves the values, and the [reproduction guide](../docs/reproduction_workflow.md) explains the review. Earlier evidence remains unchanged.

Three input fingerprints also returned in a different array order. Comparing unique model names preserves exact counts and checksum values. No general numerical tolerance, relaxed purchase policy or replacement of missing outcomes was introduced.

The separate checkout and reverse implementation provide additional checks by the same analyst. This release does not imply an external human review or an independent trading-data audit.

## Public presentation and decision

The [portfolio case study](https://jeks042.github.io/ecommerce-funnel-revenue.html), [illustrated report](commercial_report.md) and [decision memo](decision_memo.md) use the same definitions and recommendation. Four original Python figures show the recorded journey, device differences, recording coverage and hypothetical scenarios. The README leads with the business question and findings; detailed methods sit in the supporting docs. Source attribution and the aggregate-only publication boundary are documented in [source publication scope](../docs/source_publication.md).

The primary sequence remains 27,289 product-view visits, 7,874 later carts, 2,819 later checkouts and 1,437 later qualified completions. Mobile has no broad recorded disadvantage; the date-adjusted overall gap is +0.28 percentage points. Ninety-two visits contain unresolved purchases. Total revenue, AOV, financial return and recoverable sales remain unavailable.

The next business action is to verify recording, study shopper tasks and decide whether a clearer cart action deserves a controlled test. The [proposal](../docs/experiment_proposal.md) still needs a production visitor baseline, a useful improvement target, safety margins and a frozen variant. Its power illustrations use assumed inputs. No experiment has run and no uplift has been measured.

Final commit, both workflow runs, retained artifacts, portfolio deployment and live-page verification are linked in [issue #6](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6). Workflows validate and retain evidence without warehouse credentials or bot commits.
