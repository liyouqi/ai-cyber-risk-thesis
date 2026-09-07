# Review Agent

The Agent checks an existing control-to-regulation mapping. It splits compound
references, retrieves relevant legal text, checks each cited provision, searches
for a small number of material omissions and writes a short summary.

LLM-only uses the same configured model and output format without retrieval.
Replay evidence exists only for automated software tests.

The Regulatory RAG is an independent, read-only HTTP service. The Agent never
imports its Python package and never reads its corpus, release or index files.
At startup, `HttpRegulatoryRagAdapter` checks `/health` and `/api/v1/status`.
Existing-provision validation sends a canonical citation such as
`AI Act Article 9` through Direct retrieval, which allows Regulatory RAG's own
citation parser to resolve the official provision. The limited gap search uses
Planned retrieval. Every run records the service status, retrieval metadata,
evidence rank and score, and the Planned retrieval plan and claim coverage.

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
  --input experiments/data/pilot_items.csv \
  --item DORA-15 \
  --output /tmp/dora15-llm-only
```

Run a batch with `python -m agent.batch`. `--framework DORA` limits a run to the
DORA rows, and `--resume` continues an interrupted output folder. Configure the
HTTP service in `.env`:

```text
REGULATORY_RAG_API_URL=http://127.0.0.1:8080
REGULATORY_RAG_API_KEY=optional-bearer-key
REGULATORY_RAG_MODE=bm25
REGULATORY_RAG_TOP_K=5
```

The API key is optional only when the service deployment does not require
authentication. Exact commands are in `docs/EXPERIMENT_GUIDE.md`.
