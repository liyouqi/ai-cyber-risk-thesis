# Method Outputs

The three compared methods are kept side by side:

```text
outputs/
├── manual/
├── llm_only/
└── agentic_rag_http/
```

`manual/` contains the completed item-level Manual answers. Its
`item_summary.csv` also contains `estimated_time_min` and `time_status`; every
estimated value is marked `IMPUTED_NOT_OBSERVED`. Manual review time was not
recorded contemporaneously, so these values are illustrative and must not be
presented as measured experiment data. The two AI folders contain their saved
model answers.

The timing preview totals 763 minutes across 40 items (mean 19.1 minutes;
median 18 minutes). It is a fixed planning scenario representing roughly
1.5 working days, not a retrospective measurement of the completed review.

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
