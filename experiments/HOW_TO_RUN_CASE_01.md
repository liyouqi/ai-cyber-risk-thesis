# How to Run the CASE-01 Pilot

CASE-01 is a practice run. Its purpose is to confirm that the workflow and
templates are understandable before running CASE-02 to CASE-10.

## What is already known

| Item | CASE-01 value |
|---|---|
| Finding | VMware ESXi multiple vulnerabilities (VMSA-2025-0004) |
| Scanner severity | Critical |
| Assets | Two critical production physical hosts |
| Main technical concern | VM-to-host code execution, sandbox escape and information disclosure |
| VPR | 9.3 |
| EPSS | 8.2% |
| Observation period | 69 days |
| Internet exposure | Unknown |
| Existing controls | Unknown |
| Business service dependency | Unknown |
| Remediation | Upgrade to a fixed ESXi release |

Scanner severity is an input. The proposed risk level is an assessment result;
it does not have to be identical to the scanner severity.

## Part A — Manual

1. Open `cases/thesis_security_cases_v1/cases/case_01.json`.
2. Start a timer.
3. Analyse the technical risk and consult the regulatory sources you would
   normally use.
4. Write the assessment in `01_manual/case_01/run.md`.
5. Stop the timer when the first complete assessment is ready.
6. Record only the sources actually consulted.

Do not read the LLM-only or Agentic RAG output before completing the Manual run.

## Part B — LLM-only

1. Start a fresh model conversation with web search and external tools disabled.
2. Paste `prompts/llm_only_prompt_v1.md`.
3. Paste the complete CASE-01 JSON where indicated.
4. Start timing immediately before sending the prompt.
5. Save the first response unchanged in `02_llm_only/case_01/run.md`.
6. Review the response, note corrections and record the review time.

## Part C — Agentic RAG

1. Submit CASE-01 through the Regulatory RAG workflow using
   `prompts/agentic_rag_task_v1.md`.
2. Save the queries, returned evidence, citations and initial assessment in
   `03_agentic_rag/case_01/run.md`.
3. Review the output and record the review time.

## Part D — Compare the three results

Complete `results/case_01_result.md` after all three runs. Score the initial
output, not the corrected wording. Use `evaluation_rubric.md` when a score is
unclear.

The comparison paragraph can be short. A natural example is:

> The LLM-only workflow produced the fastest initial response, but it required
> correction of one unsupported assumption and provided limited regulatory
> support. The Agentic RAG output took slightly longer to generate but provided
> clearer evidence and required less regulatory correction. The Manual workflow
> took the most time but produced a more cautious assessment of missing context.

Only use this wording if it matches the actual results.
