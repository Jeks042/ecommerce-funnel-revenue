# Decision memo: investigate product view to cart across devices

**Recommendation:** verify recording and research the product-view-to-cart journey before committing to a redesign. If the research supports it, test one clearer cart action across devices. The current evidence does not justify a mobile-only redesign, advertising-budget reallocation or a revenue claim.

This independent analysis uses Google's historical e-commerce sample, primarily December 2020. It does not describe current shop performance. The [illustrated report](commercial_report.md) provides the supporting figures.

## Why this is the first investigation

Of 27,289 eligible product-view visits, 7,874 reach a later cart, 2,819 reach checkout and 1,437 complete the full sequence with a purchase that passes the counting checks. Product view to cart has the largest recorded reduction: 19,415 visits, with 28.9% progressing. The priority survives alternative timing and population rules.

The records do not establish why the next step is absent. Eighteen November dates have no cart events despite continued checkout/purchase recording, so December is the narrower comparison period. Ninety-two eligible December visits contain unresolved purchases. These gaps are not a measured pool of lost sales.

Mobile's overall recorded progression is slightly above desktop's; the difference remains only +0.28 percentage points after giving both the same daily mix. The final checkout step points the other way and is date-sensitive. That pattern supports research across devices, not assuming a mobile problem.

## What to commission next

1. **Recording check:** reconcile successful cart additions and qualified purchase IDs with reliable operational records. Resolve material gaps before relying on a treatment difference.
2. **Shopper research:** review the current product page and observe cart tasks on desktop and mobile. Confirm the mechanism before freezing a variant; implementation time and cost are not yet known.
3. **A controlled test if supported:** assign each persistent visitor ID to one group, follow it for seven days and check successful cart additions alongside purchase, reliability and accessibility safeguards. Establish the live baseline, meaningful target, sample and duration before launch. The [proposal](../docs/experiment_proposal.md) records the detail.

## Scale, limits and decision gate

An assumed one-percentage-point cart improvement means about 273 additional cart visits in a cohort the size of this sample. Under the separate downstream assumptions, the arithmetic gives zero to about 50 additional visits completing the recorded sequence. These are hypothetical cases, not predicted purchases or probability bounds. Cart gains could coexist with purchase harm.

Proceed towards a rollout only when a trustworthy test supports a practically useful improvement, adequately tested safeguards pass and purchase/contribution evidence justifies the cost. An inconclusive result or unresolved purchase safety is not a green light. Total revenue, AOV and financial return remain unavailable; no budget, launch or live-test result is approved by this study.

[Scenario assessment](opportunity_assessment.md) · [Measurement definitions](../docs/metric_contract.md) · [Report and figure reproduction](../docs/report_reproduction.md)
