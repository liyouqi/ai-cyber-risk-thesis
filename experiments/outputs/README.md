# AI Outputs

The 20 selected DORA items have been run once with both LLM-only and Agentic
RAG. AI Act items are the only AI outputs still missing.

Open these four files for normal review:

```text
llm_only/provision_checks.csv
llm_only/item_summary.csv
agentic_rag/provision_checks.csv
agentic_rag/item_summary.csv
```

The `records/` folders contain the original response and run record for each
item. Agentic RAG records also contain `evidence.json`. Both methods used the
configured model with temperature 0. Agentic RAG used DORA corpus version 0.2.1,
BM25 retrieval and top-k 5. Every cited evidence ID exists in the saved evidence.

These are real saved runs, but their correctness cannot be calculated until the
Manual reference decisions are filled. If the prompts, model or DORA corpus are
changed later, rerun the affected method instead of silently mixing versions.
