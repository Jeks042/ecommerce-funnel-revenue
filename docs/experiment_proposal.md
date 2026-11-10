# Product-page cart action: controlled experiment proposal

**Decision proposed:** prepare one product-page test across devices, after verifying event recording and testing the prototype with shoppers. The historical analysis identifies where to investigate; it does not identify a proven design fault. No live experiment has started, and this proposal is not launch-ready.

## The change and the question

Control: the current product-detail page. Candidate treatment: make the Add to cart action more prominent and keep required option choices and inline validation together. Keep price, promotions, availability, cart functionality and checkout policy unchanged. The hypothesis is that a clearer cart action helps visitors who already want a product complete an addition. This is a proposed mechanism, not an observation about the current interface.

Before freezing the variant, audit the current page and event flow, observe representative shoppers attempting the task and review accessibility on desktop and mobile. If that work does not support this mechanism, revise the hypothesis before randomisation. Do not keep changing a running variant. The [opportunity assessment](../reports/opportunity_assessment.md) explains why this is preferable to assuming a mobile-only problem.

## Assignment and eligibility

Use one persistent, first-party visitor ID as the assignment and analysis unit, with a stable 50:50 allocation. Each ID enters once at its first qualifying product-detail-page request, **before** variant rendering or interaction. Use pre-existing consent, bot/internal-traffic and supported-storefront rules established before assignment. Do not require a subsequent click, cart, successful render or purchase to enter the denominator.

Persist the group across return visits and all devices on which the same ID can already be recognised. An anonymous browser ID does not identify a person across devices or after cookie deletion. If that is the available ID, describe the unit as a browser visitor and measure reassignment/contamination; do not claim unique people. Do not invent identity stitching. Keep identifiers and assignment logs inside the production environment.

Include all assigned eligible IDs in their original group, even after failed rendering or switching behaviour: intention to treat. Log assignment separately from actual exposure. Exposure failures and missing records are quality diagnostics, not reasons to remove inconvenient outcomes. Do not apply the historical sample's post-visit consistency or single-date exclusions to trial participants. This trial has its own prospective measurement contract below.

## Outcomes and observation

Primary: the share of assigned eligible visitor IDs with at least one **validated, successful cart addition** in the 7 × 24 hours after first assignment. Count each ID once, across return visits; allow any product. A button click or repeated event alone is not a successful addition. Retain product-level cart events for diagnosis, without changing the primary denominator after seeing results.

Secondary: the seven-day share with a reconciled, qualified purchase, checkout reach and completed-purchase counts. Purchase outcomes require a reliable order ledger and consistent transaction qualification across both groups. Neither a cart addition nor the sample's full observed sequence is a sale. Monetary outcomes stay unavailable until revenue, refunds, tax, shipping and contribution inputs have been admitted separately.

Retain seven full days of follow-up for every assigned ID, then wait for the pre-agreed ingestion/reconciliation delay. Late events need event-time attribution and a frozen cutoff. Absence of an event means no **recorded** outcome only after its observation window and logging checks pass; missing telemetry must not silently become a known behavioural failure. Report unresolved purchases and exposure/outcome coverage by group. A material or differential gap blocks interpretation and triggers repair.

## Guardrails and quality gates

| Check | Required before a decision |
|---|---|
| Allocation | Check assigned-ID counts against the planned 50:50 split; investigate sample-ratio mismatch before interpreting effects. Check exposure and outcome coverage separately. |
| Identity | One assignment per ID; no inconsistent variants; return-visit and cross-device limitations measured. |
| Cart integrity | Successful server-side cart operations reconcile with events; duplicate clicks/events do not inflate success. |
| Purchase protection | Pre-agree an acceptable absolute harm margin, baseline and separately adequate sample for seven-day purchasing visitors. A nonsignificant decline does not establish safety. |
| Reliability and usability | Pre-agree cart error-rate and page/cart latency limits; review accessibility and support complaints. |
| Money and cost | Obtain verified contribution economics and implementation cost before making a financial rollout case. |

