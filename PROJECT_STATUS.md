# Project Status

Updated: 2026-09-06

Working title:

**AI-Assisted Cybersecurity Regulatory Mapping Review in Banking: A Comparative
Evaluation of Manual, LLM-Only and Agentic RAG Workflows**

## Completed

- extracted and translated the two source workbooks into one 40-item dataset;
- implemented LLM-only and Agentic RAG with the same configured model;
- completed all 20 selected DORA items with both AI methods;
- migrated the formal Agentic RAG path to the independent read-only HTTP API;
- retained the extracted AI Act paragraphs only as historical preparation data,
  not as an experiment retrieval backend;
- saved combined CSV answers and per-item RAG evidence;
- created the 40-item Manual working files under `experiments/outputs/manual/`;
- created `experiments/results/item_results.csv` with 120 rows and filled the
  objective DORA run data;
- prepared the thesis table layouts, reporting script and two Mermaid diagrams.

## Still missing

- 20 AI Act runs for each AI method (external LLM authorization pending);
- a reachable Regulatory RAG HTTP service with AI Act and Planned retrieval;
- the researcher's Manual decisions and timing;
- human correction time and Manual-based scoring;
- final tables and figures generated from the completed scores.

The saved DORA output uses the former embedded provider with corpus
`dora-luxembourg-mvp-en` version `0.2.1`, BM25 retrieval and top-k 5. It remains
an auditable historical run, but the final HTTP-based experiment should use a
new output directory (or explicitly archive and replace the old records) so
provider implementations are not silently mixed.
