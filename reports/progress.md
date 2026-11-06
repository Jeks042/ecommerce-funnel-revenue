# Project progress

Updated: 6 November 2026.

**Milestones 1 and 2 are complete.** The accepted December measurement scope now has eight reconciled physical tables in BigQuery. [Read the analytical-foundation findings](milestone_2_findings.md) for the work, validation and limits. Milestones 3–6 remain open.

The full source contains 4,295,584 events and 360,129 usable composite visit groups. The build retains 4,172 qualified recorded transactions and 12,383 item occurrences, with rejected/missing-ID records visible in audit totals. Every accepted scope cell matches milestone 1. Eight read-only model recomputations match the materialized row counts and content checksums.

For the primary December scope, the baseline remains 131,418 eligible visits, 27,289 product-view entries and 2,240 qualified transactions across 1,976 buying visits. The 92 visits containing unresolved purchases remain explicit. Total revenue, average order value and revenue per visit are unavailable; only the item-agreeing selected recorded-value sum is supported.

## Next: diagnose the recorded journey

[Issue #3](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/3) can now examine ordered progression, device differences, daily composition and definition sensitivity under [measurement version 1](../docs/metric_contract.md). Apply the minimum comparison sizes and retain purchase coverage. These are observational investigation questions; no product effect or revenue opportunity has been established.

The [SQL workflow](../docs/sql_workflow.md) records table grains, execution order, scan-review controls, native fixtures and reproduction. The existing Sandbox tables expire on 5 January 2027. Reviewed aggregate evidence and executable SQL remain in the repository. GitHub validation uses no warehouse credentials, retains artifacts and creates no bot commits.

## Reporting direction

The agreed output remains Python analysis with Matplotlib/Seaborn charts, an illustrated commercial report and a decision memo. The existing [milestones](https://github.com/Jeks042/ecommerce-funnel-revenue/milestones) retain their dependency order. Brief each stage in plain language: work completed, findings, decisions, limits and the next deliverable.
