# Experiment

The experiment reviews existing control-to-regulation mappings.

## Common input

All methods use the same CSV columns:

```text
item_id
framework
instrument
domain
control_statement
expected_evidence
applicability
existing_mapping
source_row
```

`datasets/candidates/ai_act.csv` contains 25 candidate controls from the AI Act
workbook. `datasets/candidates/dora.csv` contains 22 candidate quantitative
requirements from the DORA workbook.

Keep the candidate files separate so their origin remains obvious. The selected
rows are combined into one input file for each stage:

```text
datasets/pilot_items.csv
datasets/items.csv
```

`pilot_items.csv` contains TC05, TC20, DORA-15 and DORA-18. `items.csv`
contains 20 items from each framework. The pilot items remain part of the main
sample, but they must be rerun after the protocol is frozen.

## Common output

Manual, LLM-only and Agentic RAG use the same two output tables:

- `mapping_reviews.csv`: one row for each cited provision;
- `item_reviews.csv`: one summary row for each assessment item.

The human reviewer fills these tables manually. The AI workflows produce the
same fields, initially as raw output and then as reviewed CSV rows. Method-specific
logs may differ, but the final review structure does not.

Keep the completed output files separate by method. Combine only the evaluation
results in `results/item_results.csv`; do not put Manual and AI answers in one
working file while the experiment is running.

Blank Manual forms can be created with `scripts/prepare_manual_review.py`. The
current four-item pack and the completed DORA development calls are described in
`runs/README.md`.

## Methods

```text
manual
llm_only
agentic_rag
```

Do not create all run folders in advance. Add them when a pilot or main run is
actually performed. Each run contains a run record and the two output tables.
AI runs also preserve the raw response; Agentic RAG runs preserve the retrieved
evidence.

LLM-only and Agentic RAG both use `PRIVATE_AI_MODEL` from `.env`. Their difference
is the presence or absence of retrieved evidence, not a different chat product.
Follow `docs/EXPERIMENT_GUIDE.md` for the exact order and commands.

After scoring is complete, `scripts/build_thesis_outputs.py` creates the small
set of reproducible Chapter 5 tables and figures described in
`thesis_outputs/README.md`.

## Before the pilot

1. Add a validated AI Act corpus to the separate Regulatory RAG.
2. Test how compound article references are split.
3. Run the four pilot items.
4. Freeze the prompts, result labels and timing rules.
