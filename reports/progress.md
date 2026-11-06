# Project progress

Updated: 6 November 2026.

**Milestone 1 is complete.** [Measurement definitions version 1](../docs/metric_contract.md) are accepted for a bounded analysis of recorded shopping journeys in December 2020. Milestones 2–6 remain open.

The source review covers 4,295,584 events across all 92 days. It checks missing and repeated purchase records, money-field disagreement, gaps in cart recording, timestamp ties and visit boundaries. The final check links all 4,172 qualified transaction groups to observed visits. Native synthetic fixtures, source reconciliations and saved aggregate receipts support the decisions.

[Read the milestone 1 findings](milestone_1_findings.md) for the outcome in plain language. The primary scope contains 131,418 visits and 27,289 product-view entries. Missing/rejected-ID purchases remain visible. Only an item-agreeing selected recorded-value summary is supported; total revenue, average order value and revenue per visit are unavailable.

## Next: build the analytical foundation

[Issue #2](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2) can now build event, visit, qualified-transaction and item tables, plus exclusion and purchase-coverage ledgers. Keep full-period ID qualification separate from December reporting. Reconcile every join to the accepted gate and retain alternative timing/population scopes. Use bounded Sandbox execution and local fixtures; credential-free workflows should validate and retain evidence without bot commits.

The gate query provides measurement evidence; it is not a delivered set of analytical tables. No device ranking, product recommendation, forecast or measured intervention effect has been published.

## Reporting direction

The agreed output is Python analysis with Matplotlib/Seaborn charts, an illustrated commercial report and a decision memo. The six existing [GitHub milestones](https://github.com/Jeks042/ecommerce-funnel-revenue/milestones) retain their dependency order. At each stage, explain what was done, what the evidence supports, decisions and limits, and the next deliverable. See the [workflow](../docs/workflow.md).
