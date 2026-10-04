# Thesis Outputs

This directory is reserved for material used in Chapters 4 and 5.

`system_diagrams.md` contains two Mermaid drafts. Reproducible result tables and
figures are kept only in `generated/`.

Run:

```bash
python scripts/build_thesis_outputs.py
```

The script creates three CSV tables and three SVG figures:

```text
generated/
├── tables/
│   ├── table_dataset_summary.csv
│   ├── table_overall_results.csv
│   └── table_framework_results.csv
└── figures/
    ├── fig_5_1_execution_time.svg
    ├── fig_5_2_mapping_accuracy.svg
    └── fig_5_3_missing_detection.svg
```

The figures are reproducible drafts. SVG files can be imported into draw.io,
PowerPoint, Inkscape or another tool for final thesis styling. Do not
edit the numbers manually; regenerate the files from the CSV results.

The revised **Figure 5.2**, "Coverage decision and missing-provision
detection performance", combines the two tasks in one figure. Regenerate it with:

```bash
python scripts/build_coverage_missing_figure.py
```

This produces `fig_5_2_coverage_and_missing_detection.svg`, `.pdf` and a 300 dpi
`.png` in `generated/figures/`. Use this combined figure in place of the separate
coverage and missing-detection drafts above. Panel (a) places Accuracy and
chance-corrected agreement (CCA) together; panel (b) shows micro-aggregated
exact-match Precision, Recall and F1. Every value is computed from
`experiments/results/item_results.csv`.

The combined figure groups bars by metric on the x-axis. Workflow colors are
consistent across both panels: Manual Review (`#3B5B7A`), LLM-only Review
(`#C96A3D`) and Agentic RAG Review (`#4F8A83`), with one shared legend. Both panels have
task titles, and all bars have one-decimal value labels, including zero values
and negative CCA. Tight bounding-box export keeps margins small. Add the figure
number and overall caption in the thesis document.
Both panels label the y-axis "Metric value (%)".

The execution-time and framework-accuracy figures use the same workflow colors,
typography and tight export settings, with SVG, PDF and 300 dpi PNG outputs.
These two standalone figures have no embedded titles; their titles belong in
the thesis captions. The combined figure retains its two panel task titles.
The time figure retains its item-level boxplots, mean markers and logarithmic
seconds axis. Framework accuracy retains all six results and displays equivalent
percentage values, grouped by framework. Panel (a) of the combined figure is
titled "Coverage Decision" and uses a -30 to 105 y-axis to leave room below the
negative CCA label.

CCA is Cohen's kappa multiplied by 100: `100 * (p_o - p_e) / (1 - p_e)`, where
`p_o` is observed accuracy and `p_e` is expected agreement from the observed Gold
and predicted class marginals. Zero denotes chance-level agreement, so negative
CCA values remain visible below the zero line.

Suggested caption: **Figure 5.2. Coverage decision and missing-provision
detection performance.** (a) Item-level Accuracy and CCA for the 40-item sample.
(b) Micro-aggregated exact-match Precision, Recall and F1 for detecting missing
provisions. Agentic RAG improves coverage agreement over LLM-only, while its
ability to identify the exact missing provisions remains limited.

Elapsed time uses observed item-level review time for Manual and measured
wall-clock run time for the AI workflows. Applicability and challenge quality
remain qualitative because the experiment has no independent rating scale for
them.

Model, prompt, workflow and corpus versions are already preserved in each AI
run's `run.json`. They are not repeated as manually copied columns in
`item_results.csv`, which reduces transcription errors while retaining the raw
record.
