# Where to investigate, and what an improvement could mean

**Prioritise checking the product-view-to-cart journey across devices.** First verify that successful cart additions are being recorded, then use shopper research to decide whether the proposed page change addresses a real obstacle. The evidence supports this investigation; it does not support a revenue forecast or a redesign chosen solely because a device has a lower rate.

The primary historical sequence contains 27,289 product-view visits, 7,874 carts, 2,819 checkouts and 1,437 qualified recorded completions. Separately, 1,976 of all 131,418 eligible visits have a qualified transaction, with 92 visits containing unresolved purchase records. Those are December 2020 observations under the accepted rules, not today's addressable customers.

## Priorities for a product team

| Order | Work | Evidence and decision | Effort and uncertainty |
|---|---|---|---|
| Prerequisite | Audit recording and purchase linkage | Earlier zero-cart dates and unresolved purchases make measurement checks essential before a product test. Verify successful cart operations against event logs and qualified purchases against an order ledger. | Engineering discovery; actual time/cost unavailable. Repair tracking before interpreting a treatment difference. |
| 1 | Research product view to cart, across devices | This is the largest recorded reduction: 19,415 of 27,289 entry visits do not reach a later cart. The relative step ranking survives counting/population alternatives. | Review the current page and observe shopper tasks. Intent, product availability and recording gaps could explain part of the reduction; it is not a pool of recoverable shoppers. |
| 2 | Investigate cart to checkout | 5,055 of 7,874 ordered cart visits do not reach later checkout. Keep this as a separate question rather than adding an assumed improvement to the first case. | Journey research and engineering estimates needed. Avoid changing several steps in one test. |
| 3 | Validate checkout and purchase linkage | There are 1,382 visits without a later qualified completion among 2,819 checkouts; 70 checkout visits contain unresolved purchases. | Reconcile the recording before attributing the difference to checkout design or payment failure. |
| Defer | A mobile-only redesign or acquisition-budget change | Mobile has no broad recorded disadvantage; first-user source/medium is not the source of the current visit. | No causal/device or marketing-return case. No implementation budget or spend recommendation supported. |

This is an evidence-led investigation order, not an impact/effort score with invented costs. No measured benefit, delivery estimate or financial allocation has been approved.

## Conditional arithmetic, not a forecast

Use the fixed 27,289 product-view visits as a **reference cohort size**, not as next month's traffic. Assume an absolute change in view-to-cart progression of +0.5, +1 or +2 percentage points. The labels low/base/high identify sensitivity cases; none has a probability or a claim of being most likely. Include no-change and −1-point downside cases.

The observed strict completion-to-cart ratio is 1,437 / 7,874 (18.25%). For the additional or removed cart visits only, assume downstream progression of 0%, 50% or 100% of that ratio. Existing downstream behaviour is otherwise held fixed. These are assumptions about marginal visits; the historical average does not establish how newly encouraged visitors would behave.

| Assumed absolute cart-rate change | Additional cart-visit equivalents | Additional completion equivalents: zero downstream progression | At half the historical ratio | At the historical ratio |
|---|---:|---:|---:|---:|
| −1 point — downside | −272.89 | 0.00 | −24.90 | −49.80 |
| 0 — no change | 0.00 | 0.00 | 0.00 | 0.00 |
| +0.5 points — low | 136.45 | 0.00 | 12.45 | 24.90 |
| +1 point — base | 272.89 | 0.00 | 24.90 | 49.80 |
| +2 points — high | 545.78 | 0.00 | 49.80 | 99.60 |

Fractions are scenario arithmetic, not observed fractional people or orders. A completion equivalent is a hypothetical visit completing the **recorded sequence**. It is not an incremental sale, transaction or financial return. The displayed range is not a confidence interval, probability bound or maximum possible impact. More carts could coexist with worse purchasing behaviour; that net harm is outside this hold-other-behaviour-fixed grid and is a reason for purchase guardrails.

For each row:

`additional carts = reference product-view visits × assumed absolute rate change`

`additional recorded completions = additional carts × (1,437 / 7,874) × assumed downstream multiplier`

Do not multiply cart gains by both the full completion/cart ratio and each of its checkout/purchase factors: that would count downstream progression twice. Do not add separate step opportunities for overlapping visits. The current model changes one step only.

## What would justify commercial action

The [experiment proposal](../docs/experiment_proposal.md) tests one candidate product-page change with stable visitor-level assignment and seven-day outcomes. Its sample-size illustrations deliberately use assumed **visitor** baselines rather than recycling a visit rate. Purchase protection and tracking quality remain necessary even when the cart metric improves.

A financial case needs verified incremental purchase behaviour, reconciled sales/refunds/costs, contribution per incremental outcome and implementation/operating cost. Those inputs are unavailable here. The selected item-agreeing recorded-value subset cannot supply total revenue or AOV. No currency values, profit, ROAS, budget approvals or payback estimates are calculated.

The [assumption file](evidence/scenario-assumptions-v1.json), [15 scenario outputs and nine power illustrations](evidence/opportunity-analysis-20261110.json), [statistical reference checks](evidence/power-reference-20261110.json) and [execution receipt](evidence/opportunity-receipt-20261110.json) make the arithmetic reviewable. Run `python src/assess_opportunity.py` to regenerate it. It uses already accepted aggregates, so this stage writes no new warehouse data and exports no identifiers.
