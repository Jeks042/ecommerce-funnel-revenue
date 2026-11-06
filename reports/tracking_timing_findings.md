# What the shopping records can tell us

Several apparent gaps in the shopping journey cannot yet be treated as customer problems. **Eighteen dates have no recorded add-to-cart events**, although checkout and purchase events are present on every one of them. Those dates contain 4,728 checkout events and 1,071 purchase events. Using the whole period to estimate cart-stage losses would mix customer behaviour with uneven event coverage.

The affected dates are 2–15 and 21–24 November 2020. This establishes a source limitation; it does not tell us whether implementation, obfuscation or another factor caused it. A date with some cart events is not automatically a fully comparable date either.

## The difference across months

| Source month | Product-view events | Add-to-cart events | Checkout events | Purchase events |
|---|---:|---:|---:|---:|
| November 2020 | 148,639 | 7,674 | 9,546 | 2,054 |
| December 2020 | 150,458 | 35,347 | 18,177 | 2,434 |
| January 2021 | 86,971 | 15,522 | 11,034 | 1,204 |

These are event counts, including repeated activity. They are not an ordered funnel, distinct orders or evidence of a change in commercial performance. November's recording gaps make a simple month-to-month conversion comparison unsuitable. Device comparisons also need a common, justified date scope.

## How much does event timing change the result?

The timestamp test follows each step after the preceding selected step within the same user/session group. The primary candidate uses strictly later timestamps. A sensitivity allows the next step to share the same timestamp, showing how the counts change when ordering is uncertain.

| Recorded stage | Strictly later timestamps | Same timestamps allowed |
|---|---:|---:|
| Visit contains a product view: entry denominator | 77,020 | 77,020 |
| Subsequent add-to-cart | 14,380 | 15,167 |
| Subsequent checkout | 5,187 | 5,416 |
| Subsequent raw purchase event | 2,778 | 2,834 |

Allowing ties adds 56 completed recorded sequences, about 2.0% relative to the strict count. The effect is larger at the cart step. These are measurement sensitivities across all keyed groups, using raw purchase events as the final step. They do not establish true customer order counts, a reliable full-period conversion rate or the impact of an intervention.

All 25,101 groups containing different shopping steps at one timestamp share the same upload-bundle identifier. Previous-event timestamps and server offsets are unpopulated for these shopping events, and the newer batch-order fields are absent from the source. The available fields therefore do not establish an order within these ties. Keep the strict rule and show the sensitivity.

## Which visits are fully enough observed to compare?

The following is a conservative population sensitivity. Each row starts from the preceding row, so exclusions are not double counted.

| Population rule | User/session groups retained | Removed at this step |
|---|---:|---:|
| Usable composite user/session key | 360,129 | — |
| Exactly one recorded session start | 354,752 | 5,377 |
| Start is the first observed timestamp; consistent dates, device and first-user context | 354,580 | 172 |
| Also exclude groups touching the first or last source date | 349,223 | 5,357 |

There are 845 groups crossing source dates. Among the final population, additionally requiring a single date removes another 806 groups. Crossing midnight alone does not establish a faulty visit, so this remains an additional sensitivity. Three groups span more than 24 hours and still need review before final population acceptance.

Every numeric session ID differs by more than 60 seconds from the first observed event when interpreted as a Unix timestamp. Use that field as an identifier. Derive analytical dates from observed event timestamps under an explicit UTC policy, rather than constructing a start date from the ID.

## Decision

Use the full period to explain recording coverage. Any cart-stage or device comparison needs a separately justified comparable scope and visible exclusions. Retain strict timestamp ordering, report the tied-timestamp sensitivity, and keep purchase-event counts separate from the earlier candidate transaction rules. These findings do not justify a checkout redesign or a revenue-uplift estimate.

Milestone 1 remains open. The final measurement gate is to link candidate purchase outcomes to eligible visits, review the unusually long groups and choose a supported comparison scope and monetary policy. Then freeze the definitions before building the analytical tables.

The query passed 81 synthetic-fixture checks and 58 full-sample reconciliation checks. [Method](../docs/tracking_timing_review.md), [SQL](../sql/06_tracking_timing_sensitivity.sql), [warehouse aggregate](evidence/tracking-timing-20261106.json), [reproducible coverage summary](evidence/tracking-review-summary-20261106.json) and [execution receipt](evidence/tracking-timing-receipt-20261106.json) support the review.
