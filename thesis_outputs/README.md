# Thesis Outputs

This directory is reserved for material used in Chapters 4 and 5.

`system_diagrams.md` contains two Mermaid drafts that should be redrawn or
restyled before submission. Generated result tables and figures are created in a
new `generated/` directory only after `experiments/results/item_results.csv` has
been completed.

The table layouts can be prepared before the scores exist:

```bash
python scripts/build_thesis_outputs.py \
  --skeleton \
  --output thesis_outputs/prepared
```

This creates three tables with blank result cells and does not create misleading
zero-valued figures. A prepared copy is already kept in `prepared/`.

Run:

```bash
python scripts/build_thesis_outputs.py
```

The script creates three CSV tables and six SVG figures:

```text
generated/
├── tables/
│   ├── table_dataset_summary.csv
│   ├── table_overall_results.csv
│   └── table_framework_results.csv
└── figures/
    ├── fig_5_1_review_time.svg
    ├── fig_5_2_mapping_accuracy.svg
    ├── fig_5_3_missing_detection.svg
    ├── fig_5_4_reliability_errors.svg
    ├── fig_5_5_correction_time.svg
    └── fig_5_6_paired_time.svg
```

The SVG files are transparent, reproducible drafts. They can be imported into
draw.io, PowerPoint, Inkscape or another tool for final thesis styling. Do not
edit the numbers manually; regenerate the files from the CSV results.

The longer proposal of eight figures and five tables was deliberately reduced.
Manual accuracy is not plotted because Manual is the scoring baseline.
Applicability, challenge quality and overall usability remain qualitative
because the experiment has no reliable independent rating scale for them.
Representative cases should be selected only after reviewing the results, and a
statistical-test table should be added only if the final analysis justifies a
specific test.

Model, prompt, workflow and corpus versions are already preserved in each AI
run's `run.json`. They are not repeated as manually copied columns in
`item_results.csv`, which reduces transcription errors while retaining the raw
record.
