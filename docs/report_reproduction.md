# Regenerating the commercial report figures

The [commercial report](../reports/commercial_report.md) and [decision memo](../reports/decision_memo.md) use four figures. Two accepted milestone 3 figures are reused; two additional figures show the recording coverage and conditional scenarios. No source row, identifier, credential or notebook state is needed.

## Inputs and grains

| Figure | Approved input | Grain and handling |
|---|---|---|
| recording_coverage | tracking-timing-20261106.json, linked to its native SQL receipt | Sum source-event counts over the three devices for each of 92 dates. Require every device/date cell exactly once. Reject missing/null counts; never fill a missing date with zero. Separate panel scales; these are not funnel rates. |
| recorded_journey | funnel-analysis-20261110.json | Nested December eligible-visit populations and explicit preceding-step denominators under contract v1. Reuse the accepted renderer. |
| device_progression | funnel-analysis-20261110.json | Desktop/mobile comparison with each transition's daily denominator weights. Show observed counts, date-adjusted gaps and leave-one-date-out sensitivity; no confidence interval. Reuse the accepted renderer. |
| cart_scenarios | opportunity-analysis-20261110.json and scenario-assumptions-v1.json | Fifteen hypothetical cases at a fixed reference-cohort size. One cart-rate change per row, three marginal downstream assumptions. Decimal labels round half up; values are visit equivalents, not sales or probability bounds. |

All inputs live under `reports/evidence/`. `report-plot-data-20261110.json` records the data behind every figure. The report receipt records input, code, document and asset hashes. Existing measurement/native-run receipts remain unchanged.

Acquisition context remains a short explanation linked to the full findings, because it supports no marketing allocation. Definition sensitivity is explained beside the observed funnel; a separate figure would repeat the same point. No revenue, causal-effect or historical significance chart is supported. Prospective power illustrations remain in the experiment proposal and are not mixed with observed visit comparisons.

## Local commands

Use Python 3.12.14 in an isolated environment and install the pinned chart dependencies:

```sh
python -m pip install -r requirements-analysis.txt
python tests/run_project_validation.py
python src/plotting/build_report.py --output private/report-build
python tests/check_report_render.py private/report-build
```

The build writes eight PNG/SVG files under `private/report-build/figures/` and a `build-manifest.json`. This is an ignored review directory. It does not overwrite the published assets or earlier execution receipts. The two existing figures are reproduced by the unchanged accepted renderer in an isolated subdirectory; its chart data must reconcile to the report data. Review generated images before copying any revised figure into `reports/figures/`.

On the accepted Windows environment, all four existing milestone 3 asset files reproduced byte for byte. Raster/font and SVG differences can occur across platforms, so cross-platform acceptance requires identical numeric chart data, expected valid image files and their actual build hashes rather than assuming identical image bytes. The published assets retain their reviewed hashes. Inspect every final PNG at report reading size for labels, overlaps, crop and meaning.

The build is intentionally deterministic about date ordering, scenario ordering, labels and SVG timestamps/hash salt. Colours distinguish observed charts from the explicitly labelled hypothetical scenario chart. For plotting API details, see the official [Seaborn heatmap documentation](https://seaborn.pydata.org/generated/seaborn.heatmap.html) and [Matplotlib figure export documentation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html).

## Validation and workflows

The existing credential-free analytical workflow continues unchanged. New report tests are discovered by its regression suite and check data reconciliation, complete daily coverage, missingness, scenario-cell completeness, decimal labels, source/asset/document freshness and report links.

A separate read-only workflow, `report-validation.yml`, installs the pinned chart dependencies, checks the report evidence, actually regenerates all four figures and validates the eight files and numeric plotting data. It retains the regenerated figures and build manifest for 30 days. Neither workflow has warehouse credentials, runs paid queries or commits as a bot. The new workflow adds rendering evidence without rewriting the accepted milestone 4 workflow hash.

No new BigQuery query or inference is introduced. The coverage chart traces to the existing source audit SQL; the other figures trace through the accepted analytical tables and scenario arithmetic. Final independent end-to-end reproduction and public case-study release remain milestone 6.
