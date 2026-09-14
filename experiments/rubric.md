# Evaluation Rubric

The independent expert Gold in `data/gold_standard.csv` is used only by final
scoring. All three methods are evaluated against it.

## Coverage

- `Yes`: the existing mapping set adequately covers the material control
  objective.
- `No`: a material part is unsupported, a material citation is wrong, an
  important provision is missing, or the method cannot confirm adequate
  coverage.

Coverage Accuracy is the number of matching Yes/No decisions divided by 40.
Also report Yes recall, No recall and balanced accuracy so the 29/11 class
distribution is visible; these do not replace the primary metric.

## Missing provisions

Compare proposed missing provisions with the Gold using normalized
`document_id::provision` identifiers. Report TP, FP, FN, Precision, Recall and
F1. An empty list is valid when no clear omitted provision exists.

## Other measures

- Evidence error: a cited location does not exist or does not support the
  stated reason.
- Unsupported claim: a material legal or applicability claim is not supported
  by the item or cited evidence.
- Time: measured system execution time for LLM-only and Agentic RAG.

Keep one row per item and method in `results/item_results.csv`. Do not calculate
a weighted overall score.
