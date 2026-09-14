# Thesis Outputs

This directory is reserved for material used in Chapters 4 and 5.

`system_diagrams.md` contains two Mermaid drafts. Reproducible result tables and
figures are kept only in `generated/`.

Run:

```bash
python scripts/build_thesis_outputs.py
```

The script creates three CSV tables and four SVG figures:

```text
generated/
├── tables/
│   ├── table_dataset_summary.csv
│   ├── table_overall_results.csv
│   └── table_framework_results.csv
└── figures/
    ├── fig_5_1_execution_time.svg
    ├── fig_5_2_mapping_accuracy.svg
    ├── fig_5_3_missing_detection.svg
    └── fig_5_4_reliability_errors.svg
```

The SVG files are transparent, reproducible drafts. They can be imported into
draw.io, PowerPoint, Inkscape or another tool for final thesis styling. Do not
edit the numbers manually; regenerate the files from the CSV results.

Execution time uses measured AI run time only. Manual has no software execution
time. Applicability and challenge quality remain qualitative because the
experiment has no independent rating scale for them.

Model, prompt, workflow and corpus versions are already preserved in each AI
run's `run.json`. They are not repeated as manually copied columns in
`item_results.csv`, which reduces transcription errors while retaining the raw
record.
