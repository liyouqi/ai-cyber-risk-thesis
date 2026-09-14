# Method Outputs

The three compared methods are kept side by side:

```text
outputs/
├── manual/
├── llm_only/
└── agentic_rag_http/
```

`manual/` contains the item-level Manual answers. The current file is visibly
marked as a pipeline preview and must be replaced before final reporting. The
two AI folders contain their saved model answers.

Each fresh experiment run writes all 40 LLM-only records to `llm_only/` and all
40 HTTP Agentic RAG records to `agentic_rag_http/`.

Open these two files for normal review:

```text
llm_only/item_summary.csv
agentic_rag_http/item_summary.csv
```

The `records/` folders contain the original response and run record for each
item. Agentic RAG records also contain `evidence.json`. Both methods use the
configured model with temperature 0. The run records preserve the actual model,
workflow and RAG corpus versions.

Correctness is calculated only by the final scoring script against the isolated
expert Gold. If the task, prompt, model or corpus changes, rerun the affected
method instead of mixing versions.
