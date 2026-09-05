# Review Agent

Development is paused until the Regulatory RAG contains the required AI Act
material and the DORA source workbook has been inspected.

The intended agent has one job: review an existing mapping between an assessment
item and regulatory provisions. It will read the same standard dataset used by
the Manual and LLM-only experiments and will produce the same two review tables.

The expected workflow is:

```text
assessment item
  -> split the existing mapping into provisions
  -> retrieve evidence for each provision
  -> check for a small number of material omissions
  -> record applicability issues
  -> write a short second-line challenge comment
```

The Regulatory RAG remains a separate, read-only project. The public Python
interface has been tested from the local `compliance-agent` Conda environment.
The available DORA corpus is `dora-luxembourg-mvp-en` version `0.2.1`. It does
not currently contain the EU AI Act.

When development resumes, start with a direct Python adapter to the public
`RegulatoryRagEngine`. Do not add a web application, database, multi-agent
framework or autonomous remediation workflow.
