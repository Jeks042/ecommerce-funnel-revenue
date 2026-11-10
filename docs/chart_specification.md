# Visual reporting plan

The output is an illustrated commercial report supported by reproducible Python analysis. BigQuery SQL defines the approved populations and measures. Python loads reviewed aggregates; Matplotlib controls figure layout and annotation, with Seaborn used for suitable statistical comparisons.

## Planned figures

| Figure | Decision it supports | Evidence required |
|---|---|---|
| Daily recording coverage | Is a gap worth a tracking investigation before product action? | Event counts by date and type, with recording changes distinguished from shopper behaviour. |
| Ordered shopping progression | At which recorded step is progression weakest? | Nested session populations, approved ordering and explicit entry population. |
| Group comparisons | Which device or supported acquisition-context difference warrants investigation? | Counts, common definitions, date-mix checks, uncertainty and minimum coverage. |
| Definition sensitivity | Does the priority change when defensible counting rules change? | Reconciled strict/tied-step, boundary and exclusion variants. |
| Commercial scenarios | What assumptions would justify testing an opportunity? | Accepted eligible volumes, approved monetary inputs where available and clearly marked assumptions. |

Milestone 3 now delivers the ordered progression and device-comparison figures in `reports/figures/`, with PNG/SVG assets, numeric chart data, source/code hashes and dependency versions. The [journey findings](../reports/milestone_3_findings.md) and [reproduction method](funnel_analysis.md) explain them. Other figures remain planned. A revenue chart remains unavailable while financial reconciliation does not support it.

## Publication standard

Each final chart must name the question, population, period, denominator, units, source output and material exclusions. Use consistent colours, legible labels and direct annotations. Show uncertainty where the method warrants it. Separate counts, percentages and hypothetical values rather than combining incompatible measures.

Generate PNG and SVG assets directly from the approved tables through a documented command. Record source hashes, Python dependency versions and chart parameters. Check plotted values against SQL and inspect every final figure at its intended reading size. The report and portfolio should use the same reviewed chart assets.

Avoid hidden notebook state, raw identifiers in outputs and unsupported claims of lost sales or realised improvements. The report should lead with the commercial finding and action, followed by supporting charts and limits. Detailed methods belong in the technical documentation.
