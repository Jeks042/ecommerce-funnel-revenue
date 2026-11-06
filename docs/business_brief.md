# Business brief

## Decision and audience

A product manager and e-commerce lead need to decide which shopping-journey issue merits instrumentation work or a controlled experiment. Distinguish large observed gaps from credible opportunities to intervene.

## Questions

1. Where does ordered shopping progression decline within a session?
2. Which device and acquisition-context differences remain after accounting for population size, dates and data quality?
3. How much does the conclusion change under alternative defensible session, order and funnel definitions?
4. What bounded revenue scenarios justify investigating an opportunity, and how should an experiment measure success?

## Scope

Use the historical GA4 sample, BigQuery SQL for the analytical foundation, and Python with Matplotlib and Seaborn for analysis and reporting. Preserve event, session, transaction and item grains separately. Support an illustrated commercial report and executive decision memo with source audits, SQL assertions, reproducible aggregate outputs and charts that can be regenerated from those outputs.

The accepted measurement scope is December 2020 under [version 1 definitions](metric_contract.md), with all 92 days retained for source checks and transaction qualification. Total revenue, average order value and revenue per visit are unavailable. Commercial scenarios must label any assumed monetary input and identify the additional sales evidence needed.

Do not infer customer lifetime value from a short anonymous observation window, advertising return without spend data, or profit without costs. Observational differences are not causal effects. Production tracking changes and running an actual experiment are outside this study.

## Success criteria

A reviewer can reproduce published aggregates, explain denominators and exclusions, trace recommendations to evidence, and identify what additional data or experiment would change the decision. An inconclusive result or instrumentation-first recommendation is a valid outcome.
