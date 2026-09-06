# Review Agent

The first development version can run with replay evidence. The replay mode is
for software testing only and is never counted as Agentic RAG experiment data.

The repository also contains the LLM-only comparison runner. It reads the same
model and endpoint configuration as the Agent but does not call an evidence
provider.

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

The implementation uses a replaceable evidence-provider boundary. Replay data
tests the full workflow now; the public `RegulatoryRagEngine` adapter will supply
real evidence when the corpus is ready. Do not add a web application, database,
multi-agent framework or autonomous remediation workflow.

## Run the development version

Install the short dependency list and put the private LLM settings in `.env`.
The file is ignored by Git.

Run the tests:

```bash
python -m unittest discover -s agent/tests -v
```

Run one item with a replay evidence file:

```bash
python -m agent.main \
  --input path/to/items.csv \
  --item DEV-01 \
  --evidence replay \
  --evidence-file path/to/replay_evidence.json \
  --output path/to/new_run_folder
```

For the real adapter, set `REGULATORY_RAG_ROOT` in `.env` and replace the
evidence arguments with:

```text
--evidence rag
```

The command writes the run record, retrieved evidence, raw model response and
the two common review CSV files. Replay runs are always marked as development
outputs and cannot be marked as experiment runs.

Run one LLM-only item with the same configured model:

```bash
python -m agent.llm_only \
  --input experiments/datasets/pilot_items.csv \
  --item DORA-15 \
  --output /tmp/dora15-llm-only-dev
```

After the protocol is frozen, `agent.batch` runs either AI method over a complete
CSV dataset. Exact commands and the order of work are in
`docs/EXPERIMENT_GUIDE.md`.
