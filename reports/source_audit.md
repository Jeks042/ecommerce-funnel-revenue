# Source audit: a usable source with counting decisions still to resolve

Updated: 19 October 2026. Milestone 1 is in progress. The metric contract remains a draft.

The full three-month source is available. It contains enough recorded shopping activity to investigate the journey, but event counts cannot yet be presented as distinct orders or a reliable revenue baseline. The next step is to resolve purchase conflicts, missing monetary values and ambiguous step ordering before building the analytical tables.

## What was checked

The metadata inventory found all **92 daily tables**, covering **1 November 2020–31 January 2021**, with no missing dates. Twenty selected fields have the same types across those tables. Schema presence does not establish populated or valid values.

A one-day pilot on 1 November preceded the full-period audit. Both queries ran successfully in BigQuery's US location. Only aggregate diagnostics were returned; no customer, session or order identifiers were exported.

| Check across the full period | Observation | Consequence for the analysis |
|---|---|---|
| Event coverage | 4,295,584 events across 92 dates | Use the historical window explicitly; daily coverage alone does not establish consistent tracking. |
| Session keys | 360,129 observed user/session combinations; no events fail the current key checks | These are observed session groups, not verified complete visits. The session number alone is unsuitable: 9,906 session numbers appear under more than one user. |
| Session boundaries | 845 groups cross an event date; 5,272 lack a session-start event and 105 contain repeated starts | Keep sessions together across midnight and quantify incomplete visits before choosing a session-date rule. |
| Step ordering | 25,101 session/timestamp groups contain different funnel step types | Equal timestamps cannot establish sequence. Compare strict ordering with an explicitly labelled tie sensitivity. |
| Purchase identifiers | 5,692 purchase events; 906 lack a usable transaction ID; 4,451 distinct nonplaceholder IDs occur in 4,786 events | Purchase events and orders are different measures. Missing IDs need a separate bucket. |
| Repeated transactions | 326 IDs repeat; 15 IDs have identity conflicts and 15 have monetary conflicts | Do not automatically delete repeats or assume all are separate orders. The two conflict counts may overlap. |
| Monetary consistency | 450 purchase events lack native purchase revenue; 1,001 comparable events differ from summed item revenue by more than $0.01 | Reconcile records before approving revenue or average order value. Missing money remains unknown. |
| Other financial fields | All purchase currency parameters pass the USD format check; shipping is unpopulated and no refund events are recorded | A currency label is not financial reconciliation. There is no basis for net revenue or profit. |

The event totals reconcile across the event-type and device breakdowns, and purchase totals reconcile to the currency breakdown. These checks validate the aggregate capture, not the underlying commercial accuracy.

## Why the pilot mattered

On 1 November, the source has 31,272 events and 2,625 observed user/session groups. It records four add-to-cart events, 127 checkout starts and fourteen purchase events, all without usable transaction IDs. The full period has 58,543 add-to-cart events, 38,757 checkout starts and 5,692 purchase events. These are event counts, not an ordered funnel.

The pilot anomaly therefore needs a daily tracking review; it must not be extrapolated to the whole period or described as shopper abandonment. The first day also cannot reveal cross-date sessions on its own.

## Revenue is still a candidate measure

The raw native purchase-event revenue sum is $362,165, compared with $362,110 summed item revenue. The small $55 aggregate difference conceals 1,001 event-level differences and excludes missing values from each sum. Neither sum is accepted as a revenue headline. Tax treatment, incomplete items, conflicting IDs and the differing field populations still need reconciliation. USD-converted revenue is populated even where native revenue is missing; it is not an automatic replacement.

Google describes this as obfuscated sample data with placeholders and limited internal consistency. It cannot be reconciled to the separate Analytics demo account. See [the source documentation](https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset).

## Execution and review record

| Query | Validator estimate | Processed / billed shown by Console | Execution on 19 October 2026, UK time |
|---|---|---|---|
| Metadata inventory | 30 MB | 30 MB / 30 MB | 10:10:57; 563 ms |
| One-day profile | 16.75 MB | 16.75 MB / 17 MB | 10:15:25–10:15:27; 1.653 s |
| Full-period profile | 2.57 GB | 2.57 GB / 2.57 GB | 10:17:20–10:17:27; 7.413 s |

Sizes above retain the Console's displayed units and precision. They are not exact byte counts or monetary charges. Sandbox was visibly active before execution; billing was not enabled. Its free query quota was the enforced cost boundary. No per-job maximum-bytes setting was confirmed in this Console session. Each estimate was reviewed before Run; the expanded query was below a 3 GiB review ceiling. Use an explicit maximum-bytes-billed cap for execution in a billing-enabled project; see [Google's cost controls](https://cloud.google.com/bigquery/docs/best-practices-costs).

The [inventory SQL](../sql/01_source_inventory.sql), [profiling SQL](../sql/02_source_profile.sql), [execution instructions](../docs/source_audit_workflow.md), [aggregate output](evidence/source-profile-20201101-20210131.json) and [public run receipt](evidence/source-audit-receipt-20261019.json) record the work. The full-period query changes only the upper date bound in the pilot SQL. Private execution account and project configuration stay outside Git. The full aggregate was captured from the Console JSON display, with display wrapping removed; the local JSON is checked for reconciliation and matching values before publication.

## Decision and next step

**Proceed with further source checks; keep milestone 1 open.** Investigate repeated/conflicting transactions, monetary differences, daily event coverage and the available ordering fields. Quantify proposed exclusion and boundary rules. Freeze the metric contract only after those impacts are understood, then begin milestone 2. No funnel results, validated orders, accepted revenue or business improvements are claimed by this audit.
