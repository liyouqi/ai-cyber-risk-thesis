# Experiment Evaluation Criteria

This rubric is used to compare the Manual, LLM-only, and Agentic RAG workflows.
It is intentionally practical: the aim is to evaluate whether each workflow can
produce a useful preliminary cybersecurity risk assessment, not to create a
perfect or fully objective risk model.

For LLM-only and Agentic RAG, score the initial generated output before human
correction. Record the corrected version and correction effort separately.

## 1. Proposed risk level

Record the level proposed by each workflow:

**Critical / High / Medium / Low / Unable to Determine**

Also compare the AI result with the Manual result:

- Same level
- One level difference
- More than one level difference
- Not comparable

The Manual result is the practical comparison baseline, not an absolute ground
truth. Explain important differences in the case notes.

## 2. Risk assessment quality — core metric

Evaluate whether the proposed level and its rationale make sense based on the
case. The assessment should distinguish the scanner severity from the wider
risk judgement and should acknowledge important missing information.

| Score | Meaning |
|---:|---|
| 0 | No usable risk conclusion, or the conclusion is materially misleading |
| 1 | Mainly repeats the scanner severity with little meaningful reasoning |
| 2 | Plausible conclusion, but important factors or limitations are missing |
| 3 | Reasonable risk level supported by clear evidence and limitations |
| 4 | Strong, balanced and well-prioritised risk judgement |

## 3. Technical assessment quality

Evaluate the interpretation of the vulnerability, affected assets,
exploitability, potential impact, persistence and remediation information.

| Score | Meaning |
|---:|---|
| 0 | Incorrect or misleading |
| 1 | Major technical problems or omissions |
| 2 | Generally reasonable but incomplete |
| 3 | Correct and sufficiently complete |
| 4 | Correct, complete and clearly prioritised |

## 4. Regulatory assessment quality

Evaluate whether the identified DORA, related technical standards or CSSF
requirements are relevant to the case and are explained clearly.

| Score | Meaning |
|---:|---|
| 0 | No meaningful or correct regulatory analysis |
| 1 | Mostly vague, irrelevant or incorrect |
| 2 | Some relevant points, with noticeable gaps |
| 3 | Relevant and sufficiently complete |
| 4 | Strong, focused and well-supported regulatory analysis |

## 5. Citation accuracy and traceability

Check each regulatory citation against the cited source and record it as:

- Supported
- Partially supported
- Unsupported
- Unverifiable

Record the counts and use the following simple calculation:

```text
Citation accuracy = supported citations / total citations × 100
```

If the output contains no citations, record `N/A — no citations provided`.

## 6. Unsupported claims

Count material statements presented as facts that are not supported by the
Security Case or regulatory evidence. Typical examples include invented
internet exposure, exploitation, business impact, controls, deadlines or
remediation ownership.

**Lower is better.** Briefly quote or describe every counted claim.

## 7. Human correction effort

Evaluate how much work is needed to turn the initial output into an acceptable
preliminary assessment.

| Score | Meaning |
|---:|---|
| 0 | No meaningful correction |
| 1 | Minor wording or formatting changes |
| 2 | Several factual, regulatory or structural corrections |
| 3 | Major corrections or substantial rewriting |
| 4 | Output is not practically usable without rewriting |

Record the actual review time in minutes as well as the score.

## 8. Completion time

Record actual elapsed time:

- Manual: case review, research and writing time
- LLM-only: generation time plus human review time
- Agentic RAG: workflow time plus human review time

Prompt and system development time is discussed separately and is not added to
each case.

## 9. Overall usability

| Score | Meaning |
|---:|---|
| 0 | Not usable |
| 1 | Usable only after major rework |
| 2 | Partly usable |
| 3 | Usable after normal human review |
| 4 | Strong draft requiring minimal review |

## 10. Scoring notes

- Do not calculate one combined total score; compare the metrics separately.
- Do not penalise an output for clearly stating that information is unavailable.
- Do penalise invented facts.
- Keep the score explanation to one or two sentences.
- Test the rubric on CASE-01 and then use the same rubric for CASE-02 to CASE-10.
