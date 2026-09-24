# Metric contract — draft

**Not frozen.** Validate these definitions during milestone 1. Record changes and reasons before accepting milestone 2.

| Measure / object | Proposed definition and review requirement |
|---|---|
| Session key | Composite user_pseudo_id and extracted ga_session_id; the latter alone is not assumed unique. Quantify missing keys separately. |
| Event grain | One retained source event under a documented duplicate policy. Matching timestamps and event names alone do not establish duplicates. |
| Session date | Approved session-start and timezone policy; distinguish source event date from UTC timestamp and audit cross-date sessions. |
| Primary funnel | Ordered view_item → add_to_cart → begin_checkout → purchase in the same eligible session. Select each step after the preceding selected step. Resolve ties only using fields actually available; otherwise report ambiguity and sensitivity. |
| Entry population | Eligible sessions with view_item. This differs from all sessions. Item identity need not persist across steps unless a separately validated item-level funnel is adopted. |
| Step conversion | Sessions reaching the next ordered step divided by sessions reaching its preceding ordered step. Publish counts and exclusions. |
| Overall session conversion | Eligible sessions with a valid purchase divided by all eligible sessions, independently of the ordered funnel. |
| Orders | Valid distinct transactions after deduplication/conflict rules; never item row counts. Quarantine missing or conflicting IDs for sensitivity review. |
| Revenue | Select a supported purchase-level field and currency policy after reconciliation. State refund, tax and shipping coverage before naming gross/net metrics. |
| Average order value | Approved purchase revenue divided by valid orders from the same scope. |
| Revenue per session | Approved revenue attributable to eligible sessions divided by those sessions; reconcile unmatched purchases separately. |
| Segments | Device and observed acquisition context with explicit session-grain assignment, coverage and unknowns. Observed source fields do not imply causal attribution. |

## Acceptance questions

- Can repeated parameters and item arrays be extracted without multiplying events or revenue?
- How are repeated steps, multiple purchases and partially observed sessions handled?
- Are window-edge sessions censored, and what does boundary sensitivity change?
- Which monetary fields reconcile, and which conflicts remain because of obfuscation?
- What minimum segment sizes and uncertainty methods will be used?
- Which comparisons survive exclusions and date-mix checks?

Record approved answers, aggregate impacts and SQL check references before labelling this contract frozen.
