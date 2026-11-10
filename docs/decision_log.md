# Decision log

## 24 September 2026 — Scope and sequence

Set up six milestones for a GA4/BigQuery study focused on shopping funnels and revenue opportunity assessment, with Power BI reporting. Begin with source and metric validation. No analysis or cloud provisioning is included in setup.

## 24 September 2026 — Measurement before interpretation

Source suitability is a gate. Validate sessions, transactions and monetary fields before drawing conclusions. Use scenario language for potential improvements; causal effects require a future controlled experiment.

## 24 September 2026 — Public presentation

Publish methods, permitted aggregate evidence and professional decision records. Preserve provenance and limitations. Keep raw records, credentials and unrelated personal planning outside the project.

## 19 October 2026 — Kickoff and six delivery milestones

Continue the existing repository and six issues. Create matching GitHub milestones, without inventing due dates. Begin source validation and give a plain-language briefing at each stage before explaining the next step. Use the existing public presentation as the style reference: business question first, technical methods in the supporting docs.

## 19 October 2026 — Sandbox and bounded source checks

The existing project is visibly in Sandbox. Run metadata first, then a one-day pilot, then the explicit 92-day window after reviewing the pilot and the larger validator estimate. Sandbox's enforced quota provides the no-paid-billing boundary; do not represent the Console review ceiling as a per-job maximum-bytes setting. Keep private project/account configuration outside Git.

## 19 October 2026 — Source available; measurement gate stays open

The full profile covers 4,295,584 events and identifies missing/repeated purchase IDs, money-field differences and tied funnel timestamps. Continue source checks; do not call purchase events distinct orders, approve revenue/AOV, or start the SQL marts until the counting rules and their impacts are settled. First-user acquisition context must retain its actual meaning. No causal or realised revenue opportunity is established.

## 19 October 2026 — Report presentation

Preserve the report owner's preference to review Power BI formatting and provide or approve captures before public use. Use an approved executive overview as the case-study preview, with the complete report linked; do not publish automated desktop captures during report development.

## 5 November 2026 — Python analysis and visual reporting

Replace the planned Power BI reporting stage with Python analysis and charts using Matplotlib and Seaborn. Retain BigQuery SQL, all measurement gates and the six-stage dependency order. Deliver reproducible figures, an illustrated commercial report and a decision memo. This broadens the portfolio's analytical presentation while preserving consistent quality checks. Earlier Power BI entries describe the original plan and are superseded by this decision.

Continue the unfinished source-validation stage: purchase reconciliation is the next evidence task. Do not skip to building analytical tables or drawing conversion charts while counting rules remain unresolved.

## 6 November 2026 — Purchase counting remains a sensitivity

Compare full item contents without treating array order as a change in the basket; preserve duplicate rows. The 285 further stored-detail differences comprise 264 metadata-changing groups and 21 order-only groups. Keep metadata-changing and customer/amount-conflicting groups outside a cautious candidate population rather than selecting a convenient first or last record.

The candidate rule retains 4,172 identifier groups; 779 fail native/item amount agreement. Retained purchase events have markedly uneven monthly coverage. Publish this effect and keep raw-event counts separate from candidate groups. No headline orders, revenue, average order value or conversion results are approved. Continue daily tracking, ordering and session-boundary checks before freezing the contract. The SQL, aggregate evidence, native fixture and run receipt accompany the findings.

## 6 November 2026 — Coverage before funnel interpretation

The daily review identifies eighteen dates without cart events despite checkout/purchase activity. Use the full period for coverage diagnostics; justify a comparable date scope before interpreting cart-stage or device differences. Do not fill gaps with invented events or equate missing records with shopper abandonment.

Use strict timestamp progression for the primary candidate and retain a separately labelled tie sensitivity. All mixed-step ties share one bundle and have no populated previous-event timestamp or server offset; those fields cannot resolve the observed ties. Preserve repeated steps and allow a later occurrence to complete the sequence. Session IDs remain identifiers, with analytical dates derived from observed timestamps under an explicit UTC policy.

