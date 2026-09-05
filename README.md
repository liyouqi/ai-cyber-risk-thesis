# AI-Assisted Regulatory Mapping Review

This repository contains the thesis experiment and a small review agent for
checking whether control and risk statements are correctly mapped to regulatory
provisions.

The practical task comes from second-line review work: a spreadsheet already
contains control statements and proposed legal references. The reviewer checks
whether each reference is supported, whether important provisions are missing,
and whether applicability assumptions have been stated.

The experiment compares three ways of doing that work:

1. manual review of the official texts;
2. review by an LLM without retrieved legal evidence;
3. review by an agent using the separate Regulatory RAG project.

Current source material is kept in `data/`. The AI Act workbook is available;
the DORA workbook has not yet been added.

The standard experiment dataset and output tables are under `experiments/`.
Agent development is paused until the required regulatory corpus and the DORA
source workbook are available.

See `docs/EXPERIMENT_REQUIREMENTS.md` for the experiment definition and
`agent/README.md` for the agent boundary.
