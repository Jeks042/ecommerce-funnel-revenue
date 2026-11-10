# An investigation worth testing, with its assumptions made clear

**The next product decision is to investigate the move from viewing a product to adding it to the cart, across devices.** Check recording first, observe shopper tasks and then decide whether to test a clearer cart action. The analysis does not yet justify a redesign budget, advertising reallocation or a revenue forecast.

I translated the [recorded-journey findings](milestone_3_findings.md) into a small set of improvement scenarios and one controlled experiment proposal. The practical distinction is between the size of a question and the value of a proven intervention. The largest recorded gap gives us a place to look; it does not tell us what we can recover.

## What the scenarios tell us

For a reference cohort the size of December's 27,289 product-view visits, an assumed **one-percentage-point increase** in view-to-cart progression produces about **273 additional cart visits**. If those additional visits progress at half the historical cart-to-completion ratio, the arithmetic gives about 25 more visits completing the recorded sequence. At the full historical ratio it gives about 50; with no downstream progression it gives zero.

These are conditional calculations, not predicted customers, sales or measured uplift. Cart gains could also coexist with purchase harm. The [opportunity assessment](opportunity_assessment.md) shows all low/base/high, no-change and downside cases, plus why separate step opportunities must not be added together. Total revenue, AOV and financial return remain unavailable.

## What the proposed test would establish

The candidate change makes the cart action and required product options clearer. The current interface and shopper behaviour have not been audited, so this mechanism needs confirmation before a variant is frozen.

The [proposal](../docs/experiment_proposal.md) assigns each persistent visitor ID to one group and follows it for seven days, including return visits. It asks whether a larger share makes a successful cart addition. Purchase protection, event reconciliation, reliable assignment and performance checks constrain any rollout decision. A cart-only improvement would not establish a commercial return.

The power illustrations keep experiment visitors separate from historical visits. Under a **hypothetical 30% visitor-level baseline**, detecting a one-point increase with the stated two-sided 5% test and 80% power requires approximately 33,275 IDs per group. This is not a final launch sample. The live visitor baseline, meaningful business target, harm margins, identity reliability and traffic volume must be established first. No test duration is promised from the historical visit totals.

## Work delivered and checked

- An evidence-led order for recording checks, product-page research, cart/checkout investigation and deferred device/marketing actions.
- Fifteen reproducible scenarios covering five cart assumptions and three downstream assumptions. Observed counts, assumed changes and unavailable money are explicit.
- A versioned prospective experiment plan with eligibility, assignment, exposure, outcomes, repeat-visitor treatment, quality gates, stopping and decision rules.
- Nine sample-size illustrations checked against statsmodels 0.15.0; for each, the selected integer reaches the planning-power target and the preceding integer does not.
- Regression checks for percentage-point arithmetic, no gain, downside, infeasible populations, sample-size behaviour, independent statistical references and unavailable outcomes. Credential-free CI reproduces the outputs and checks their hashes alongside the accepted historical evidence.

No new warehouse query was needed: the scenarios use the already accepted aggregates. No production system, tracking, experiment or customer record was changed. Historical measurement contract v1 and its uncertainty limits remain in force; the prospective trial design is separately versioned and has not been used to infer effects from this sample.

All 51 local regression tests passed. Thirty independent rational-arithmetic checks reconcile the scenario outputs through the separate checkout and purchase steps. Eighteen statistical-library power evaluations reconcile the nine sample-size illustrations and their preceding integers. The [planning receipt](evidence/opportunity-receipt-20261110.json) binds the reviewed inputs, code and outputs; the existing historical evidence checks remain intact.

## Next deliverable

[Milestone 5](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/5) can now assemble the illustrated commercial report and decision memo, using the reviewed Python figures and the explicit scenarios. Lead with the recommended investigation and what evidence would justify acting. Keep hypothetical values visibly distinct from observed findings. The final independent reproduction and portfolio release remain milestone 6.
