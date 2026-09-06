# Datasets

The files in this directory are experiment inputs, not legal conclusions.

## AI Act

`candidates/ai_act.csv` is generated from:

```text
source_files/AI_Tool_Onboarding_Risk_Assessment.xlsx
sheet: 技术控制清单IT Control CheckList
rows: TC01-TC25
```

The source workbook already contains English translations. The experiment CSV
uses those English fields so that all methods receive the same language as the
official English regulatory corpus. `source_row` preserves the link back to the
workbook.

The TC13 applicability cell has no separate English translation in the source.
The preparation script renders `生成式AI/RAG/Agent` as
`Generative AI, RAG or agent systems`; no other source wording is manually
translated.

Regenerate it with:

```bash
python scripts/prepare_ai_act_items.py
```

This is the complete candidate set, not the final selected sample.

## DORA

`candidates/dora.csv` is generated from the four sections of
`source_files/DORA KPI.xlsx`.
It contains 22 candidate items. The Chinese domains and statements are
translated directly into English by the preparation script. The translation is
for a common experiment language; it does not correct or expand the source
claim.
Because the source has no item IDs, the extractor assigns `DORA-01` to
`DORA-22` in source-row order.

Regenerate it with:

```bash
python scripts/prepare_dora_items.py
```

The `instrument` column is required because article numbers repeat across the
DORA Level 1 Regulation and its Delegated Regulations. One row also contains a
cross-instrument reference; that reference remains unchanged in
`existing_mapping`.

## Selected datasets

`pilot_items.csv` contains four items used to test the procedure before it is
frozen. It is a practice run, not a separate type of data.

`items.csv` is the common 40-item input for Manual, LLM-only and Agentic RAG.
It contains AI Act TC05-TC17 and TC19-TC25, plus 20 DORA items. DORA-09 is
excluded because it concerns a supervisory penalty rather than a cybersecurity
control review. DORA-11 is excluded because it substantially duplicates the
same provision and timing issue already represented by DORA-10.

Regenerate both selected files with:

```bash
python scripts/build_experiment_samples.py
```
