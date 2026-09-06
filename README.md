# AI-Assisted Cybersecurity Regulatory Mapping Review

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

Current source material is kept in `source_files/`. Candidate experiment datasets
have been extracted from one AI Act workbook and one DORA workbook.

The standard experiment dataset and output tables are under `experiments/`. A
small command-line agent is under `agent/`. It can be developed with replay
evidence, but only runs made against a complete frozen regulatory corpus may be
used as Agentic RAG experiment results.

See `docs/EXPERIMENT_DESIGN.md` for the research design,
`docs/EXPERIMENT_GUIDE.md` for the exact operating sequence and
`agent/README.md` for the Agent boundary.

Run the local checks with:

```bash
python -m unittest discover -s agent/tests -v
```
