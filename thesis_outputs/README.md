# Thesis Outputs

This directory is reserved for material used in Chapters 4 and 5.

`system_diagrams.md` contains two Mermaid drafts. Reproducible result tables and
figures are kept only in `generated/`.

Run:

```bash
python scripts/build_thesis_outputs.py
```

The script creates three CSV tables and three PNG figures:

```text
generated/
├── tables/
│   ├── table_dataset_summary.csv
│   ├── table_overall_results.csv
│   └── table_framework_results.csv
└── figures/
    ├── fig_5_1_execution_time.png
    ├── fig_5_2_mapping_accuracy.png
    └── fig_5_3_missing_detection.png
```

The PNG files are reproducible drafts suitable for the thesis or presentation
slides. Do not edit the numbers manually; regenerate the files from the CSV
results.

Elapsed time uses observed item-level review time for Manual and measured
wall-clock run time for the AI workflows. Applicability and challenge quality
remain qualitative because the experiment has no independent rating scale for
them.

Model, prompt, workflow and corpus versions are already preserved in each AI
run's `run.json`. They are not repeated as manually copied columns in
`item_results.csv`, which reduces transcription errors while retaining the raw
record.
