# Source access and handling

## Proposed source

`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

Google documents coverage from 1 November 2020 to 31 January 2021. The sample is obfuscated, includes placeholders and has limited internal consistency. It cannot be compared against the separate Google Analytics demo account. A Cloud project with BigQuery API enabled is required; Sandbox can support initial exploration subject to its limits. See [Google's source documentation](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset).

Documentation reviewed again: 19 October 2026. Existing Sandbox access and US query execution are confirmed. All 92 daily tables and the 20 selected field/type entries were checked. Source quality is under review; see the [source audit](../reports/source_audit.md) and [execution workflow](source_audit_workflow.md).

## Access gate

1. Confirm the available Cloud project, source location and query permissions. Keep private configuration and authentication local.
2. Inspect metadata and select a bounded date slice. Apply explicit `_TABLE_SUFFIX` bounds to wildcard event queries.
3. Review the validator or dry-run estimate before execution. For a billing-enabled project, set a maximum-bytes-billed cap. The kickoff instead used confirmed Sandbox with its enforced free quota, fixed date bounds and reviewed estimates; no per-job cap was confirmed. The review ceiling is 3 GiB and does not itself enforce a cap. No paid billing or capacity provisioning is part of this project setup.
4. Audit dates, event coverage, key completeness, parameter types, purchase identifiers, item arrays and monetary consistency. Expand only after the small-slice audit succeeds.
5. Record the source tables, retrieval date, query versions, exclusions and cost controls. Freeze definitions before comparison results.

If access or source quality is insufficient, document the blocker and revise scope explicitly. Do not substitute another source silently.

## Publication

Raw events and row-level extracts stay outside Git. Publish reviewed aggregates and small synthetic fixtures only. Check dataset use terms before redistribution; documentation licensing is not a blanket licence for every dataset artifact. Review embedded Power BI data before publication.

## Source audit output

Record observed table/date coverage, key completeness, duplicate/conflicting transactions, currency and revenue coverage, excluded row counts, scan size and a go/no-go assessment for the [metric contract](metric_contract.md).
