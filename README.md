# E-commerce Funnel & Revenue Analytics

**Measurement checks complete; analytical tables next.** The study now has agreed rules for examining recorded shopping journeys in December 2020.

Which parts of the shopping journey should a product team investigate first, and what evidence would justify an experiment?

I am examining how shoppers move from viewing a product to making a purchase, which differences deserve closer investigation, and what a product team should test next. BigQuery SQL will provide the analytical tables. Python analysis and charts will present the findings in an illustrated commercial report.

The first finding is about what the records can tell us. Eighteen dates in November have no cart records even though checkout and purchase activity continued. Treating that gap as shoppers abandoning their baskets would give a misleading picture. I have chosen December as a narrower comparison period and will show how the results change under alternative counting rules.

Within that scope, 131,418 visits meet the agreed recording rules, including 27,289 with a product view. Repeated purchase records count once, and uncertain purchases remain visible. Some purchase and item values still disagree, so total revenue and average order value are unavailable. [Read the measurement findings](reports/milestone_1_findings.md) for the decisions and their limits.

The next stage turns these rules into repeatable analytical tables. The analysis will then examine which recorded steps deserve investigation and what a product team would need to test before acting. No commercial recommendation or measured sales improvement has been established yet.

## Planned workflow

Source audit and metric contract → event/session/purchase SQL marts → ordered funnel analysis → opportunity scenarios and experiment proposal → Python charts and decision memo → independent reproduction.

The source is Google's historical, obfuscated e-commerce sample for November 2020–January 2021. The full period supports source checks; December is the agreed scope for the primary journey analysis. It does not represent current trading performance.

## Milestones

1. [Validate GA4 access, source quality and metric definitions](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/1) — complete
2. [Build reproducible event, session and purchase SQL marts](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2) — planned
3. [Diagnose conversion funnels and segment differences](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/3) — planned
4. [Prioritise revenue opportunities and propose an experiment](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/4) — planned
5. [Build Python charts and a commercial decision memo](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/5) — planned
6. [Reproduce, review and publish the completed case study](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6) — planned

[View the six GitHub milestones](https://github.com/Jeks042/ecommerce-funnel-revenue/milestones). Each has an issue recording its work, acceptance checks and dependencies.

## Start here

- [Business brief](docs/business_brief.md)
- [Source access and handling](docs/data_access.md)
- [Agreed measurement definitions](docs/metric_contract.md)
- [Measurement findings and scope decision](reports/milestone_1_findings.md)
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

Source profiling, purchase linkage and the reviewed measurement evidence are available. Analytical tables, funnel diagnosis and the Python report will follow their milestone checks.

## Evidence boundaries

This is a historical observational study. Funnel differences do not establish why shoppers leave or what intervention will increase revenue. Scenario values will be labelled assumptions. Obfuscation, missing identifiers, short coverage and instrumentation gaps constrain interpretation.

Publish reviewed aggregate evidence only. Keep raw events, customer/session identifiers, credentials and unrelated personal planning outside this repository.

## Author

Chukwujekwu Joseph Ezema · [Portfolio](https://jeks042.github.io/) · [GitHub](https://github.com/Jeks042)

Completed companion studies: [A/B Testing & Incremental Revenue](https://github.com/Jeks042/ab-testing-incremental-revenue) · [Subscription Churn & Retention](https://github.com/Jeks042/subscription-churn-retention).
