# Which purchase records can we count?

The repeated records are now better understood. Most differences concern promotion labels or the order in which items were stored. A smaller set contains conflicting customers or amounts. Simply removing every repeated record would discard useful observations; treating every record as a separate order would overcount them.

This is a measurement review of Google's historical, obfuscated sample, covering 1 November 2020–31 January 2021. It does not verify real customer orders or establish a sales figure.

## What changed

The source contains 5,692 purchase events and 4,451 usable transaction identifiers. Of those identifiers, 326 appear more than once. Comparing the full purchase details gives the following mutually exclusive groups:

| What differs within an identifier | Identifier groups | Purchase events |
|---|---:|---:|
| Customer/session or compared monetary summaries | 15 | 33 |
| Item metadata, with the compared products and amounts unchanged | 264 | 530 |
| Item order only | 21 | 45 |
| No compared purchase-detail difference | 26 | 53 |
| Only one observation | 4,125 | 4,125 |
| **Total with usable identifiers** | **4,451** | **4,786** |

The other 906 events have unusable identifiers. All 15 identifiers observed across multiple dates belong to the customer/summary conflict group. Matching details within a repeated identifier still do not prove that the source represents one genuine sale.

Promotion-name values change in all 264 metadata-changing groups. No other individual field's value multiset changes within that bucket. The full-row comparison remains necessary because separate field totals do not preserve which values belong to each item.

## The cautious counting rule

For the next round of testing, retain one candidate per identifier only when the customer/session, currency, purchase details and complete item contents agree after allowing item order to change. Require one observed source date and device, a usable customer/session key and USD currency. Preserve repeated identical item rows when comparing baskets. Keep missing identifiers and conflicting groups separate.

This rule retains **4,172 candidate identifier groups**, represented by 4,223 events. It admits the 21 item-order-only groups and the 26 matching-detail repeated groups. It sets aside the 264 metadata-changing groups as well as the 15 customer/summary conflicts. The 51 additional observations within retained repeated groups are counted once per identifier for this sensitivity calculation.

These are candidate counts for a documented rule, not validated orders. Keeping the metadata-changing groups out is deliberately cautious; a wider sensitivity can later test whether accepting specific label changes alters the conclusions.

## Revenue still needs a narrower scope

All 4,172 retained candidates have a populated, finite, nonnegative native purchase amount. However, **779 (18.7%)** do not pass the complete-item agreement check. Only **3,393** pass both the identifier rule and the purchase-versus-item amount check.

The diagnostic native sums are $288,470 for all retained candidates and $212,582 for the agreeing subset. These describe different selected populations. Neither is an approved revenue measure, and their difference is not lost revenue, an adjustment or a commercial opportunity. USD-field substitution, tax treatment and obfuscation remain unresolved.

## Why the exclusions matter commercially

The retained purchase events cover 74.2% of the raw purchase events, unevenly across the period:

| Source month | Raw purchase events | Events attached to retained candidates |
|---|---:|---:|
| November 2020 | 2,054 | 1,003 |
| December 2020 | 2,434 | 2,323 |
| January 2021 | 1,204 | 897 |

These are coverage counts, not monthly order totals or conversion rates. All purchases on eleven dates lack usable identifiers. A chart using only the retained population could therefore make tracking exclusions look like a change in trading performance. Device and channel comparisons must account for this date mix before being interpreted.

## Decision and next step

Use the candidate rule to test sensitivity, keeping raw purchase-event counts alongside it. Do not publish headline orders, average order value or revenue per session yet. Continue milestone 1 with daily funnel-event coverage, available ordering fields, tied timestamps and session boundaries. Freeze the metric contract only after those checks establish the supported comparisons.

The [technical method](../docs/purchase_counting_review.md), [SQL](../sql/05_purchase_detail_diagnostics.sql), [aggregate evidence](evidence/purchase-detail-diagnostics-20261106.json) and [execution receipt](evidence/purchase-detail-receipt-20261106.json) make the result reviewable.
