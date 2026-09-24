# E-commerce Funnel & Revenue Analytics

**Status: scoped and ready for source validation. Six milestone issues are open; no analysis has been run.**

Which parts of the shopping journey should a product team investigate first, and what evidence would justify an experiment?

This project will use GA4 event data, BigQuery SQL and Power BI to examine funnel progression, segment differences and revenue opportunities. The aim is a reproducible decision record with explicit measurement boundaries.

## Planned workflow

Source audit and metric contract → event/session/purchase SQL marts → ordered funnel analysis → opportunity scenarios and experiment proposal → Power BI and decision memo → independent reproduction.

The proposed source is Google's obfuscated e-commerce sample. Identity coverage, purchase consistency and source suitability must pass milestone 1 before implementation proceeds. There are no findings or measured business improvements at this stage.

## Milestones

1. [Validate GA4 access, source quality and metric definitions](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/1) — next
2. [Build reproducible event, session and purchase SQL marts](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2) — planned
3. [Diagnose conversion funnels and segment differences](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/3) — planned
4. [Prioritise revenue opportunities and propose an experiment](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/4) — planned
5. [Build a reconciled Power BI report and decision memo](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/5) — planned
6. [Reproduce, review and publish the completed case study](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6) — planned

## Start here

- [Business brief](docs/business_brief.md)
- [Source access and handling](docs/data_access.md)
- [Draft metric contract](docs/metric_contract.md)
- [Delivery workflow and acceptance gates](docs/workflow.md)
- [Current progress and next session](reports/progress.md)
- [Decision log](docs/decision_log.md)

## Planned outputs

| Location | Purpose |
|---|---|
| docs/ | Scope, measurement definitions, workflow and decisions |
| sql/ | BigQuery profiling, staging, marts and analytical queries |
| tests/ | Synthetic edge cases and reconciliation checks |
| reports/ | Validated aggregate findings and decision records |
| dashboard/ | Power BI model, measures and presentation evidence |

Only documentation exists at setup. SQL, tests and dashboard artifacts will be added during their milestones.

## Evidence boundaries

This is a historical observational study. Funnel differences do not establish why shoppers leave or what intervention will increase revenue. Scenario values will be labelled assumptions. Obfuscation, missing identifiers, short coverage and instrumentation gaps constrain interpretation.

Publish reviewed aggregate evidence only. Keep raw events, customer/session identifiers, credentials and unrelated personal planning outside this repository.

## Author

Chukwujekwu Joseph Ezema · [Portfolio](https://jeks042.github.io/) · [GitHub](https://github.com/Jeks042)

Completed companion studies: [A/B Testing & Incremental Revenue](https://github.com/Jeks042/ab-testing-incremental-revenue) · [Subscription Churn & Retention](https://github.com/Jeks042/subscription-churn-retention).
