# Experiment Files

This directory contains the files used in the three-method comparison.

```text
experiments/
├── data/                     # items and isolated expert Gold
├── outputs/
│   ├── manual/               # files the researcher completes
│   ├── llm_only/             # saved LLM-only answers
│   └── agentic_rag_http/     # formal HTTP Agentic RAG batch
├── results/
│   └── item_results.csv      # one scoring row per item and method
└── rubric.md                 # scoring definitions
```

## What to open

For Manual work, use only:

- `outputs/manual/item_summary.csv`.

For each AI method, `item_summary.csv` contains the saved answers. The
`records/` folders preserve per-item raw output, run settings and RAG evidence.

`data/gold_standard.csv` is read only by final scoring. `results/item_results.csv`
has one derived scoring row per item and method. Manual execution time is blank
because it is not a software workflow; numeric `0` means a completed measurement
was zero.

LLM-only and Agentic RAG use the same model configured in `.env`. Their only
substantive difference is whether retrieved legal evidence is supplied. New
Agentic RAG runs use the separate Regulatory RAG only through its read-only HTTP
API.
