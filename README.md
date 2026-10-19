# E-commerce Funnel & Revenue Analytics

**In progress: source checks.** The first audit covers 4.30 million events across all 92 days. Purchase-counting and measurement rules are still being resolved before funnel analysis begins.

Which parts of the shopping journey should a product team investigate first, and what evidence would justify an experiment?

I am examining how shoppers move from viewing a product to making a purchase, which differences deserve closer investigation, and what a product team should test next. BigQuery SQL will provide the analytical tables and Power BI will present the findings.

The first checks found missing and repeated purchase identifiers, incomplete money fields and events that share a timestamp. Those details affect how visits, orders and progression can be counted. [Read the source audit](reports/source_audit.md) for the observations and the decisions still to make. There are no accepted funnel or revenue findings yet.

## Planned workflow

Source audit and metric contract → event/session/purchase SQL marts → ordered funnel analysis → opportunity scenarios and experiment proposal → Power BI and decision memo → independent reproduction.

The source is Google's historical, obfuscated e-commerce sample for November 2020–January 2021. It supports an investigation of recorded shopping activity; it does not represent current trading performance. Milestone 1 must establish which measures are reliable enough to use.

## Milestones

1. [Validate GA4 access, source quality and metric definitions](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/1) — in progress
2. [Build reproducible event, session and purchase SQL marts](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2) — planned
3. [Diagnose conversion funnels and segment differences](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/3) — planned
4. [Prioritise revenue opportunities and propose an experiment](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/4) — planned
5. [Build a reconciled Power BI report and decision memo](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/5) — planned
6. [Reproduce, review and publish the completed case study](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6) — planned

[View the six GitHub milestones](https://github.com/Jeks042/ecommerce-funnel-revenue/milestones). Each has an issue recording its work, acceptance checks and dependencies.

## Start here

- [Business brief](docs/business_brief.md)
- [Source access and handling](docs/data_access.md)
- [Draft metric contract](docs/metric_contract.md)
- [Delivery workflow and acceptance gates](docs/workflow.md)
- [Current progress and next session](reports/progress.md)
- [Source audit and current decisions](reports/source_audit.md)
- [Decision log](docs/decision_log.md)

## Planned outputs

| Location | Purpose |
|---|---|
| docs/ | Scope, measurement definitions, workflow and decisions |
| sql/ | BigQuery profiling, staging, marts and analytical queries |
| tests/ | Synthetic edge cases and reconciliation checks |
| reports/ | Validated aggregate findings and decision records |
| dashboard/ | Power BI model, measures and presentation evidence |

Source profiling SQL and its reviewed aggregate evidence are available. Analytical tables, funnel results and the dashboard will follow their milestone checks.

## Evidence boundaries

This is a historical observational study. Funnel differences do not establish why shoppers leave or what intervention will increase revenue. Scenario values will be labelled assumptions. Obfuscation, missing identifiers, short coverage and instrumentation gaps constrain interpretation.

Publish reviewed aggregate evidence only. Keep raw events, customer/session identifiers, credentials and unrelated personal planning outside this repository.

## Author

Chukwujekwu Joseph Ezema · [Portfolio](https://jeks042.github.io/) · [GitHub](https://github.com/Jeks042)

Completed companion studies: [A/B Testing & Incremental Revenue](https://github.com/Jeks042/ab-testing-incremental-revenue) · [Subscription Churn & Retention](https://github.com/Jeks042/subscription-churn-retention).
