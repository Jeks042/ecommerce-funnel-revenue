# A dependable base for the shopping-journey analysis

The analytical tables are built in BigQuery. Events, visits, qualified purchases and basket items have their own level of detail, with checks that keep their totals aligned. The December analysis still uses the measurement rules agreed in milestone 1.

This matters when a purchase contains several items or appears more than once in the records. It should remain one qualified transaction, while each basket item retains its place. A visit can also contain several transactions. Keeping those distinctions makes the next stage's comparisons reviewable.

## What was built

| Table | What it holds | Rows |
|---|---|---:|
| Source events | The selected fields from all 92 source days, without flattening item arrays | 4,295,584 |
| Transaction rules | Each usable purchase-ID group, including groups rejected by the agreed rules | 4,451 |
| Qualified transactions | One row per accepted recorded transaction ID | 4,172 |
| Transaction items | Every item occurrence in those qualified transactions, including repeated identical rows | 12,383 |
| Visits | One row per composite customer/session group, with timing and purchase coverage | 360,129 |
| Event-key audit | Daily device totals that keep unusable keys visible | 276 |
| Visit-exclusion audit | Mutually exclusive eligibility reasons by month | 17 |
| Purchase-coverage audit | Purchase outcomes by source date and device | 245 |

The source contains 5,692 purchase events: 906 have unusable IDs, 563 belong to rejected ID groups and 4,223 belong to qualified groups. Counting each qualified group once gives 4,172 recorded transactions; the remaining 51 are repeated observations under this policy. These distinctions do not establish real shop sales or lost orders.

## The accepted December scope is preserved

The tables reproduce all scope cells from the measurement gate, including:

- **131,418 eligible visits**, with **27,289 product-view entries**.
- **2,240 qualified recorded transactions** across **1,976 buying visits**.
- **90 missing-ID and 17 rejected-ID events** across **92 visits** with unresolved purchases.
- **1,851 item-agreeing transactions**, with **$114,848 recorded USD value for that selected subset**.

The unresolved purchases remain visible. The selected value does not become total revenue, average order value or revenue per visit. Those measures remain unavailable.

## Checks and repeatability

Twenty native warehouse assertions pass. They check the separate grains, joins, event and exclusion ledgers, item multiplicity, selected values and ordered-step populations. Each model was then recomputed with a read-only query: all eight row counts and content checksums match the stored tables, including source ingestion. This verifies repeatability without writing a second warehouse copy.

The materialized synthetic test uses 94 events across eighteen journeys. It covers multi-item and duplicate-row baskets, repeated purchases, missing/repeated visit keys, conflicting currencies, metadata changes, tied timestamps, out-of-order steps and cross-date visits. Its 66 aggregate checks pass; the source result passes 995 checks against the accepted measurement evidence. All 32 local regression tests pass.

The GitHub workflow validates saved evidence and checks rendering without warehouse credentials. It retains a small validation artifact and has no commit step. Current SQL/renderer hashes and the regenerated fixture must match the native execution receipt, so changing the code cannot silently reuse stale evidence. Workflow execution evidence is recorded in [issue #2](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2) and [Actions](https://github.com/Jeks042/ecommerce-funnel-revenue/actions/workflows/validate.yml).

## Decisions and limits

The build uses a dedicated private dataset and fails if a target table already exists. Each source-backed statement and read-only recomputation has its scan estimate reviewed individually against the existing 3 GiB ceiling. The initial source scan displayed 2.57 GB; paid billing was not enabled. The free Sandbox quota remains the cost boundary, with no claimed per-job byte cap.

The eight physical tables are unpartitioned. Their observed expiry dates are **5 January 2027**, reflecting Sandbox's 60-day retention. Historical date partitions could expire immediately under that policy, so they are unsuitable for retaining this 2020â€“21 sample. SQL and reviewed aggregate evidence remain in the repository for reproduction; raw identifiers stay in the warehouse.

This stage establishes the analytical foundation. It does not yet identify a device problem, a product intervention or a revenue opportunity. The source remains historical and obfuscated, with the tracking and purchase limits recorded in the [measurement definitions](../docs/metric_contract.md).

## Next decision

[Milestone 3](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/3) will examine the recorded journey in December: where progression declines, whether device differences survive common-date and counting checks, and which questions deserve investigation. It will apply the agreed comparison-size rules and show the effect of unresolved purchases and alternative definitions before proposing priorities.

Technical evidence: [SQL workflow](../docs/sql_workflow.md), [source aggregate](evidence/marts-20261106.json), [fixture aggregate](evidence/marts-fixture-20261106.json), [recomputation results](evidence/marts-reproduction-20261106.json), [physical-table inventory](evidence/marts-inventory-20261106.json) and [execution receipt](evidence/marts-receipt-20261106.json).
