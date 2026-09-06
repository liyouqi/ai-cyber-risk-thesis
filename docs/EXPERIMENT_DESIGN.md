# Experiment Design

Working thesis title:

**AI-Assisted Cybersecurity Regulatory Mapping Review in Banking: A Comparative
Evaluation of Manual, LLM-Only and Agentic RAG Workflows**

Status: working draft. Freeze only after the pilot.

## 1. Research task

The experiment studies a second-line regulatory review task. A source workbook
contains a control or risk statement and one or more proposed legal references.
The reviewer must determine whether the mapping is supported by the official
text, whether it is too broad, and whether an important provision is missing.

The system supports review. It does not make a final legal or compliance
decision.

## 2. Research question

Can an evidence-grounded agent reduce the time needed to review existing
control-to-regulation mappings while maintaining useful legal accuracy and
traceability?

## 3. Source material

The intended frameworks are:

- EU AI Act;
- DORA, including related instruments when they are part of the frozen corpus.

Current material:

- `source_files/AI_Tool_Onboarding_Risk_Assessment.xlsx`;
- `source_files/DORA KPI.xlsx`.

The AI Act workbook contains several tables. The technical control checklist is
the most suitable starting point because it has one consistent row per control.
The DORA workbook contributes 22 candidate quantitative requirements across the
Level 1 Regulation and three Delegated Regulations. Together, the two workbooks
provide 47 candidate items. The main dataset contains 20 items from each
framework. The AI Act selection excludes the transparency and bias rows to keep
the sample centred on cybersecurity and operational controls. The selection is
purposeful rather than statistically representative.

## 4. Assessment item

One workbook row is one Assessment Item. Only fields that affect the review are
kept:

```text
Item ID
Framework
Instrument
Domain
Control or risk statement
Expected control evidence (if present)
Applicability (if present)
Existing legal mapping
Source row
```

Instrument identifies the legal text in which an article is located. Source row
is provenance, not a fact for legal reasoning; the extraction script identifies
the source workbook and sheet.

All three methods receive the same substantive item. They do not receive a
reference answer or another method's output.

## 5. Review output

The common output should remain short.

### Existing mappings

Review each cited provision separately:

```text
Provision
Supported / Partially supported / Unsupported / Unable to determine
Reason
Evidence reference
```

### Missing mappings

List only provisions that materially improve or correct the existing mapping.
Do not produce a long list of loosely related articles.

### Applicability

State any important condition, such as provider/deployer role, high-risk AI
classification, entity scope, or critical-function context. If the workbook
does not establish the condition, say so.

### Challenge comment

Give a short second-line comment stating what is acceptable, what should be
challenged, and what evidence or clarification is needed.

All methods fill the same two logical tables. One table contains a row for each
existing provision and its decision, reason and evidence. The other contains one
summary row per Assessment Item. CSV is the experiment format; it can be opened
and edited in Excel. A combined workbook may be generated later for convenience
without changing the fields.

## 6. Compared methods

### Manual

The researcher checks the official texts without an LLM or the Regulatory RAG.
Record the sources used and the time to reach a complete review.

### LLM-only

The model receives the Assessment Item and the common output instructions through
the same configured API used by the Agent. It receives no retrieved legal text
and has no browsing or search tools. Save the first response, model configuration,
generation time and human correction time.

### Agentic RAG

The agent:

1. parses the Assessment Item;
2. separates the existing legal references;
3. creates focused validation and gap-search questions;
4. calls the public Regulatory RAG interface;
5. links its conclusions to returned evidence IDs;
6. flags insufficient evidence instead of filling gaps from model memory;
7. produces the common review output.

The first implementation makes one focused validation query per cited provision
and one limited gap query per item. Changes to this behaviour must be tested in
the pilot. Observable queries and evidence are saved; private model reasoning is
not.

## 7. Experimental controls

- Use the same item and output fields for all methods.
- Use the same final model for LLM-only and Agentic RAG where possible.
- Read model and endpoint settings from environment configuration.
- Freeze model settings, prompts and corpus versions after the pilot.
- Manual and Agentic RAG review the same official source scope.
- Do not silently treat a missing corpus document as a retrieval failure.
- Preserve raw AI outputs before human correction.

## 8. Verified manual baseline

The completed Manual review is checked against the official legal text and then
used as the practical scoring baseline. Each decision records its provision,
official source and a short supporting passage. This avoids creating a fourth
workflow that repeats the same work.

The baseline is not treated as universal legal truth. If later checking shows
that a baseline decision is wrong, record the correction and rescore all methods
against the corrected decision. One researcher performs the review, so the
thesis reports this as a limitation.

## 9. Measures

Keep the result table limited to measures that answer the research question:

- time to reach an acceptable review;
- accuracy of existing-mapping classifications;
- precision and recall for material missing mappings, where the manual baseline
  makes these measures possible;
- citation support or citation errors;
- unsupported legal claims;
- human correction time and a short correction note.

Applicability handling and challenge usefulness may be discussed qualitatively
or scored after the pilot if a stable rubric is practical. Do not create one
combined quality score.

## 10. Pilot

Run TC05, TC20, DORA-15 and DORA-18 before the main experiment. Each is reviewed
by all three methods.

The pilot checks:

- whether workbook rows contain enough context;
- whether the RAG contains the necessary texts;
- whether existing citations can be parsed consistently;
- whether the output is useful to a second-line reviewer;
- whether timing and scoring can be applied consistently.

Pilot outputs are development records. Rerun the four items under the frozen
protocol before including them in the main results.

## 11. Records to keep

For every run, retain:

- item ID and source row;
- method;
- prompt/workflow version;
- model settings where applicable;
- RAG and corpus version where applicable;
- raw output;
- retrieved evidence IDs for Agentic RAG;
- execution and human review time;
- corrections and final review.

These records are sufficient for the thesis. No chain-of-thought, database or
large workflow platform is required.

## 12. Conditions before the main experiment

- both source workbooks have been inspected;
- selected items and source scope are fixed;
- the AI Act and DORA source texts required by those items are in the RAG;
- the common output and verified-manual procedure work in the pilot;
- prompts, model settings, corpus versions and timing rules are frozen.

The thesis corpus profile must have `corpus_status` set to `frozen`, a valid
`frozen_at` date, and a locked processed-corpus fingerprint before a run is
treated as formal Agentic RAG evidence.

## 13. Final analysis choices

Each AI method is run once per item with temperature 0. Applicability handling
and challenge usefulness are reported qualitatively rather than converted into
an additional ordinal score. These choices keep the workload proportionate and
avoid a weak composite quality measure.
