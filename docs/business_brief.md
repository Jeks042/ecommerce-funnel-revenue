# Business brief

## Decision and audience

A product manager and e-commerce lead need to decide which shopping-journey issue merits instrumentation work or a controlled experiment. Distinguish large observed gaps from credible opportunities to intervene.

## Questions

1. Where does ordered shopping progression decline within a session?
2. Which device and acquisition-context differences remain after accounting for population size, dates and data quality?
3. How much does the conclusion change under alternative defensible session, order and funnel definitions?
4. What bounded revenue scenarios justify investigating an opportunity, and how should an experiment measure success?

## Scope

Use the historical GA4 sample, BigQuery for the analytical foundation, and Power BI for reporting. Preserve event, session, transaction and item grains separately. Support an executive decision memo with source audits, SQL assertions and reproducible aggregate outputs.

Do not infer customer lifetime value from a short anonymous observation window, advertising return without spend data, or profit without costs. Observational differences are not causal effects. Production tracking changes and running an actual experiment are outside this study.

## Success criteria

A reviewer can reproduce published aggregates, explain denominators and exclusions, trace recommendations to evidence, and identify what additional data or experiment would change the decision. An inconclusive result or instrumentation-first recommendation is a valid outcome.
