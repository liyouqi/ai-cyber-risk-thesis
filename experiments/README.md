# Experiment

The experiment reviews existing control-to-regulation mappings.

## Common input

All methods use the same CSV columns:

```text
item_id
framework
domain
control_statement
expected_evidence
applicability
existing_mapping
source_row
```

`datasets/ai_act/items.csv` is a candidate dataset extracted from the technical
control checklist in the source workbook. It contains all 25 controls; the final
sample has not been selected. The DORA dataset will be added only after its
workbook is available and inspected.

## Common output

Manual, LLM-only and Agentic RAG use the same two output tables:

- `mapping_reviews.csv`: one row for each cited provision;
- `item_reviews.csv`: one summary row for each assessment item.

The human reviewer fills these tables manually. The AI workflows produce the
same fields, initially as raw output and then as reviewed CSV rows. Method-specific
logs may differ, but the final review structure does not.

## Methods

```text
manual
llm_only
agentic_rag
```

Do not create all run folders in advance. Add them when a pilot or main run is
actually performed. Each run should contain only the copied input, the two output
tables and a short run record. AI runs must also preserve the raw response.

## Before the pilot

1. Add and inspect the DORA workbook.
2. Add a validated AI Act corpus to the separate Regulatory RAG.
3. Select a balanced set of AI Act and DORA items.
4. Test how compound article references are split.
5. Freeze the prompts, result labels and timing rules.
