# AI-Assisted Cybersecurity Regulatory Mapping Review

This repository contains a master's thesis experiment on reviewing mappings
between cybersecurity controls and EU regulatory provisions. The practical
question is simple: given a control statement and its existing regulatory
mapping, does that mapping adequately cover the material control objective? If
not, which important provision is missing?

## Experiment overview

The same 40 assessment items are evaluated using three workflows:

1. **Manual** — a reviewer searches and checks official regulatory text without
   an LLM or Regulatory RAG.
2. **LLM-only** — the configured model receives the item and existing mapping,
   but no retrieved legal text and no search tools.
3. **Agentic RAG** — the same model receives evidence from an independent,
   read-only Regulatory RAG service over HTTP.

Each workflow returns one item-level `Yes` or `No` decision. `Yes` means the
existing mapping, considered as a whole, provides a sufficiently complete legal
basis for the control. `No` means a material requirement is unsupported, a
material citation is wrong, an important provision is missing, or adequate
coverage cannot be established.

## Data sources

The experiment combines two operational source workbooks:

- `source_files/AI_Tool_Onboarding_Risk_Assessment.xlsx`;
- `source_files/DORA KPI.xlsx`.

Their control statements and existing mappings are normalized into
`experiments/data/items.csv`. The final sample contains 40 items: 20 concerning
the EU AI Act and 20 concerning DORA. The source contains 63 existing AI Act
provision references and 22 existing DORA references.

`experiments/data/gold_standard.csv` contains one company-provided expert
reference decision per item, constructed from official EUR-Lex text. It contains
29 `Yes` and 11 `No` items. The Gold is used only by the final scoring script;
none of the three workflows can read it while producing answers.

## Agentic RAG workflow

Regulatory RAG runs as a separate service configured with:

```text
REGULATORY_RAG_API_URL=http://127.0.0.1:8080
```

The Agent checks `/health` and `/api/v1/status`, then calls
`POST /api/v1/retrieve`. Direct retrieval resolves the provisions already cited
by an item. Planned retrieval searches, within the permitted regulatory scope,
for material omissions. The Agent preserves the returned evidence IDs, document
IDs, text, source locations, URLs, ranks, scores, query plan and claim coverage.
It does not import the RAG package or implement its parser, BM25, vector search,
RRF or legal-text chunking.

LLM-only and Agentic RAG use the same model, temperature and item-level output
schema. Their substantive difference is the retrieved regulatory evidence.

## Evaluation

The primary metric is Coverage Accuracy against the Gold. Because the Gold is
imbalanced, the experiment also reports Yes recall, No recall and balanced
accuracy. Missing provisions are compared using normalized
`document_id::provision` identifiers and reported with Precision, Recall and F1.
Measured system execution time is reported for the two AI workflows. No
weighted overall score is calculated.

## Current results

| Workflow | Coverage accuracy | Balanced accuracy | No recall | Missing-provision F1 | Mean execution |
|---|---:|---:|---:|---:|---:|
| Manual | 87.5% | 82.9% | 72.7% | 87.5% | — |
| LLM-only | 62.5% | 43.1% | 0.0% | 0.0% | 4.93 s/item |
| Agentic RAG | 77.5% | 76.0% | 72.7% | 10.0% | 22.69 s/item |

Framework-level Coverage Accuracy is:

| Workflow | EU AI Act | DORA |
|---|---:|---:|
| Manual | 85% | 90% |
| LLM-only | 60% | 65% |
| Agentic RAG | 65% | 90% |

The current results indicate that Agentic RAG improves coverage classification
over LLM-only by 15 percentage points. The main improvement is its ability to
reject inadequate mappings: LLM-only did not correctly identify any Gold `No`
item, whereas Agentic RAG achieved 72.7% No recall. The benefit is much stronger
for DORA than for the EU AI Act.

The results do not show that retrieval solves the entire task. Agentic RAG still
performs poorly at naming the exact omitted provision, and its 77.5% raw
accuracy is only five points above the 72.5% always-`Yes` majority baseline. On
40 paired items, the observed advantage over LLM-only is not statistically
significant at the conventional 5% level (exact McNemar `p ≈ 0.146`). The
appropriate conclusion is therefore that retrieved legal evidence improves
decision balance and practical reliability, not that the Agent has replaced
expert review.

### Result status

The LLM-only and Agentic RAG answers and execution times come from completed
40-item runs. The Manual decisions were completed through manual legal review,
but review time was not recorded contemporaneously and is therefore excluded
from the measured execution-time comparison. 

## Reproduce the outputs

After the three `item_summary.csv` files are complete, score them and rebuild
the thesis tables and figures:

```bash
python scripts/update_results.py
python scripts/build_thesis_outputs.py
```

The generated material is written to:

```text
thesis_outputs/generated/
├── tables/
└── figures/
```

Run the local checks with:

```bash
python -m unittest discover -s agent/tests -v
```

See `docs/EXPERIMENT_DESIGN.md` for the methodology,
`docs/EXPERIMENT_GUIDE.md` for the operating sequence and `agent/README.md` for
the Agent/RAG boundary.
