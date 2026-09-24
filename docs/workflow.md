# Delivery workflow

## Milestones and acceptance

### 1. Validate GA4 access, source quality and metric definitions

[Issue #1](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/1) · Dependency: None

Establish a usable, cost-controlled source and freeze the analytical definitions before building funnel results.

Acceptance: An authorised analyst can repeat the bounded source audit. Every headline metric has a grain, denominator, exclusion rule and known limitation. No query has run without an explicit bytes cap or equivalent documented cost control.

Deliverables: docs/data_access.md, docs/metric_contract.md, reports/source_audit.md and executable profiling SQL.

### 2. Build reproducible event, session and purchase SQL marts

[Issue #2](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2) · Dependency: #1

Create a reconciled analytical foundation in BigQuery without multiplying events or order revenue.

Acceptance: The same inputs and parameters reproduce the marts. Joins do not inflate session, order or revenue counts, and all exclusions reconcile. Meaningful edge-case fixtures and BigQuery assertions pass.

Deliverables: sql/, tests/, docs/sql_workflow.md and reports/milestone_2_findings.md.

### 3. Diagnose conversion funnels and segment differences

[Issue #3](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/3) · Dependency: #2

Identify where observed journeys lose progression while separating data quality effects from product hypotheses.

Acceptance: Every chart reconciles to the marts; ordered step populations are nested and denominators explicit. Priorities are robust enough to discuss or clearly marked uncertain.

Deliverables: sql/ funnel queries, aggregate outputs and reports/milestone_3_findings.md.

### 4. Prioritise revenue opportunities and propose an experiment

[Issue #4](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/4) · Dependency: #3

Translate observed funnel gaps into bounded decisions without claiming recoverable revenue or causal gains.

Acceptance: A reviewer can recompute all scenarios and see which inputs are observed versus assumed. No realised uplift, profit, ROAS or causal channel claim is made without supporting data.

Deliverables: docs/experiment_proposal.md, reports/opportunity_assessment.md and reports/milestone_4_findings.md.

### 5. Build a reconciled Power BI report and decision memo

[Issue #5](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/5) · Dependency: #4

Make the analytical decision, supporting evidence and measurement limitations clear to stakeholders.

Acceptance: A stakeholder can trace each recommendation to reconciled evidence. Selected filters and totals agree with SQL, report interactions work, and only approved aggregates are embedded in public artifacts.

Deliverables: dashboard/, reports/decision_memo.md and reports/milestone_5_findings.md.

### 6. Reproduce, review and publish the completed case study

[Issue #6](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/6) · Dependency: #5

Deliver a reproducible, professionally presented public analytical case study.

Acceptance: All prior milestones are accepted, a fresh run is documented, public artifacts contain only permitted evidence, and the business conclusion states limitations and the next decision.

Deliverables: docs/reproduction_workflow.md, reports/milestone_6_findings.md and final README/case study.


## SQL sequence and validation

Profile first, then build event staging, session facts, transaction facts, item facts, funnel facts and aggregate reporting tables. Parameterise dates and destination datasets. Declare grains and keys, avoid cross joining repeated parameters with item arrays, and make builds repeatable.

Tests should cover missing keys, timestamp ties, out-of-order steps, repeated events, multi-item purchases, conflicting transactions, window edges and join inflation. Failed assertions and quarantined records must be visible in aggregate reconciliation.

## Version control and reproduction

Use small scoped changes and codex/ branches where a branch is needed. Link evidence to its milestone issue and keep the issue open until acceptance checks pass. Retain query text, parameters, source windows, tool versions, timestamps, bytes processed, validation outputs and the commit for each accepted run. Document exact execution commands once authentication and runtime are validated.

GitHub Actions is not configured during planning. Introduce meaningful credential-free SQL/fixture checks in milestone 2. Authenticated BigQuery execution remains explicit and cost-controlled; do not auto-run paid queries on pushes.

Keep raw data and intermediate outputs in ignored locations. Publish only reviewed aggregates and professional analytical documentation. Personal career planning stays outside this repository.
