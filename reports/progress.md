# Project progress

Updated: 19 October 2026.

The project has started. All six [GitHub milestones](https://github.com/Jeks042/ecommerce-funnel-revenue/milestones) are linked to their existing issues. Milestone 1 is in progress; milestones 2–6 depend on its measurement decisions.

## What has been done

- Confirmed access through an existing BigQuery Sandbox project, without enabling paid billing.
- Verified all 92 daily tables and 20 selected field/type entries.
- Ran a one-day pilot and then the complete 1 November 2020–31 January 2021 source profile.
- Reconciled event/device totals to 4,295,584 events and purchase/currency totals to 5,692 purchase events.
- Published the [source audit](source_audit.md), [aggregate evidence](evidence/source-profile-20201101-20210131.json), [SQL](../sql/02_source_profile.sql) and [execution instructions](../docs/source_audit_workflow.md).

## What the checks mean

The source is available for further investigation, but counting decisions remain. Purchase events include missing and repeated order identifiers; native and item money fields do not consistently agree. Some sessions cross dates and many funnel steps share timestamps. Those issues affect a credible funnel and revenue comparison.

The [metric contract](../docs/metric_contract.md) remains a draft. No funnel results, validated order counts or accepted revenue measures have been published. Milestone 1 stays open.

## Resume here

Continue [issue #1](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/1): inspect daily event coverage, repeated/conflicting purchases, monetary-field reconciliation and available ordering fields. Quantify exclusion, tie and boundary sensitivities. Agree the supported measures and freeze the contract before beginning the SQL marts in issue #2.

At every milestone, give the project briefing: work completed, findings, decisions and reasons, limits and next step. See the [workflow](../docs/workflow.md) for the full sequence.
