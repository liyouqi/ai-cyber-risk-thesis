"""Run one AI method over every row in a dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import dotenv_values

from agent.evidence import RegulatoryRagProvider, validate_experiment_profile
from agent.llm import LlmConfig, OpenAiCompatibleLlm
from agent.workflow import load_items, run_llm_only, run_review, write_run


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one AI method over a CSV dataset")
    parser.add_argument("--method", choices=("llm-only", "agentic-rag"), required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument(
        "--output",
        required=True,
        help="New folder containing one folder per item",
    )
    parser.add_argument("--env-file", default=str(ROOT / ".env"))
    parser.add_argument(
        "--experiment-run",
        action="store_true",
        help="Mark outputs as part of a frozen experiment",
    )
    args = parser.parse_args()

    items = load_items(args.input)
    llm = OpenAiCompatibleLlm(LlmConfig.from_env_file(args.env_file))

    provider = None
    if args.method == "agentic-rag":
        env = dotenv_values(args.env_file)
        rag_root = env.get("REGULATORY_RAG_ROOT")
        if not rag_root:
            raise SystemExit("REGULATORY_RAG_ROOT is missing from the environment file")
        rag_profile = env.get("REGULATORY_RAG_PROFILE") or None
        if args.experiment_run:
            validate_experiment_profile(rag_profile, items)
        provider = RegulatoryRagProvider(
            rag_root,
            profile=rag_profile,
            mode=str(env.get("REGULATORY_RAG_MODE") or "hybrid"),
            top_k=int(env.get("REGULATORY_RAG_TOP_K") or 8),
        )

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)

    if args.method == "llm-only":
        prompt = (ROOT / "agent/prompts/llm_only_system.md").read_text(encoding="utf-8")
        for item in items:
            run = run_llm_only(
                item,
                llm,
                prompt,
                eligible_for_experiment=args.experiment_run,
            )
            write_run(run, output / item.item_id)
    else:
        assert provider is not None
        prompt = (ROOT / "agent/prompts/review_system.md").read_text(encoding="utf-8")
        for item in items:
            run = run_review(
                item,
                provider,
                llm,
                prompt,
                eligible_for_experiment=args.experiment_run,
            )
            write_run(run, output / item.item_id)

    print(f"Completed {len(items)} items in {output}")
    if not args.experiment_run:
        print("Development output: not eligible for experiment results")


if __name__ == "__main__":
    main()
