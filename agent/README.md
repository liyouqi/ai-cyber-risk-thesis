# Review Agent

The Agent checks an existing control-to-regulation mapping. It splits compound
references, retrieves relevant legal text, checks each cited provision, searches
for a small number of material omissions and writes a short summary.

LLM-only uses the same configured model and output format without retrieval.
Replay evidence exists only for automated software tests.

The Regulatory RAG remains a separate read-only project. The current corpus is
`dora-luxembourg-mvp-en` version `0.2.1`; AI Act is not available yet.

## Output

A batch produces two files intended for normal use:

```text
provision_checks.csv
item_summary.csv
```

Detailed files are kept under `records/<item_id>/`: the run settings, original
model response and, for Agentic RAG, retrieved evidence. If validation fails,
the Agent makes one correction attempt and saves both responses.

## Commands

Run the tests:

```bash
python -m unittest discover -s agent/tests -v
```

Run one LLM-only item:

```bash
python -m agent.llm_only \
  --input experiments/pilot_items.csv \
  --item DORA-15 \
  --output /tmp/dora15-llm-only
```

Run a batch with `python -m agent.batch`. `--framework DORA` limits a run to the
DORA rows, and `--resume` continues an interrupted output folder. Exact commands
and the remaining AI Act step are in `docs/EXPERIMENT_GUIDE.md`.
