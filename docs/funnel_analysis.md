# Funnel analysis and reproduction

The [findings](../reports/milestone_3_findings.md) lead with the commercial interpretation. This document records how those findings were calculated under [measurement contract v1](metric_contract.md). No definition or monetary permission changed.

## SQL outputs

`sql/funnel/01_recorded_progression.sql` reads the existing tables; it does not rebuild or persist data. It returns December-start daily device counts for `all_keyed`, `anchored_interior` and `primary` populations; primary first-user context totals; daily counts for the two admitted contexts; and fingerprints of its three input models. Each table is aggregated before publication. No customer, session or transaction identifiers leave the warehouse.

Ordered steps use the accepted earliest subsequent timestamp logic in `fact_visits`, and qualified transactions use the globally admitted ID rule before cohort selection. Tied ordering, unordered event presence and raw purchase completion remain separate diagnostics. Unordered completion requires a view, cart, checkout and at least one qualified transaction in the visit; it does not require their chronology or a matching SKU. Buying-visit share uses all eligible visits independently of the chain.

Context admission requires literal, interpretable source and medium values and the fixed minimum size for entry-to-purchase comparison. Preserve `(direct) / (none)` as the source's literal context, without inventing session attribution. Choose the two largest admitted groups by entry count, not by their observed rates. Other contexts remain in the aggregate coverage ledger. Landing context was not admitted or analysed.

`sql/funnel/02_independent_reverse_check.sql` independently reconstructs event arrays from `stg_events`, joins eligible keys and globally qualified `fact_transactions`, then searches backwards: the latest admissible purchase time, a preceding checkout, a preceding cart and a preceding view. The latest purchase considered is the maximum of each qualified ID's **earliest** observation, not the latest replay. Separate reverse searches recalculate cart-only, checkout-only, raw completion, strict and tied definitions. This existence test uses no stored forward-step flags. It matches all 11 recalculated metrics across all 93 primary date/device cells.

## Comparison method

The desktop/mobile comparison uses the two largest primary groups by entry count. For **each displayed comparative rate**, both groups need at least 500 denominator visits, 30 successes and 30 other visits. Tablet is shown as counts only in the report to avoid a partially ranked funnel with sparse later steps. These thresholds are reporting rules, not a power calculation.

For each transition separately, retain dates with positive denominators in both groups. On date d use weight:

`w[d] = (denominator_A[d] + denominator_B[d]) / sum_common_dates(denominator_A + denominator_B)`

Apply these same weights to each group's daily success/denominator rate. The gap is group B minus A, multiplied by 100 for percentage points. All 31 dates and all relevant denominators remain in the admitted source comparisons. The saved output retains common-date counts and full counts so a narrower overlap cannot be hidden. Different transitions use different weights; the adjusted values must not be multiplied into an adjusted funnel.

Leave-one-date-out sensitivity omits each common date, reapplies each group's reporting thresholds and recomputes pooled weights on the remaining dates. Save the minimum and maximum gap and the number of admissible omissions (31 for each current comparison). These ranges are not confidence intervals. They do not handle repeat-user dependence or establish statistical significance. No inference beyond contract v1 was introduced.

Only calendar composition is adjusted. Device, first-user context, product, intent and repeat-user composition can remain associated; no causal device or marketing ranking is supported. First-user contexts were not standardised for device mix, so their descriptive differences must not become acquisition recommendations.

## Validation and evidence

The source-free native fixture reuses 94 literal events and nine temporary models from milestone 2. It contains tied and out-of-order events, replay timing, multiple transactions, missing/conflicting IDs, malformed session keys and duplicate item occurrences. The forward profile produces 13 primary entries, 11 strict carts/checkouts and five strict completions; the tied definition gives six and unordered presence eight. The independent reverse calculation agrees. Eighty fixture checks include the expected counts and small-context suppression.

`tests/check_funnel_result.py` checks integer counts, uniqueness, complete independent cell coverage, nested strict/tied/presence populations, context reconciliation, accepted scope/device baselines, unresolved outcomes and model fingerprints: 4,682 source checks in the current evidence. Three input fingerprints equal milestone 2. The source profile processed 1.61 GB; the independent recalculation processed 219.66 MB, both reviewed below the 3 GiB ceiling. Native fixture scripts have no complete-script scan estimate; their bounded temporary-table reads still consume free quota. Full job/configuration references remain private; the public receipt contains hashes and execution metadata.

Python tests exercise reporting thresholds, zero denominators, a known date-mix reversal, common-date loss, duplicate dates, leave-one-date-out recomputation and tampered/dropped evidence. CI reproduces the analysis from saved aggregates, checks native SQL/code/output freshness, reconciles the chart data and verifies the published asset hashes. **CI does not rerun BigQuery or render charts**. It uses no warehouse credentials, retains its validation artifact and commits nothing. Final PNG layouts were inspected separately.

## Reproduce

For saved-evidence validation, Python 3.12.14 and the standard library suffice:

```sh
python tests/run_local_validation.py
```

To regenerate the summary and figures, create an isolated Python environment and install the pinned chart dependencies:

```sh
python -m pip install -r requirements-analysis.txt
python src/analyse_funnel.py
python src/plot_funnel.py
```

The figures are PNG and SVG generated directly from the reviewed summary. The chart receipt contains numeric plotting data, source/code hashes, asset hashes and dependency versions. Numeric results should reproduce exactly; font rendering and image bytes may vary across platforms. Review image changes before updating hashes.

For a fresh native run, first reproduce the [accepted models](sql_workflow.md) in a dedicated private US dataset. Configure the existing ignored mart manifest, then run `python src/render_funnel.py` locally. It renders read-only source statements and two source-free temporary-table fixture scripts under `private/`. The optional loopback transfer packet is also private and is never served publicly. Review each source estimate separately, stop above 3 GiB, keep Sandbox/no paid billing, run and download only aggregate `audit_json`. Verify fingerprints, native fixtures, baseline comparisons and independent reverse results before replacing any evidence. The current source tables expire on 5 January 2027.

The evidence files use the `funnel-*-20261110.json` naming family under `reports/evidence/`. The execution receipt connects the native SQL hashes to the aggregate outputs; the figure receipt connects those outputs to the published figures. The final independent reproduction and commercial case-study release remain milestone 6.
