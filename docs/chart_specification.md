# Visual reporting plan

The output is an illustrated commercial report supported by reproducible Python analysis. BigQuery SQL defines the approved populations and measures. Python loads reviewed aggregates; Matplotlib controls figure layout and annotation, with Seaborn used for suitable statistical comparisons.

## Reviewed report figures

| Figure | Decision it supports | Evidence required |
|---|---|---|
| recording_coverage | Why restrict the primary comparison to December? | 92 days of source-event counts, 18 observed zero-cart dates and the selected month. No gap filling or funnel-rate interpretation. |
| recorded_journey | Where is recorded progression weakest? | Nested December visit populations, timestamp ordering and explicit preceding-step denominators. |
| device_progression | Does the evidence support a mobile-only response? | Observed counts, common-date weighting and date-sensitivity ranges for the two largest entry groups. Tablet counts remain visible without ranked rates. |
| cart_scenarios | How much do hypothetical outcomes depend on assumptions? | Five assumed cart-rate changes × three marginal downstream assumptions. Hypothetical visit equivalents, including zero/downside; no revenue or probability bounds. |

All four figures are available as PNG/SVG assets in `reports/figures/`. The [commercial report](../reports/commercial_report.md) explains their implications. Acquisition context and definition sensitivity stay in concise prose and the supporting findings because additional figures would repeat the decision or invite unsupported marketing interpretation. A revenue chart remains unavailable. [Report reproduction](report_reproduction.md) records input grains, code, dependency pins and checks.

## Publication standard

Each final chart must name the question, population, period, denominator, units, source output and material exclusions. Use consistent colours, legible labels and direct annotations. Show uncertainty where the method warrants it. Separate counts, percentages and hypothetical values rather than combining incompatible measures.

Generate PNG and SVG assets directly from the approved tables through a documented command. Record source hashes, Python dependency versions and chart parameters. Check plotted values against SQL and inspect every final figure at its intended reading size. The report and portfolio should use the same reviewed chart assets.

Avoid hidden notebook state, raw identifiers in outputs and unsupported claims of lost sales or realised improvements. The report should lead with the commercial finding and action, followed by supporting charts and limits. Detailed methods belong in the technical documentation.
