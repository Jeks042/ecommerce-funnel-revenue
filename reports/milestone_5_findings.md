# Commercial report and decision memo

The [illustrated report](commercial_report.md) and [decision memo](decision_memo.md) are complete. They lead with the recommendation to investigate product view to cart across devices, verify recording and understand shopper tasks before committing to a change. The report explains the evidence; the memo gives a product or e-commerce lead the shorter decision and the conditions for acting.

## What changed

Four Python figures now support the report:

- **Recording coverage:** why December is the primary comparison period. Source-event counts and observed zero-cart dates stay separate from visit conversion.
- **Recorded journey:** explicit nested visit counts and progression from each preceding step.
- **Device comparison:** observed counts, a common daily mix and date sensitivity, with no claim of a causal device effect.
- **Conditional scenarios:** low/base/high, no-change and downside cases under three explicit downstream assumptions. The figure is labelled hypothetical and does not imply sales, financial return or probability bounds.

The two accepted journey/device figures were reused and regenerated without changing their source or published assets. Daily coverage and the scenario matrix add decision context; further acquisition-context or sensitivity charts would repeat the text without strengthening the recommendation. Technical detail remains in the supporting methods.

## What was checked

All 57 regression tests passed. Chart data reconcile to the reviewed SQL aggregates and scenario outputs. The recording figure requires all 92 dates and three devices exactly once; missing/null counts are rejected rather than filled with zero. All 15 scenario cells are required, with explicit decimal rounding. Input, code, report-document and eight asset hashes reconcile, and report links resolve.

One documented command regenerates all four figures as eight PNG/SVG files in an ignored review directory. On the accepted Windows environment, the four original files reproduced byte for byte. Numeric chart data must match on other platforms, while raster/font bytes may differ. Final layouts were reviewed for legible labels, explicit units, no overlaps and clear distinction between observed data and assumptions.

The existing analytical workflow remains unchanged and discovers the new report tests. A separate read-only workflow actually renders the figures with pinned dependencies, validates the outputs and retains the regenerated figures and build manifest for 30 days. Neither workflow needs warehouse credentials or creates bot commits. The [reproduction guide](../docs/report_reproduction.md) and [report receipt](evidence/report-receipt-20261110.json) provide the detail.

## Decision and limits

The report recommends an investigation, not a proven fix. Missing next steps do not establish abandonment, and the small device differences do not justify a mobile-only response. The sample is historical and obfuscated. Unresolved purchases, incomplete monetary evidence, unadjusted visitor/product mix and the lack of a live experiment still limit the commercial conclusion.

Total revenue, AOV, financial return and a live-test duration remain unavailable. No new warehouse query or inference was introduced. The prospective trial still needs production tracking, visitor baseline, practical target, guardrail margins and a frozen variant before launch.

## Next

[Milestone 6](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6) can now independently reproduce the complete evidence chain, review the final public presentation and prepare the case-study/portfolio release. This reporting milestone does not claim that final release review or a portfolio update has already happened.
