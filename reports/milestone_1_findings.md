# Which shopping activity can this study measure?

The source checks are complete. The project can now build a controlled analysis of recorded shopping journeys in **December 2020**. It cannot support a total-revenue assessment or a claim that a particular checkout change would increase sales.

The main decision is to give the analysis a narrower, defensible scope. November contains eighteen dates with no cart events even though checkout and purchase activity continued. December has cart records on all 31 days. That makes it a useful comparison period for the next stage, while leaving tracking completeness and the sample's obfuscation as limits.

## What counts as a visit or purchase?

A visit needs a clearly recorded start, consistent identifying information and usable dates. The primary analysis also keeps visits within one day. We retain broader versions so the reader can see how those choices change the result; crossing midnight is not itself a tracking error.

Across the full source, all **4,172 qualified transaction groups** link to recorded visits. Repeated observations count once, while different transactions in the same visit stay separate. The three unusually long visits span roughly 29–112 hours, contain sixteen events and have no purchases. They fall outside the within-day primary scope.

For December, the eligibility ledger is:

| Scope | Visits | Removed at this step |
|---|---:|---:|
| All observed composite groups starting in December | 133,351 | — |
| Clear start, consistent recording and away from the outer sample dates | 131,713 | 1,638 |
| Also recorded within one UTC date: primary scope | 131,418 | 295 |

The primary scope includes **27,289 product-view entry visits** and **2,240 qualified recorded transactions** across **1,976 buying visits**. These are measurement baselines for building the next stage, not verified shop sales.

Of those entry visits, 1,437 reach a qualified recorded purchase through strictly ordered view, cart and checkout steps. Allowing tied timestamps gives 1,470; allowing cross-date visits gives 1,461 under strict ordering. Choosing the latest repeated purchase observation instead of the earliest makes no difference to this December result. The production code nevertheless keeps the earliest rule so a replay cannot manufacture a conversion in other inputs.

## What remains uncertain?

The primary scope contains **90 purchase events with unusable IDs** and **17 with rejected IDs**. Ninety-two visits contain an unresolved purchase record, including six that also contain a qualified transaction. Those records remain visible. Treating every excluded purchase as a known nonbuyer would overstate what the source tells us.

Purchase and item values agree for **1,851 of the 2,240** qualified transactions. Their recorded value totals **$114,848**, covering that selected subset only. The other 389 qualified transactions fail the item-agreement rule. Missing-ID and rejected-ID records sit outside this transaction denominator as well. The selected sum is not total revenue, and its exclusions are not lost sales.

Total revenue, average order value and revenue per visit remain unavailable. We can still investigate recorded progression and propose a test, but any commercial value scenario must expose its assumptions and the additional sales evidence needed.

December was chosen for recording coverage before comparing device performance. Device counts now support the next stage, subject to a common daily mix and minimum comparison sizes. No device or acquisition-context opportunity has been established yet.

## Decision and validation

**Go:** build reproducible event, visit and qualified-transaction tables under [measurement definitions version 1](../docs/metric_contract.md). Preserve unresolved purchases, monetary coverage and the alternative scopes. Continue with Python charts and an illustrated report after the analytical checks.

The final SQL passed a native zero-byte fixture containing 56 events across eleven synthetic journeys. All **93 fixture checks**, **525 source checks**, **268 comparisons with previous evidence** and **22 local regression tests** passed. The Python scope ledger reproduces from the saved aggregates. The source run's displayed estimate was 2.57 GB, processed 2.57 GB and billed 2.58 GB in confirmed Sandbox. No paid billing was enabled; the free-quota boundary and 3 GiB scan-review ceiling apply. No per-job byte cap is claimed.

See the [method and repeatable commands](../docs/measurement_gate.md), [source aggregate](evidence/measurement-gate-20261106.json), [scope ledger](evidence/measurement-scope-20261106.json) and [run receipt](evidence/measurement-gate-receipt-20261106.json). Google's [dataset description](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset) explains the obfuscation and limited internal consistency of the sample.

The next deliverable is [milestone 2](https://github.com/Jeks042/ecommerce-funnel-revenue/issues/2): analytical tables with reconciled joins and explicit exclusions. Funnel diagnosis and recommendations follow after those tables pass their own checks.
