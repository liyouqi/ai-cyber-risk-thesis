# Experiment Files

This directory contains the files used in the three-method comparison.

```text
experiments/
├── items.csv                 # common 40-item input
├── pilot_items.csv           # four rows used for the small process check
├── manual/                   # files the researcher completes
├── outputs/
│   ├── llm_only/             # saved LLM-only answers
│   └── agentic_rag/          # saved answers and retrieved evidence
├── results.csv               # one scoring row per item and method
├── candidates/               # rows extracted from the source workbooks
└── .archive/                 # old duplicate layouts; hidden and unused
```

## What to open

For Manual work, use only:

- `manual/provision_checks.csv`;
- `manual/item_summary.csv`;
- `manual/timing.csv`.

For each AI method, the two CSV files directly inside its output folder contain
all available DORA answers. The `records/` folders preserve per-item raw output,
run settings and RAG evidence; they normally do not need to be opened.

`results.csv` already has 120 rows for 40 items and three methods. The DORA AI
rows contain their measured execution time and actual number of proposed missing
mappings. Blank cells mean that Manual scoring, human review time or AI Act runs
are still missing. A numeric `0` means the completed run actually produced zero.

LLM-only and Agentic RAG use the same model configured in `.env`. Their only
substantive difference is whether Regulatory RAG evidence is supplied.
