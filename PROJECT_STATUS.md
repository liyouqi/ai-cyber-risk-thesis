# Project Status

Updated: 2026-09-06

## Current thesis direction

The thesis evaluates manual, LLM-only and Agentic RAG workflows for reviewing
existing control-to-regulation mappings in a banking context. The intended use
is second-line challenge and decision support, not automated legal or compliance
approval.

Primary frameworks:

- EU AI Act
- DORA and the DORA instruments present in the approved RAG corpus

## Available material

- `data/AI_Tool_Onboarding_Risk_Assessment.xlsx`
- a separate read-only Regulatory RAG project at
  `/Users/dada/Developer/italy_proj/regulatory-rag`

The Regulatory RAG currently exposes a public Python interface and a frozen
DORA corpus profile. Its current corpus does not contain the EU AI Act.

## Done in the current revision

- simplified the experiment protocol around mapping validation;
- defined a common CSV input schema;
- defined the same review tables for all three methods;
- verified the public RAG interface without modifying the RAG repository;
- paused Agent development until the missing inputs are available.

## Waiting for input

- DORA mapping workbook;
- EU AI Act corpus in the Regulatory RAG project;
- final sample size and item selection after both source workbooks are known.

## Next steps

1. Inspect the DORA workbook when it is added.
2. Add and validate an AI Act corpus in the separate RAG project.
3. Select the pilot items.
4. Implement the Agent against the frozen input and output tables.
5. Run a small pilot before freezing the experiment.
