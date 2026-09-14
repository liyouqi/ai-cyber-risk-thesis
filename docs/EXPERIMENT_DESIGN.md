# Experiment Design

Working title: **AI-Assisted Cybersecurity Regulatory Mapping Review in
Banking: A Comparative Evaluation of Manual, LLM-Only and Agentic RAG
Workflows**

## Task

For each of the 40 assessment items, determine whether the existing regulatory
mapping, considered as a whole, adequately covers the material requirements of
the control. If it does not, identify any important missing provisions.

Each method returns one item-level decision:

- `Yes`: the mapping set provides a defensible and sufficiently complete
  regulatory basis for the material control objective;
- `No`: a material part is unsupported, a cited provision is materially wrong,
  an important provision is missing, or the method cannot confirm adequate
  coverage.

The regulation need not name the exact implementation technology when its
requirements clearly support that control as a reasonable implementation. A
broad or redundant citation does not make an otherwise adequate mapping `No`.

## Data and gold standard

`experiments/data/items.csv` contains the 40 common assessment items.
`experiments/data/gold_standard.csv` contains exactly one expert reference row
per item:

```text
item_id,coverage,missing_provisions,reason,source_url,evidence_excerpt
```

Missing provisions use `document_id::provision` and semicolons between multiple
references. The Gold is based on official EUR-Lex text and is a reference
standard for this experiment, not a claim of universal legal truth.

The Gold is never loaded by Manual, LLM-only or Agentic RAG. Only the final
scoring script reads it.

## Compared methods

### Manual

The reviewer checks official regulatory texts without an LLM or Regulatory RAG
and records the item-level decision, important omissions, sources and time.

### LLM-only

The model receives the assessment item and output instructions. It receives no
retrieved text and has no browsing or search tools.

### Agentic RAG

The Agent uses the independent Regulatory RAG only through its read-only HTTP
API. It retrieves every existing citation with Direct mode and searches for
material omissions with Planned mode. It then makes the same item-level
decision as the other methods and links its answer to returned evidence IDs.

The thesis project does not import the RAG package or read its data, release or
index directories. The run record preserves queries, evidence, rank, score,
source metadata, the Planned plan and claim coverage.

## Common output

Each method produces one row per item containing:

```text
item_id
coverage
reason
missing_mapping
evidence_reference
evidence_excerpt
applicability_note
challenge_comment
```

`coverage` is only `Yes` or `No`. If a method cannot determine that the mapping
is adequate, it returns `No`. Missing provisions are listed only when a clear
provision materially repairs the gap; otherwise the list is empty.

## Measures

The primary metric is:

```text
Coverage Accuracy = correctly classified items / 40
```

Because the Gold contains 29 `Yes` and 11 `No` items, also report the Yes and
No recall and their unweighted mean (balanced accuracy) to make majority-class
behaviour visible. Coverage Accuracy remains the primary metric.

For missing provisions, report true positives, false positives, false
negatives, Precision, Recall and F1. Matching uses the normalized
`document_id::provision` identifier.

The existing secondary measures remain:

- total review or completion time;
- evidence or citation errors;
- unsupported claims;
- human correction time.

No weighted overall score is used.

## Experimental controls

- All three methods receive the same 40 items and the same task definition.
- Manual, LLM-only and Agentic RAG cannot access the Gold during execution.
- LLM-only and Agentic RAG use the same model and temperature 0.
- Prompt, model, workflow and RAG corpus versions are recorded.
- Raw AI responses and Agentic RAG evidence are retained.
- Empty retrieval and service errors are recorded; the Agent does not widen the
  legal scope or invent legal support.
- Each method is run once per item. Results are scored only after the Gold is
  fixed.

## Reporting

Report overall and framework-level results for all three methods. Because all
methods assess the same items, pairwise accuracy comparisons use paired item
outcomes. Provision-level material may be retained as historical audit data but
is not part of the new experiment score.
