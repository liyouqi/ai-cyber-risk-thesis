# Experiment Requirements

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

- `data/AI_Tool_Onboarding_Risk_Assessment.xlsx`;
- a DORA workbook to be added later.

The AI Act workbook contains several tables. The technical control checklist is
the most suitable starting point because it has one consistent row per control.
Final item selection and sample size will be decided after the DORA workbook is
available. The earlier proposal of 20 items per framework is not yet fixed.

## 4. Assessment item

One workbook row is one Assessment Item. Only fields that affect the review are
kept:

```text
Item ID
Framework
Domain
Control or risk statement
Expected control evidence (if present)
Applicability (if present)
Existing legal mapping
Source sheet and row
```

Source sheet and row are provenance, not facts for legal reasoning.

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

The model receives the Assessment Item and the common output instructions. It
does not receive retrieved legal text and may not browse the web. Save the model
configuration, raw output, generation time and human correction time.

### Agentic RAG

The agent:

1. parses the Assessment Item;
2. separates the existing legal references;
3. creates focused validation and gap-search questions;
4. calls the public Regulatory RAG interface;
5. links its conclusions to returned evidence IDs;
6. flags insufficient evidence instead of filling gaps from model memory;
7. produces the common review output.

The exact retry and coverage behaviour will be decided during development and
tested in the pilot. Observable queries and evidence are saved; private model
reasoning is not.

## 7. Experimental controls

- Use the same item and output fields for all methods.
- Use the same final model for LLM-only and Agentic RAG where possible.
- Read model and endpoint settings from environment configuration.
- Freeze model settings, prompts and corpus versions after the pilot.
- Manual and Agentic RAG review the same official source scope.
- Do not silently treat a missing corpus document as a retrieval failure.
- Preserve raw AI outputs before human correction.

## 8. Reference review

Each selected item needs a careful reference review based on the official legal
text. The reference records decisions for existing provisions, material missing
provisions, applicability conditions and supporting passages.

The same researcher may create and score the reference set. This single-reviewer
design will be stated as a limitation. To reduce avoidable bias, experiment
outputs should be saved first and scored later without method labels where
practical.

## 9. Measures

Keep the result table limited to measures that answer the research question:

- time to reach an acceptable review;
- accuracy of existing-mapping classifications;
- precision and recall for material missing mappings, where a reference set
  makes these measures possible;
- citation support or citation errors;
- unsupported legal claims;
- human correction time and a short correction note.

Applicability handling and challenge usefulness may be discussed qualitatively
or scored after the pilot if a stable rubric is practical. Do not create one
combined quality score.

## 10. Pilot

Run a small pilot before selecting the full dataset. The preferred pilot is two
AI Act items and two DORA items, each reviewed by all three methods.

The pilot checks:

- whether workbook rows contain enough context;
- whether the RAG contains the necessary texts;
- whether existing citations can be parsed consistently;
- whether the output is useful to a second-line reviewer;
- whether timing and scoring can be applied consistently.

Pilot results should be excluded or rerun if the protocol changes materially.

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
- the common output and reference-review procedure work in the pilot;
- prompts, model settings, corpus versions and timing rules are frozen.

## 13. Known open decisions

- final DORA item structure;
- final sample size;
- number of AI runs per item;
- whether applicability and challenge quality receive ordinal scores.
