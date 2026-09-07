# Method Outputs

The three compared methods are kept side by side:

```text
outputs/
├── manual/
├── llm_only/
└── agentic_rag/
```

`manual/` contains the blank files completed by the researcher. The two AI
folders contain their saved model answers.

All 40 items have LLM-only records. A fresh 40-item HTTP Agentic RAG batch is
stored at `agentic_rag_http/`; the older 20-item DORA embedded-provider batch
remains at `agentic_rag/` for historical audit only.

Open these four files for normal review:

```text
llm_only/provision_checks.csv
llm_only/item_summary.csv
agentic_rag_http/provision_checks.csv
agentic_rag_http/item_summary.csv
```

The `records/` folders contain the original response and run record for each
item. Agentic RAG records also contain `evidence.json`. Both methods used the
configured model with temperature 0. The formal Agentic RAG batch used HTTP RAG
corpus `regulatory-en` version `regulatory-core-20260907-r2`, BM25 and top-k 5.
Every cited evidence ID exists in the saved evidence.

These are real saved historical runs, but their correctness cannot be calculated until the
Manual reference decisions are filled. If the prompts, model or DORA corpus are
changed later, rerun the affected method instead of silently mixing versions.
