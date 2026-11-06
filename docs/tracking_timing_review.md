# Tracking, ordering and boundary review

Status: milestone 1 measurement review. No analytical marts have been built and the metric contract is not frozen.

## Source and extraction

[SQL 06](../sql/06_tracking_timing_sensitivity.sql) scans the fixed 1 November 2020–31 January 2021 source window. Parameter extraction uses correlated subqueries to avoid event multiplication. Usable keys require a nonblank, nonplaceholder customer ID and exactly one positive integer `ga_session_id`. The grouping key retains both values. Transaction-ID usability follows the earlier trimming/placeholder rule, but this query does not deduplicate purchases or apply the complete purchase-detail candidate policy.

Daily coverage is grouped by source-table suffix and device, at event grain. Each source event contributes to one daily/device row. The query retains all events, including repeated names/timestamps; matching names and timestamps alone do not prove duplication. No event rows, customer IDs, session IDs or transaction IDs are returned.

## Ordering

For each keyed group, select the earliest usable product-view timestamp. Select the earliest cart timestamp strictly greater than that view; then the earliest checkout strictly after that selected cart; then the earliest raw purchase strictly after that selected checkout. Do not take the independent minimum of each event type: a later repeat may complete a valid sequence after an earlier out-of-order observation.

The alternative chain uses `>=` at each step. It is an explicit tie sensitivity, not an observed ordering of simultaneous steps. Step counts are nested, and each chain is counted once per keyed group. The entry denominator is groups containing a product-view event, not all sessions. Raw purchase events are used for this timing test; neither chain is an accepted commercial order conversion measure.

Google describes the bundle sequence as the upload bundle's sequence, and the newer batch event index as event ordering within a batch. Its schema also defines the previous-event timestamp and collection/upload offset. Those definitions do not turn a populated bundle ID into within-bundle ordering. See [Google's export schema](https://support.google.com/analytics/answer/7029846?hl=en). The [field inventory](../reports/evidence/purchase-field-inventory-20261106.json) confirms the three checked batch-order fields are absent from this historical source. SQL 06 tests whether the available fields are populated and differ within tied groups.

## Scope sensitivities

All six scopes use the same source and key policy:

- `all_keyed`: every usable composite group, including partially observed groups.
- `all_keyed_interior`: excludes any group with an event on 1 November or 31 January, regardless of its first date.
- `one_start`: exactly one recorded `session_start` event.
- `anchored_candidate`: one start at the first usable timestamp; no unusable timestamps or source/event/UTC date discrepancies; one device variant and one first-user source/medium variant, including null values in variant comparisons.
- `anchored_candidate_interior`: the preceding candidate plus the edge exclusion.
- `anchored_candidate_interior_single_date`: additionally requires one source date, as a separately labelled sensitivity.

These are alternative populations, not mutually exclusive buckets. The report's waterfall uses only nested scopes. Do not add the edge exclusion to missing-start exclusions without accounting for their overlap. A group crossing midnight is not automatically invalid. A recorded start at the first observed timestamp does not guarantee that all real activity is observed.

The source's timestamps are microseconds in UTC. The analytical UTC date policy must be explicit; no property timezone is inferred. Session IDs are treated as identifiers. Safe timestamp interpretation and safe arithmetic are used only to diagnose whether ID-derived time agrees with observations, including out-of-range fixture IDs. No date is assigned from the ID.

## Coverage interpretation

A zero daily cart-event count is an observed coverage flag. It does not establish the cause of the gap or imply that customers did not use baskets. Similarly, more checkout events than cart events is an investigation flag, not proof of failure: events can repeat and journeys can enter at different steps. Do not repair those gaps with synthetic events or automatically choose dates because they produce attractive conversion rates.

The Python [summary builder](../src/build_tracking_review.py) groups the approved aggregate by date/month, lists coverage flags and reproduces the exclusion waterfall. It does not declare dates commercially comparable. Run:

```text
python src/build_tracking_review.py reports/evidence/tracking-timing-20261106.json reports/evidence/tracking-review-summary-20261106.json
```

Keep the canonical input hash with the summary. No third-party Python packages, credentials or raw events are needed for this step.

## Validation and execution

Generate `private/tracking_fixture.sql` with `python tests/prepare_tracking_fixture.py`. The production CTEs are retained when the public-source reference is replaced by 78 synthetic events. The fixture asserts the expected strict/tied chain level and population flags for each of 15 keyed journeys; a further unkeyed journey tests exclusions. Cases cover ties, early and later repeated steps, missing carts/starts/timestamps, repeated starts, cross-midnight activity, both window edges, late starts, inconsistent dates/devices/context and a positive ID outside the timestamp range.

After a zero-byte validator estimate, execute the fixture and save the inner `audit_json`. Validate it against the independently declared expected populations with `tests/check_tracking_result.py --expected`. The source run uses the same SQL logic and the [existing Sandbox controls](source_audit_workflow.md). Its validator estimate was 1.16 GB, within the 3 GiB review ceiling. This ceiling is not an enforced per-job API cap; Sandbox's free quota remained the cost boundary and paid billing was not enabled.

The [receipt](../reports/evidence/tracking-timing-receipt-20261106.json) records canonical SQL/output hashes, hashed job references, UTC execution details and validations. Console local JSON exports were parsed without changing nulls or result keys. Full job references and account/project configuration remain private. The fixture and source passed 81 and 58 checks respectively. Local regression tests reject altered counts and inconsistent scope/timing evidence; they do not replace native execution.

Continue with candidate-purchase/session linkage, unusually long groups, comparison-scope suitability and monetary policy before contract acceptance.
