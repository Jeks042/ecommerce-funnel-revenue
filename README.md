# E-commerce Funnel & Revenue Analytics

**Recorded journey analysis complete; experiment design next.**

Where should a product team investigate the shopping journey first?

I examined how visits progressed from viewing a product to adding it to a cart, starting checkout and making a recorded purchase. The study uses Google's historical e-commerce sample, with December 2020 chosen after checking the quality of the records.

The largest recorded gap is before the cart: 7,874 of 27,289 product-view visits reached that next step. Only 1,437 completed the full observed sequence. That gives the product team a focused research question, but it does not explain why people stopped or establish how many sales could be recovered.

Mobile does not show a broad disadvantage. Its recorded progression from view to purchase is 5.41%, compared with 5.16% on desktop. Giving both groups the same daily mix leaves a small difference of 0.28 percentage points. The final checkout step points in the other direction, so a mobile-only redesign would be premature.

![Recorded shopping progression](reports/figures/recorded_journey.png)

[Read the journey findings](reports/milestone_3_findings.md) for the device comparison, alternative counting rules and the questions to carry into experiment design.

Before drawing these findings, I checked missing steps, repeated purchase records and uncertain identifiers, then built separate analytical tables for events, visits, purchases and basket items. Eighteen November dates had no cart records despite checkout and purchase activity, so I kept those dates out of the primary comparison. Some monetary records also disagree; total revenue and average order value remain unavailable.

BigQuery SQL provides the data foundation and checks. Python with Matplotlib and Seaborn produces the charts directly from reviewed totals. Detailed methods sit in the supporting docs. The next stage will set out improvement assumptions and a controlled experiment; no sales uplift or commercial return has been measured.

## Planned workflow

Source audit and metric contract → event/session/purchase SQL marts → ordered funnel analysis → opportunity scenarios and experiment proposal → Python charts and decision memo → independent reproduction.

The source is Google's historical, obfuscated e-commerce sample for November 2020–January 2021. The full period supports source checks; December is the agreed scope for the primary journey analysis. It does not represent current trading performance.

## Milestones

1. [Validate GA4 access, source quality and metric definitions](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/1) — complete
2. [Build reproducible event, session and purchase SQL marts](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2) — complete
3. [Diagnose conversion funnels and segment differences](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/3) — complete
4. [Prioritise revenue opportunities and propose an experiment](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/4) — planned
5. [Build Python charts and a commercial decision memo](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/5) — planned
6. [Reproduce, review and publish the completed case study](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6) — planned

[View the six GitHub milestones](https://github.com/Jeks042/ecommerce-funnel-revenue/milestones). Each has an issue recording its work, acceptance checks and dependencies.

## Start here

- [Business brief](docs/business_brief.md)
- [Source access and handling](docs/data_access.md)
- [Agreed measurement definitions](docs/metric_contract.md)
- [Measurement findings and scope decision](reports/milestone_1_findings.md)
- [Analytical foundation and reconciliation](reports/milestone_2_findings.md)
- [Recorded journey findings](reports/milestone_3_findings.md)
- [Funnel methods and Python reproduction](docs/funnel_analysis.md)
- [SQL workflow and reproduction](docs/sql_workflow.md)
- [Delivery workflow and acceptance gates](docs/workflow.md)
- [Current progress and next session](reports/progress.md)
- [Source audit and current decisions](reports/source_audit.md)
- [Purchase-reconciliation findings](reports/purchase_reconciliation.md)
- [Purchase-detail findings and counting sensitivity](reports/purchase_detail_findings.md)
- [Tracking coverage, timing and population findings](reports/tracking_timing_findings.md)
- [Python chart and report plan](docs/chart_specification.md)
- [Decision log](docs/decision_log.md)

## Planned outputs

| Location | Purpose |
|---|---|
| docs/ | Scope, measurement definitions, workflow and decisions |
| sql/ | BigQuery profiling, staging, marts and analytical queries |
| tests/ | Synthetic edge cases and reconciliation checks |
| reports/ | Validated aggregate findings and decision records |
| src/ | Python analysis and chart-generation code |
| reports/figures/ | Reviewed PNG and SVG charts generated from approved aggregates |

Source checks, analytical tables and recorded-journey findings are available. Commercial scenarios, experiment design and the final illustrated report follow their milestone checks.

## Evidence boundaries

This is a historical observational study. Funnel differences do not establish why shoppers leave or what intervention will increase revenue. Scenario values will be labelled assumptions. Obfuscation, missing identifiers, short coverage and instrumentation gaps constrain interpretation.

Publish reviewed aggregate evidence only. Keep raw events, customer/session identifiers, credentials and unrelated personal planning outside this repository.

## Author

Chukwujekwu Joseph Ezema · [Portfolio](https://jeks042.github.io/) · [GitHub](https://github.com/Jeks042)

Completed companion studies: [A/B Testing & Incremental Revenue](https://github.com/Jeks042/ab-testing-incremental-revenue) · [Subscription Churn & Retention](https://github.com/Jeks042/subscription-churn-retention).
