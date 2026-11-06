# Analytical tables and execution

The warehouse build implements [measurement definitions version 1](metric_contract.md). It retains the full 92-day source for transaction qualification and creates the December eligibility flag afterwards. It does not enable total revenue, AOV or revenue per visit.

## Grains and dependencies

| Model | One row represents | Input |
|---|---|---|
| `stg_events` | One retained source event, with nested items and e-commerce details | Fixed 92 source tables |
| `transaction_policy` | One nonplaceholder transaction-ID group, including rejected groups | Purchase events in staging |
| `fact_transactions` | One globally qualified recorded transaction | Staging and transaction policy |
| `fact_transaction_items` | One sorted item occurrence in a qualified transaction | Qualified transaction's item array |
| `fact_visits` | One usable composite user/session group, with eligibility, timing and purchase coverage | Staging, transaction policy and transaction facts |
| `audit_event_keys` | One date/device/key-status total | All staged events, including unkeyed events |
| `audit_visit_exclusions` | One cohort/reason total under disjoint exclusion rules | Visit facts |
| `audit_purchase_coverage` | One source-date/device purchase-outcome total | Purchase events and transaction policy |

The event table has no invented unique event ID. Matching names/timestamps do not prove duplicates. Item rows never join directly into visit or transaction totals. Transaction items have a key of transaction ID plus sorted item occurrence; identical rows retain separate occurrences. Purchase-level value is absent from the item table, preventing accidental summation through a one-to-many join.

Full e-commerce payloads and complete item multisets are compared before a transaction qualifies. The earliest observation supplies purchase timing; a later replay remains a sensitivity. `ANY_VALUE` chooses an already proven identical sorted item multiset, not a way to resolve conflicts. Monetary disagreement keeps `supported_recorded_value` null. Visits with unresolved purchases retain explicit counts; they are not silently recoded as known nonbuyers.

First-user source/medium is retained separately from device. Eligible visits require consistent context/device. The minimum values in broader diagnostic groups do not assign session acquisition or justify comparing mixed groups. Source dates and UTC visit-start dates remain separate: monthly purchase-event totals need not equal monthly visit-cohort totals.

## Render and review

Use an existing authenticated US BigQuery Sandbox. The renderer needs no credentials and executes nothing:

```powershell
python src/render_marts.py --project your-project-id --dataset ecommerce_v1_build --output private/marts
```

Only a dedicated `ecommerce_v1_` namespace is accepted. Rendered project configuration and query hashes stay under ignored `private/`. The source window and December cohort are fixed by the contract; changing them requires a new measurement decision. The public SQL templates contain no private project IDs.

Check that the destination is available before first execution. Files `00`–`08` create the dataset and eight tables. Execute **one statement at a time**, in order, checking the validator estimate before each Run and stopping above 3 GiB. `CREATE TABLE` fails if a target is already present; the build does not overwrite unrelated work. A failed build is not transactional: earlier tables can remain. Inspect the failure and existing objects before resuming. Do not append a rerun or replace tables silently.

Only the first table reads the public events. Later models read the retained staged input and previously built tables. No DML, dynamic SQL, external sharing, paid billing or scheduled warehouse execution is needed. Sandbox's free quota supplies the no-paid-billing boundary; the 3 GiB review ceiling is not an enforced per-job maximum-bytes cap.

The tables are unpartitioned and clustered by user/session where useful. Sandbox automatically expires tables, views and partitions after 60 days. Partition expiration is based on the historical partition date, so date partitioning this 2020–21 source could immediately expire the data. Unpartitioned table retention starts at table creation. Google's [Sandbox limits](https://docs.cloud.google.com/bigquery/docs/sandbox) also specify a lifetime storage allowance that deletion does not restore; avoid unnecessary rebuild copies. See [partition expiration](https://docs.cloud.google.com/bigquery/docs/managing-partitioned-tables#partition-expiration).

## Validate and reproduce

Run `09_validate.sql` after all tables exist. Its twenty named runtime checks use `ERROR()` to fail the query if any assertion fails. They cover unique grains, event/key and visit-exclusion conservation, purchase coverage, transaction/visit linkage, item multiplicity, selected monetary values and nested ordered populations. The query returns reviewed aggregates and row-count/content checksums, never source identifiers.

Run `10_inventory.sql` to verify object types, expiration settings and absence of date partitions. Files `11`–`18` recompute each model as a read-only SELECT against its declared inputs. Review each estimate individually. Compare all eight row counts and order-independent content checksums with the materialized build, as well as the saved scope counts. This checks that the retained inputs reproduce each model without writing another copy against Sandbox's lifetime storage allowance. A checksum is a consistency check, not proof of data authenticity.

Download only aggregate JSON through Console. Preserve the values and nulls when parsing the outer result row. Check the source result against the accepted measurement gate:

```powershell
python tests/check_mart_result.py reports/evidence/marts-20261106.json --gate reports/evidence/measurement-gate-20261106.json
python tests/run_local_validation.py
```

The execution receipt records template/rendered query hashes, hashed native job references, displayed scan sizes and the comparison results. Full native job/project references remain private. If the 60-day tables expire, the SQL and reviewed aggregate evidence remain available; a new warehouse build consumes storage allowance and requires the same access/cost checks.

## Native edge cases and GitHub checks

Generate the source-free fixture using `python tests/prepare_mart_fixture.py`. `private/mart_fixture_materialized.sql` creates temporary input/model tables and runs the same validation query. Its 94 literal events cover eighteen journeys, including multi-item and duplicate-row baskets, repeated purchases straddling checkout, cross-month/currency conflicts, missing/repeated session parameters, missing IDs, metadata changes, ties, out-of-order steps and cross-date groups. Missing visit keys stay in the event audit.

The literal input alone validates at zero source bytes. BigQuery does not estimate an entire temporary-table script; see its [dry-run limitations](https://docs.cloud.google.com/bigquery/docs/multi-statement-queries#dry-run_a_multi-statement_query). Review that the script contains only the 94 literal rows and temporary model references. Temporary-table reads still process and bill bytes against the free Sandbox quota; do not call the full script a zero-byte run. Select the final child job's results for aggregate export.

After saving the inner fixture JSON, run:

```powershell
python tests/check_mart_result.py reports/evidence/marts-fixture-20261106.json --expected private/mart_fixture_expected.json
```

The GitHub workflow runs the local regression suite, validates saved aggregate evidence against the accepted gate, checks fixture/configuration rendering and retains a small validation artifact for 30 days. It has read-only repository permissions, no warehouse credentials and no commit step. It does not claim to rerun native BigQuery tests on GitHub.
