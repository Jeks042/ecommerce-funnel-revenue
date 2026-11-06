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
