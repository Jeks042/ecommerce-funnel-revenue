# Purchase reconciliation: agree what can be counted before comparing performance

Updated: 6 November 2026. Source-validation work continues; milestone 1 remains open.

The follow-up audit confirms that repeated purchase identifiers cannot be handled by a simple rule based on matching totals. It also shows that the missing identifiers are concentrated in specific dates. These findings affect measurement; they do not establish faults in a real retailer's website or recoverable lost revenue.

## What the follow-up establishes

| Check | Result | Implication |
|---|---|---|
| Missing identifiers | Of 906 unusable-ID events, 883 have a known placeholder and 23 have a null identifier. | Keep these events separate from distinct-order measures. Missingness is explicit, not zero orders. |
| Dates without usable identifiers | All recorded purchases on 1–10 November 2020 and 31 January 2021 lack usable IDs: eleven dates in total. | A valid-ID-only order population would exclude all purchases on these dates. Assess date coverage before comparing periods or devices. |
| Conflict overlap | The fifteen identity-conflicting IDs and fifteen summary-conflicting IDs are the same fifteen IDs, representing 33 events. | Count the union once; the initial two counts must not be added as thirty different IDs. |
| Additional stored-detail differences | Another 285 repeated IDs, covering 575 events, have different stored e-commerce/item payloads while their user/session and monetary summaries agree. | Inspect what changed before deciding whether these are repeat notifications, changed records or distinct activity. Matching totals alone do not settle that question. |
| Consistent repeats | Twenty-six repeated IDs, covering 53 events, have matching compared summaries and stored e-commerce/item payloads. | These are candidates for further duplicate review, not automatically verified duplicates. All 326 repeated-ID groups have different recorded timestamps. |
| Monetary differences | Of 5,242 events with both native and summed item value, 1,001 differ by more than one cent: 519 above and 482 below. Seven differences numerically match observed tax. | Tax matching alone does not establish the explanation. Native purchase value and item value remain unreconciled measures. |
| Missing financial context | Native purchase revenue is absent on 450 events, across 68 dates; shipping is missing on every purchase event. | Do not fill missing money with zero, silently substitute another field or label a measure net revenue or profit. |

The four mutually exclusive ID groups reconcile to **4,451 distinct usable IDs and 4,786 purchase events**. Adding 906 unusable-ID events reconciles to the existing 5,692 purchase events. The new query also agrees with the earlier audit's missing-revenue and monetary-difference counts.

The stored-payload comparison uses the serialized `ecommerce` and `items` records. It is conservative and sensitive to item-array order and nonfinancial item metadata. The query's `financial_payload` names are diagnostic labels: a changed payload does **not** prove that money changed, nor does an identical payload prove a duplicate sale. Field-level differences and ordering need review before a production deduplication policy is accepted.

## Validation and execution

The [actual query](../sql/03_purchase_reconciliation.sql) was first run against eleven synthetic events using the [fixture generator](../tests/prepare_purchase_fixture.py). Thirteen scalar expectations and four group expectations passed natively in BigQuery, including a multi-item case where item values change but totals stay equal. The fixture scan was zero bytes.

The real-data query used the fixed 1 November 2020–31 January 2021 window in the existing Sandbox project. The validator estimate and processed/billed displays were 2.42 GB, below the existing 3 GiB review ceiling; the job completed in 4.574 seconds. Sandbox's enforced free quota remained the cost boundary, and no paid billing was enabled. The review ceiling is not a per-job maximum-bytes setting.

The [aggregate result](evidence/purchase-reconciliation-20261106.json), [run receipt](evidence/purchase-reconciliation-receipt-20261106.json) and [validation instructions](../tests/README.md) record this work. No event rows or identifiers were exported. These are further diagnostics on the same historical, obfuscated sample, not new evidence of real-world sales performance.

## Decisions and next work

1. Retain purchase events, usable-ID groups and accepted orders as separate concepts. No deduplicated order measure is accepted yet.
2. Investigate the specific fields behind the 285 additional payload differences; quantify the effect of any conservative exclusion rule.
3. Review daily funnel-event recording, timestamp ordering and session boundaries before freezing the metric contract. Preserve uncertainty where the data cannot establish order.
4. Keep revenue, average order value and revenue opportunities unavailable until their populations and monetary definitions are reconciled.

The reporting approach is now Python analysis with Matplotlib and Seaborn, an illustrated commercial report and a decision memo. This changes the presentation tools; it does not relax the source-validation gate or mean funnel charts have already been produced.
