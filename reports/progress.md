# Project progress

Updated: 10 November 2026.

**Milestones 1–4 are complete.** [Journey findings](milestone_3_findings.md) identify the product-view-to-cart step as the first investigation question. The [scenario and experiment stage](milestone_4_findings.md) now sets out the assumed scale of improvement and how one candidate change could be tested. This does not establish abandonment, a cause or recoverable sales.

The December primary sequence is 27,289 product-view visits → 7,874 carts → 2,819 checkouts → 1,437 qualified recorded completions. Separately, 1,976 of 131,418 eligible visits contain a qualified purchase. The 92 visits containing unresolved purchases remain visible. Total revenue, AOV and revenue per visit remain unavailable.

Mobile's overall recorded progression is slightly higher than desktop's; the date-standardised difference is +0.28 percentage points. Checkout-only progression points the other way and is date-sensitive. First-user context comparisons remain descriptive, with 35,754 eligible visits lacking interpretable context. No device redesign or advertising allocation is justified by these associations alone.

Two reviewed Python figures are available as PNG and SVG. Native edge-case fixtures, a separate backwards calculation across all 93 primary device/date cells, model fingerprints and prior-baseline reconciliation support the findings. Credential-free validation reproduces the summary, reconciles chart data and checks code/evidence/asset freshness. [Methods and reproduction](../docs/funnel_analysis.md) document the detail.

## Scenarios and test design

The [opportunity assessment](opportunity_assessment.md) includes 15 cases, with no-change/downside and explicit downstream assumptions. A hypothetical +1-point cart change gives 272.89 additional cart-visit equivalents and 0–49.80 additional full-sequence completion equivalents under the specified hold-other-behaviour-fixed cases. Those are not incremental sales or probability bounds.

The [experiment proposal](../docs/experiment_proposal.md) uses stable visitor IDs and seven-day outcomes. Nine power illustrations use hypothetical visitor baselines, independently checked against statsmodels; the observed visit rate does not supply that baseline. The live baseline, business target, guardrail margins, prototype research, identity reliability and duration remain launch requirements. No trial has begun.

## Next: illustrated report and decision memo

[Issue #5](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/5) can assemble the reviewed Python figures, observed findings and conditional scenarios into a clear commercial report and memo. Keep assumptions visibly separate from observations and explain the evidence needed to proceed. Milestones 5–6 remain open; independent reproduction and the public case-study release belong to milestone 6. No portfolio/CV publication is implied by the current stage.

The eight Sandbox tables expire on 5 January 2027. Reviewed aggregates and executable SQL remain in GitHub. Configuration, source identifiers and full job references stay private. Workflows retain validation artifacts, use no warehouse credentials and create no bot commits.
