"""Command line entry point for the first review-agent version."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import dotenv_values

from agent.evidence import (
    HttpRegulatoryRagAdapter,
    ReplayEvidenceProvider,
)
from agent.llm import LlmConfig, OpenAiCompatibleLlm
from agent.workflow import load_item, run_review, write_run


ROOT = Path(__file__).resolve().parents[1]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review one regulatory mapping")
    parser.add_argument("--input", default=str(ROOT / "experiments/data/pilot_items.csv"))
    parser.add_argument("--item", required=True, help="Assessment item ID")
    parser.add_argument("--output", required=True, help="New folder for run files")
    parser.add_argument("--env-file", default=str(ROOT / ".env"))
    parser.add_argument("--evidence", choices=("replay", "http"), default="replay")
    parser.add_argument("--evidence-file", help="Replay evidence JSON")
    parser.add_argument("--rag-api-url", help="Regulatory RAG HTTP service base URL")
    parser.add_argument(
        "--rag-mode",
        choices=("bm25", "vector", "hybrid"),
        help="Underlying retrieval mode used by both Direct and Planned queries",
    )
    parser.add_argument("--rag-top-k", type=int)
    return parser


def main() -> None:
    args = _parser().parse_args()
    env = dotenv_values(args.env_file)
    item = load_item(args.input, args.item)

    if args.evidence == "replay":
        if not args.evidence_file:
            raise SystemExit("--evidence-file is required with replay evidence")
        provider = ReplayEvidenceProvider(args.evidence_file)
    else:
        api_url = args.rag_api_url or env.get("REGULATORY_RAG_API_URL")
        if not api_url:
            raise SystemExit("Set --rag-api-url or REGULATORY_RAG_API_URL")
        rag_mode = args.rag_mode or str(env.get("REGULATORY_RAG_MODE") or "bm25")
        rag_top_k = args.rag_top_k or int(env.get("REGULATORY_RAG_TOP_K") or 5)
        provider = HttpRegulatoryRagAdapter(
            str(api_url),
            api_key=env.get("REGULATORY_RAG_API_KEY") or None,
            retrieval_mode=rag_mode,
            top_k=rag_top_k,
        )

    config = LlmConfig.from_env_file(args.env_file)
    llm = OpenAiCompatibleLlm(config)
    system_prompt = (ROOT / "agent/prompts/review_system.md").read_text(encoding="utf-8")
    run = run_review(
        item,
        provider,
        llm,
        system_prompt,
    )
    path = write_run(run, args.output)
    print(f"Review written to {path}")


if __name__ == "__main__":
    main()
