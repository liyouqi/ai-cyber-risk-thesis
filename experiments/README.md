# Experiment Files

This directory contains the files used in the three-method comparison.

```text
experiments/
├── data/                     # input data
├── outputs/
│   ├── manual/               # files the researcher completes
│   ├── llm_only/             # saved LLM-only answers
│   ├── agentic_rag/          # historical embedded-provider records
│   └── agentic_rag_http/     # formal HTTP Agentic RAG batch
├── results/
│   └── item_results.csv      # one scoring row per item and method
└── rubric.md                 # scoring definitions
```

## What to open

For Manual work, use only:

- `outputs/manual/provision_checks.csv`;
- `outputs/manual/item_summary.csv`;
- `outputs/manual/timing.csv`.

For each AI method, the two CSV files directly inside its output folder contain
the saved answers. The `records/` folders preserve per-item raw output, run
settings and RAG evidence; they normally do not need to be opened.

`results/item_results.csv` already has 120 rows for 40 items and three methods. The DORA AI
rows contain their measured execution time and actual number of proposed missing
mappings. Blank cells mean that Manual scoring or human review time is still
missing. A numeric `0` means the completed run actually produced zero.

LLM-only and Agentic RAG use the same model configured in `.env`. Their only
substantive difference is whether retrieved legal evidence is supplied. New
Agentic RAG runs use the separate Regulatory RAG only through its read-only HTTP
API. The local AI Act extraction is historical preparation data and is not an
experiment retrieval backend.
