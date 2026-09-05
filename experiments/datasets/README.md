# Datasets

The files in this directory are experiment inputs, not legal conclusions.

## AI Act

`ai_act/items.csv` is generated from:

```text
data/AI_Tool_Onboarding_Risk_Assessment.xlsx
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

No DORA dataset is created yet. Its source workbook has a different structure
and must be inspected before conversion to the common columns.
