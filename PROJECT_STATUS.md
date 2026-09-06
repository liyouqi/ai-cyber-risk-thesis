# Project Status

Updated: 2026-09-06

Working title:

**AI-Assisted Cybersecurity Regulatory Mapping Review in Banking: A Comparative
Evaluation of Manual, LLM-Only and Agentic RAG Workflows**

## Completed

- extracted and translated the two source workbooks into one 40-item dataset;
- implemented LLM-only and Agentic RAG with the same configured model;
- completed all 20 selected DORA items with both AI methods;
- prepared a provisional local retriever over 500 official AI Act paragraphs;
- saved combined CSV answers and per-item RAG evidence;
- created the 40-item Manual working files under `experiments/outputs/manual/`;
- created `experiments/results/item_results.csv` with 120 rows and filled the
  objective DORA run data;
- prepared the thesis table layouts, reporting script and two Mermaid diagrams.

## Still missing

- 20 AI Act runs for each AI method (external LLM authorization pending);
- replacement of the provisional AI Act retriever with the final Regulatory RAG corpus;
- the researcher's Manual decisions and timing;
- human correction time and Manual-based scoring;
- final tables and figures generated from the completed scores.

The current DORA output uses corpus `dora-luxembourg-mvp-en` version `0.2.1`,
BM25 retrieval and top-k 5. Configuration details are preserved in each
`experiments/outputs/agentic_rag/records/<item_id>/run.json`.
