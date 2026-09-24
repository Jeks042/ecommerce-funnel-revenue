# Source access and handling

## Proposed source

`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

Google documents coverage from 1 November 2020 to 31 January 2021. The sample is obfuscated, includes placeholders and has limited internal consistency. It cannot be compared against the separate Google Analytics demo account. A Cloud project with BigQuery API enabled is required; Sandbox can support initial exploration subject to its limits. See [Google's source documentation](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset).

Documentation reviewed: 24 September 2026. Account access, actual schema and source quality remain unverified.

## Access gate

1. Confirm the available Cloud project, source location and query permissions. Keep private configuration and authentication local.
2. Inspect metadata and select a bounded date slice. Apply explicit `_TABLE_SUFFIX` bounds to wildcard event queries.
3. Dry-run the query, review processed bytes and set a maximum-bytes-billed cap appropriate to the available quota before execution. No paid billing or capacity provisioning is part of setup.
4. Audit dates, event coverage, key completeness, parameter types, purchase identifiers, item arrays and monetary consistency. Expand only after the small-slice audit succeeds.
5. Record the source tables, retrieval date, query versions, exclusions and cost controls. Freeze definitions before comparison results.

If access or source quality is insufficient, document the blocker and revise scope explicitly. Do not substitute another source silently.

## Publication

Raw events and row-level extracts stay outside Git. Publish reviewed aggregates and small synthetic fixtures only. Check dataset use terms before redistribution; documentation licensing is not a blanket licence for every dataset artifact. Review embedded Power BI data before publication.

## Source audit output

Record observed table/date coverage, key completeness, duplicate/conflicting transactions, currency and revenue coverage, excluded row counts, scan size and a go/no-go assessment for the [metric contract](metric_contract.md).