Publish the nested start/edge population sensitivities and avoid double-counting overlapping exclusions. Crossing midnight is an additional sensitivity, not an automatic data error. Three groups spanning over 24 hours and the linkage of candidate transactions to eligible visits remain to be reviewed. Milestone 1 stays open until scope and monetary definitions are accepted.

## 6 November 2026 — Measurement version 1 accepted

The final [acceptance check](../reports/milestone_1_findings.md) links all 4,172 qualified transaction groups to visits. The three >24-hour groups contain no purchase records. Adopt December 2020 as the primary comparison period based on daily recording coverage, before inspecting device performance. Qualify IDs globally over all 92 days before selecting that cohort. Require a clear start, consistent timestamps/device/context, interior source coverage and one observed UTC date; retain cross-date and all-keyed sensitivities.

The December primary scope has 131,418 visits, 27,289 product-view entries and 2,240 qualified transactions in 1,976 buying visits. Count each qualified ID once, use its earliest timestamp and keep missing/rejected-ID purchases as unresolved outcomes. The within-day choice removes 295 visits after start/consistency rules; it does not declare midnight crossings erroneous.

Permit only the item-agreeing selected recorded-value sum with its coverage (1,851/2,240 qualified transactions). Total revenue, AOV and revenue per visit remain unavailable. Freeze [measurement definitions version 1](metric_contract.md), including explicit denominators, comparative-rate minimum sizes and descriptive sensitivity methods. Milestone 1 is complete; issue #2 can now implement the tables and exclusion ledgers under this bounded contract. No complete revenue assessment, causal claim or analytical-table delivery is implied.

## 6 November 2026 — Reconciled analytical tables

Build eight physical tables with separate event, transaction, item and visit grains, plus disjoint key/visit and purchase-coverage audits. Keep raw event multiplicity, complete transaction qualification over all 92 days, earliest qualified purchase timing, explicit December eligibility and null unsupported monetary outcomes. Item occurrences retain duplicates and do not carry purchase-level selected value.

Use a dedicated private US dataset and fail-if-present table creation. Keep the historical tables unpartitioned because Sandbox's partition expiry could remove 2020–21 data immediately. Observed table retention ends on 5 January 2027. Review every source-backed statement separately; do not treat a script's first DDL estimate as coverage of later statements. Literal-only native fixtures have bounded synthetic inputs, while temporary-table reads still consume the free query quota.

All eight model recomputations match their stored row counts and content checksums without writing a second build. Warehouse assertions and source comparisons preserve the version 1 baselines and unresolved purchases. Add credential-free GitHub validation with artifact retention, code/evidence hash checks and read-only repository permissions. No bot commits or warehouse credentials are required. See the [milestone 2 evidence](../reports/milestone_2_findings.md). Move next to recorded-journey diagnosis, without changing the monetary limits or claiming a commercial opportunity yet.

## 10 November 2026 — Recorded journey diagnosis

Retain contract v1. The largest recorded reduction is from product view to cart across the accepted December populations and timing alternatives. Carry that forward as an investigation across devices. The primary mobile/desktop overall difference remains small after pooled daily-denominator standardisation; it does not justify assuming a mobile problem. Preserve the opposite final-step direction and its date sensitivity. Tablet stays as counts only because later-step bases are small.

Choose the two largest interpretable first-user contexts by entry volume and retain unknown coverage. Do not turn their descriptive differences into session attribution, advertising efficiency or spend advice. Use common-date counts, fixed comparative-rate thresholds and leave-one-date-out ranges as descriptive checks, without confidence intervals or significance claims. Product, intent and repeat-user differences remain unadjusted.

Publish two Python figures and the [stage findings](../reports/milestone_3_findings.md), backed by native fixtures, an independent reverse existence calculation and reconciled input fingerprints. The next issue should compare explicit improvement assumptions and design an experiment after measurement and shopper-research checks. No complete-revenue or recoverable-sales estimate is admitted.
