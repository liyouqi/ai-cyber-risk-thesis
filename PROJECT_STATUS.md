# Project Status

Updated: 2026-09-20

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
- completed the Manual legal review for all 40 items and recorded item-level
  review time;
- created `experiments/results/item_results.csv` with 120 rows and filled the
  objective AI run data;
- prepared the generated thesis tables, three figures and two Mermaid diagrams;
- completed the 20 remaining AI Act LLM-only runs;
- completed a fresh 40-item HTTP Agentic RAG batch using corpus
  `regulatory-en` version `regulatory-core-20260907-r2`, hybrid retrieval and
  top-k 8.

## Still missing

- document in the thesis that the company-provided Gold was fixed before
  scoring and unavailable to the three workflows;
- explain the purposive sample exclusions in the methodology;
- review the generated tables and figures for final thesis styling.

The formal 40-item HTTP batch is stored at
`experiments/outputs/agentic_rag_http/`.
