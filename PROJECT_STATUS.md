# Thesis Project Status

Last updated: 2026-08-28

## 1. Thesis Topic

Working title:

**AI-Assisted Cybersecurity Risk Assessment in Banking**

Working subtitle:

**A Comparative Evaluation of Manual, LLM-Only, and Agentic RAG Workflows**

The thesis studies whether AI-assisted workflows can improve cybersecurity
risk assessment in a banking environment, with particular focus on efficiency,
regulatory grounding, traceability, and human review effort.

---

## 2. Thesis Scope

The thesis does NOT attempt to automate the complete bank IT risk / GRC lifecycle.

The main workflow is:

Security Case  
→ Risk Assessment Agent  
→ Regulatory Research  
→ Regulatory RAG  
→ Regulatory Evidence  
→ Preliminary Risk Assessment  
→ Human Review

The regulatory RAG is an independent existing project.

The thesis project adds:
- cybersecurity security cases;
- risk assessment agent;
- comparative experiment;
- experiment results and analysis.

Out of scope:
- automatic remediation;
- PDCA updates;
- CMDB automation;
- vulnerability ticket workflow;
- full multi-agent GRC platform;
- autonomous risk acceptance.

---

## 3. Existing Regulatory RAG

Current RAG capabilities already implemented:

- configuration-driven multi-regulation corpus;
- official EUR-Lex / local regulatory sources;
- legal-structure-aware chunking;
- BM25 retrieval;
- vector retrieval;
- RRF hybrid retrieval;
- Query Planner;
- claim-based retrieval;
- Coverage Guard;
- evidence grounding;
- citation validation;
- structured answer generation;
- extractive fallback.

Current corpus includes DORA/CSSF material and GDPR.
The wider RAG platform may later include AI Act and other regulations.

The thesis experiment will mainly use:
- DORA;
- DORA related RTS / technical standards;
- relevant CSSF ICT / cybersecurity material.

GDPR and AI Act can be mentioned as part of the broader regulatory platform,
but they are not the main experimental focus.

---

## 4. Experimental Question

Main research question:

**To what extent can an AI-assisted regulatory workflow improve the efficiency
of cybersecurity risk assessment in banking while maintaining regulatory
accuracy and traceability?**

The experiment compares three workflows:

### 01 Manual

Security Case  
→ manual technical analysis  
→ manual regulatory research  
→ manual risk assessment

### 02 LLM-only

Security Case  
→ LLM  
→ preliminary risk assessment

No regulatory RAG evidence is provided.

### 03 Agentic RAG

Security Case  
→ Risk Assessment Agent  
→ Regulatory RAG  
→ retrieved regulatory evidence  
→ preliminary risk assessment

---

## 5. Experimental Input

The experiment uses 10 representative and anonymised cybersecurity cases.

Primary source:
- vulnerability findings derived from Tenable reports.

Possible additional case types:
- security control deviation;
- patching issue;
- threat event;
- configuration weakness.

The original Tenable CSV is retained as the experiment source dataset. The
workflow inputs and thesis examples use anonymised Security Case files.

Each experiment uses a standardised Security Case, for example:

- finding type;
- technical severity;
- CVSS where applicable;
- asset criticality;
- network exposure;
- known exploitation;
- existing controls;
- remediation status;
- days outstanding;
- business / operational context.

The same Security Case must be used by all three experimental methods.

---

## 6. Evaluation Metrics

Initial metrics:

1. Total completion time
2. Regulatory citation accuracy
3. Regulatory coverage
4. Unsupported / hallucinated regulatory claims
5. Human correction effort

Potential additional metric:
- quality / reasonableness of risk assessment

The exact evaluation rubric should be frozen after the first pilot case.

---

## 7. Experiment Evidence to Keep

For every case, retain enough information to reproduce and explain the result.

### Manual
- final assessment;
- completion time;
- notes.

### LLM-only
- input;
- prompt version;
- model;
- output;
- generation time;
- human review/correction.

### Agentic RAG
- input;
- agent workflow result;
- regulatory research task;
- retrieval plan / claims;
- retrieved regulatory evidence;
- citations;
- final output;
- generation time;
- human review/correction.

Do NOT record or expose model private chain-of-thought.

---

## 8. Repository Structure

```text
experiments/
├── cases/
├── 01_manual/
├── 02_llm_only/
├── 03_agentic_rag/
└── results/

agent/
figures/
notes/
```

`regulatory-rag` remains a separate repository.

---

## 9. Thesis Structure

Current draft structure:

1. Introduction
2. Background and Related Work
3. Banking Cybersecurity Risk Assessment Workflow
4. Agentic Regulatory RAG System
5. Experimental Evaluation
6. Discussion and Conclusion

Chapter 3 first draft: started / drafted.

Chapter 4 first draft:
- System Requirements
- Overall System Architecture
- Regulatory Knowledge Base
- Document Processing and Corpus Construction
- Hybrid Retrieval
- Query Planning and Claim-Based Retrieval
- Evidence Grounding and Citation
- Risk Assessment Agent
- End-to-End Assessment Workflow

Agent implementation details must be updated after the actual implementation.

---

## 10. Current Status

### Done

- [x] Thesis repository created
- [x] EIT Digital thesis template imported into Overleaf
- [x] Working thesis title defined
- [x] Overall thesis scope reduced
- [x] Three-way experimental comparison selected
- [x] Regulatory RAG already implemented as separate project
- [x] Chapter 3 first draft prepared
- [x] Chapter 4 first draft prepared
- [x] Experiment repository structure created
- [x] Ten anonymised Security Cases prepared
- [x] Initial experiment output and result templates prepared
- [x] CASE-01 pilot run package and prompts prepared

### In Progress

- [ ] Add remaining ICT / cybersecurity-related CSSF documents to RAG corpus
- [ ] Prepare professor meeting slides
- [ ] Freeze experiment output template and scoring rubric

### Not Started

- [ ] Pilot Case 01
- [ ] Manual Case 01
- [ ] LLM-only Case 01
- [ ] Agentic RAG Case 01
- [ ] Risk Assessment Agent implementation
- [ ] Full 10-case experiment
- [ ] Results aggregation
- [ ] Chapter 5
- [ ] Final thesis revision

---

## 11. Immediate Next Steps

Do these next, in order:

1. Run CASE-01 manually
2. Run CASE-01 with LLM-only
3. Run CASE-01 through the RAG-assisted workflow
4. Complete the CASE-01 comparative result template
5. Make any small practical changes to the templates
6. Freeze the experiment design
7. Implement the thin Risk Assessment Agent and automate the Agentic RAG path
8. Run CASE-02 to CASE-10

---

## 12. Decisions Still to Confirm with Supervisor

- final thesis title;
- final research question;
- whether Manual vs LLM-only vs Agentic RAG is sufficient;
- evaluation methodology;
- graduation target and thesis timeline.

---

## 13. Important Constraints

- No confidential bank data in the thesis repository.
- No real IP addresses, hostnames or internal system names.
- Security cases must be anonymised / normalised.
- AI output remains decision support.
- Human review remains mandatory.
- Do not expand the thesis back into a full GRC / multi-agent platform.
