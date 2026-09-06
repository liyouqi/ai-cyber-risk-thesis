# DORA Development Batch

This directory contains one development run for each of the 20 selected DORA
items using LLM-only and Agentic RAG. AI Act items are not included.

All `run.json` files have `eligible_for_experiment: false`. The outputs show that
the workflow runs over the complete DORA subset, but they are not frozen formal
results and have not been scored against the Manual baseline. An output label
such as `Correct` is the model's conclusion, not measured accuracy.

Both methods used the configured model with temperature 0. Agentic RAG used the
default DORA development corpus, BM25 retrieval and top-k 5. Every cited evidence
ID was checked against the saved `evidence.json`; no run required the automatic
correction retry.

Open the two CSV files at the root of each method folder for a quick spreadsheet
review. The item folders retain the original response and evidence for auditing.
