# Project Status

Updated: 2026-09-07

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
  objective AI run data;
- prepared the thesis table layouts, reporting script and two Mermaid diagrams.
- completed the 20 remaining AI Act LLM-only runs;
- completed a fresh 40-item HTTP Agentic RAG batch using corpus
  `regulatory-en` version `regulatory-core-20260907-r2`, BM25 and top-k 5.

## Still missing

- the researcher's Manual decisions and timing;
- human correction time and Manual-based scoring;
- final tables and figures generated from the completed scores.

The saved DORA output under `experiments/outputs/agentic_rag/` uses the former
embedded provider and remains an auditable historical run. The formal 40-item
HTTP batch is stored separately at `experiments/outputs/agentic_rag_http/`; its
objective values have replaced the Agentic RAG rows in the result table.
