# Measurement definitions — version 1

Accepted on 6 November 2026 for analysis of recorded shopping journeys. The [acceptance report](../reports/milestone_1_findings.md) documents the evidence and the restricted go decision. This contract does not certify the sample as real sales or complete tracking.

## Period and eligible visits

Use all 92 source days, 1 November 2020–31 January 2021, when qualifying transaction identifiers. Apply the analysis cohort **after** that qualification. A conflicting identifier must not become acceptable because its other observation falls outside the reporting month.

The primary comparison period is **December 2020**, chosen because it is a complete calendar month without the zero-cart dates observed in November. It is a bounded historical comparison, not evidence that December tracking is complete or representative of other months. November and January remain coverage diagnostics. Do not combine them into a headline cart funnel or infer a trading trend from their differences.

One visit is a composite `user_pseudo_id` / `ga_session_id` group. A usable user key is nonblank and not `<Other>` or `(not set)`. Extract the session parameter only if it occurs exactly once, contains an integer and is positive. Do not convert the ID into a start timestamp.

Primary eligibility requires:

- Exactly one `session_start`, at the first usable observed timestamp.
- Usable positive event timestamps and agreement between UTC timestamp date, event date and source table suffix.
- One device value and one first-user source/medium combination, retaining null as an explicit unknown value.
- No event on either outer source date, 1 November or 31 January.
- All observed events within one UTC date, with the first timestamp in December.

UTC is an analytical convention verified against these records; no unverified shop timezone is asserted. Excluding cross-date groups is a conservative scope choice, not a claim that crossing midnight invalidates a GA4 session. Retain `anchored_interior` (allow cross-date groups) and `all_keyed` as separate sensitivity populations. Keep their counts and exclusions visible; do not pool their denominators.

## Event and purchase treatment

Retain source events at their original grain. Equal event names/timestamps do not establish duplicate events. Extract nested parameters and item summaries with correlated subqueries; never join every event to every item for event/session counting.

One **qualified recorded transaction** is one nonplaceholder transaction-ID group passing the [complete purchase rule](purchase_counting_review.md) over all 92 days: one customer/session identity, currency/monetary summary, complete e-commerce payload, sorted complete-item multiset, observed purchase date and device; usable customer/session keys; and an unambiguous `USD` currency parameter. Sorting retains duplicate item rows. Reject conflicting groups in full. Do not choose a convenient first/last payload to resolve disagreement.

For a qualified ID with repeated observations, count it once and use its **earliest** recorded purchase timestamp for the primary chain. A replay after checkout cannot manufacture a new conversion. Keep latest-observation timing as a diagnostic sensitivity. Count several qualified IDs in one visit as several transactions but only one buying visit. Missing-ID and rejected-ID events remain separate unresolved outcomes, including visits that contain both qualified and unresolved purchases. Do not silently recode those visits as known nonbuyers.

## Measures and denominators

| Measure | Definition |
|---|---|
| Eligible visits | Count of primary eligible composite groups, including visits with no product-view event. |
| Product-view entries | Eligible visits with at least one usable `view_item` timestamp. This is the funnel denominator. |
| Ordered cart / checkout | From the earliest view, choose the earliest cart strictly later, then the earliest checkout strictly later than that cart. Repeated steps can complete the chain. |
| Ordered recorded purchase | At least one qualified transaction's earliest purchase timestamp strictly after the selected checkout, in the same eligible visit. Count each visit once. |
| Step progression | Next selected-step visit count / preceding selected-step visit count. A zero denominator produces unavailable, not zero. |
| Entry-to-purchase progression | Ordered recorded-purchase visits / product-view entry visits. |
| Recorded buying-visit share | Eligible visits with at least one qualified transaction / all eligible visits, independent of whether the full funnel is observed. This is not total true conversion. |
| Qualified transaction count | Distinct qualified IDs belonging to eligible visits, independent of funnel completion. Label as recorded transactions, not verified sales. |
| Unresolved purchase coverage | Missing-ID and rejected-ID event counts, affected visits and visits containing both qualified and unresolved records. Publish alongside the above measures. |

The chain is a visit-level progression measure. It does not require the same product at every step and does not establish that a product was abandoned. Do not infer within-timestamp order from event names, array position or bundle ID. Run the equivalent `>=` chain as a labelled sensitivity; available source fields cannot resolve the observed ties. Raw-purchase-event completion remains a separate recording diagnostic and does not inherit the qualified-ID definition.

## Money

The only supported monetary summary is **recorded purchase value (USD), item-agreeing selected subset**: sum each qualified ID once when native purchase revenue is finite and nonnegative, the item array is nonempty, every item revenue is finite/present and the native/item sum differs by at most $0.01. Show both the selected transaction count and total qualified count in the same scope. Do not replace missing native amounts with the USD field.

This selected sum is not total shop revenue. Total sales revenue, gross/net revenue, average order value, revenue per visit, profit and advertising return are **unavailable**. No refunds were observed and shipping coverage is absent; these observations do not establish zero refunds or costs. No missing/excluded monetary outcome is filled with zero. Scenarios using assumed values must identify them as assumptions and must not reuse this selected sum as complete sales or a recoverable-revenue estimate.

## Comparisons and uncertainty

Device is assigned at visit grain; unknown values remain visible. `traffic_source.source` / `medium` describes **first-user acquisition context**, not session acquisition, spend efficiency or causal attribution. Stable unknown context can remain eligible; report its coverage before considering context comparisons.

Use a common December scope and check daily composition before ranking device/context differences. For a displayed comparative rate, require at least 500 visits in that rate's denominator and at least 30 observed successes and 30 other visits in each compared group. Smaller groups retain counts and a small-base label, without a ranked rate. These reporting thresholds are chosen for stability and readability; they are not a power calculation or proof of representativeness.

Version 1 uses counts, unresolved-outcome coverage and strict/tied, start and cross-date sensitivity ranges to express uncertainty. No population significance or formal confidence interval is claimed. Any later inferential method needs an explicit amendment, must account for repeat users and must keep identifiers inside the warehouse. Sensitivity cannot repair missing tracking or obfuscation. An observed difference is an investigation question, not a measured intervention effect.

## Acceptance and change control

The [measurement gate SQL](../sql/07_measurement_gate.sql) links the purchase rule to the audited visit populations without row multiplication. The [saved ledger](../reports/evidence/measurement-scope-20261106.json), native fixture and [receipt](../reports/evidence/measurement-gate-receipt-20261106.json) record impacts and validation. [Reproduction instructions](measurement_gate.md) accompany the implementation.

Milestone 2 may now build the analytical tables under these definitions. Its acceptance still requires reconciled event, visit, transaction and exclusion tables; no tables or analytical findings are implied by this contract. Any change to period, eligibility, purchase rule, money or ordering requires a versioned decision and regenerated evidence before reporting.

The [prospective experiment proposal](experiment_proposal.md), prepared on 10 November 2026, defines a separate version 1 visitor-level, seven-day trial plan. Its assumed power calculations do not amend this historical visit contract or add significance claims to the sample. Retrospective single-date and post-visit consistency exclusions must not be applied after randomisation in a future trial.