Use an A/A pilot to validate assignment, logging, event reconciliation and mature windows before treatment exposure. An A/A pilot cannot prove that later treatment logging is unbiased, so keep the same diagnostics during the A/B test. Sample-ratio mismatch can arise from selection or logging problems; diagnose it rather than deleting users to force balance. [Microsoft's experimentation guidance](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/) supports this quality gate.

## Sample size and timing

The historical 28.85% rate is **cart visits / product-view visits**. It is not the seven-day visitor-level baseline above. Do not use the 27,289 historical visits as 27,289 independent experiment participants, or divide a required visitor count by historical daily visits to promise a duration.

The [versioned planning assumptions](../reports/evidence/scenario-assumptions-v1.json) use hypothetical visitor baselines of 20%, 30% and 40%, absolute effects of 0.5, 1 and 2 percentage points, 50:50 assignment, two-sided alpha 0.05 and 80% power. The [planning output](../reports/evidence/opportunity-analysis-20261110.json) contains all nine combinations. At a **hypothetical 30% baseline**, the approximate required sample is:

| Absolute effect to detect | Visitor IDs per group | Total visitor IDs |
|---|---:|---:|
| +0.5 percentage points | 132,484 | 264,968 |
| +1 point | 33,275 | 66,550 |
| +2 points | 8,394 | 16,788 |

These are normal-approximation planning calculations for a difference from zero, not a powered test that an effect exceeds a business-value threshold. They assume independent IDs, complete follow-up and a stable design. The method uses pooled variance under the null and separate variances under the alternative, matching [statsmodels' two-proportion power method](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.power_proportions_2indep.html). All nine selected integer samples and their preceding integers were checked against statsmodels 0.15.0. No measured sample effect or historical significance test is presented.

Before launch, estimate the actual seven-day control rate and newly eligible visitor-ID volume from production/A/A data. Agree the smallest effect worth detecting using implementation cost, downstream evidence and contribution economics. Recompute sample size, check guardrail feasibility, then freeze the required sample **and** an enrolment end date covering at least two complete weekly cycles. Allow enough time for seven-day follow-up plus ingestion delay. If traffic cannot support the design, choose a larger meaningful effect, a different decision or no test; do not manufacture precision by counting return visits independently.

## Prospective analysis contract — version 1

This is a future trial plan, separate from historical measurement contract v1. Historical definitions and descriptive results are unchanged. Before launch, freeze the variant, ID policy, eligibility, observation windows, primary outcome, practical target, harm margins, sample and end date in a dated registration.

At the fixed endpoint, compare one binary primary outcome per assigned ID. Report group successes/denominators, treatment-minus-control percentage points, a two-sided pooled two-proportion z test at alpha 0.05 and a pre-specified large-sample 95% difference interval. The simple interval uses the separate group variances; check its approximation conditions before use. If sparse outcomes or dependent assignment units invalidate the method, revise the registration and planning before launch rather than selecting a method after seeing effects. No future outcome-analysis engine or interval has been run in this repository.

Use one confirmatory primary outcome and a fixed-sample analysis. Device and acquisition-context subgroups are exploratory; do not select a winning segment after looking at results. Secondary outcomes and safety measures cannot become an alternative primary success claim. Pre-specify how multiple guardrail comparisons will be handled and power their harm margins; this approval is a launch requirement, not something the historical sample supplies.

Operational checks may run daily. Stop exposure for a serious reliability, accessibility, allocation or tracking failure; log the stop and treat that run as interrupted, not as a successful efficacy test. Do not stop early because the primary p-value first crosses 0.05, or extend enrolment after inspecting it. If the frozen sample is not reached by the frozen date, report an underpowered/inconclusive result. No sequential efficacy method is assumed.

## Decision rules

| Result | Decision supported |
|---|---|
| Quality gate fails | Repair and reassess; no treatment-effect conclusion. |
| Clear primary improvement, agreed practical target met, and adequately tested guardrails pass | Consider a controlled rollout only after purchase and contribution evidence support it; a cart effect alone is not a revenue case. |
| More carts, but purchase harm is detected or safety remains unresolved | Do not declare commercial success; investigate or continue a separately justified study. |
| Estimate is small, imprecise or below the practical target | Do not roll out on the strength of this test; document the uncertainty and revisit the mechanism/cost. |

A significant difference from zero does not prove that the true effect exceeds the practical target. Report that distinction when deciding. The live visitor baseline, identity reliability, guardrail margins, contribution inputs, variant research and calendar plan remain unavailable. Completing this **proposal** does not authorise a live test or establish its results.
