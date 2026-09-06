# Project Status

Updated: 2026-09-06

## Current thesis direction

Working title:

**AI-Assisted Cybersecurity Regulatory Mapping Review in Banking: A Comparative
Evaluation of Manual, LLM-Only and Agentic RAG Workflows**

The thesis evaluates manual, LLM-only and Agentic RAG workflows for reviewing
existing cybersecurity control-to-regulation mappings in a banking context. The
intended use is second-line challenge and decision support, not automated legal
or compliance approval.

Primary frameworks:

- EU AI Act
- DORA and the DORA instruments present in the approved RAG corpus

## Available material

- `source_files/AI_Tool_Onboarding_Risk_Assessment.xlsx`
- `source_files/DORA KPI.xlsx`
- a separate read-only Regulatory RAG project at
  `/Users/dada/Developer/italy_proj/regulatory-rag`

The Regulatory RAG currently exposes a public Python interface and a versioned
DORA development profile. Its current corpus does not contain the EU AI Act and
must be frozen before formal experiment runs.

## Done in the current revision

- simplified the experiment protocol around mapping validation;
- defined a common CSV input schema;
- defined the same review tables for all three methods;
- extracted 25 AI Act and 22 DORA candidate items;
- selected a balanced 40-item main dataset and a four-item pilot;
- verified the public RAG interface without modifying the RAG repository;
- implemented the first one-item Agent workflow with replaceable replay and RAG
  evidence providers;
- added strict output checks and a development-only replay test;
- implemented a same-model LLM-only runner and a batch runner for both AI
  methods;
- documented the complete experiment procedure and the separate AI Act corpus
  work;
- completed real DORA end-to-end development runs with the configured external
  model for DORA-15 and the compound mapping in DORA-18;
- added exact-provision retrieval, one auditable correction retry and a final
  evidence guardrail for uncited claims.

## Waiting for input

- EU AI Act corpus in the Regulatory RAG project;

## Next steps

1. Add and validate an AI Act corpus in the separate RAG project.
2. Check AI Act retrieval through the Agent.
3. Run the four-item pilot before freezing the experiment.
