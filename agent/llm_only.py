"""Run the comparison method without retrieval or tools."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent.llm import LlmConfig, OpenAiCompatibleLlm
from agent.workflow import load_item, run_llm_only, write_run


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Review one mapping without RAG")
    parser.add_argument("--input", default=str(ROOT / "experiments/data/pilot_items.csv"))
    parser.add_argument("--item", required=True, help="Assessment item ID")
    parser.add_argument("--output", required=True, help="New folder for run files")
    parser.add_argument("--env-file", default=str(ROOT / ".env"))
    args = parser.parse_args()

    llm = OpenAiCompatibleLlm(LlmConfig.from_env_file(args.env_file))
    item = load_item(args.input, args.item)
    prompt = (ROOT / "agent/prompts/llm_only_system.md").read_text(encoding="utf-8")
    run = run_llm_only(item, llm, prompt)
    path = write_run(run, args.output)
    print(f"Review written to {path}")


if __name__ == "__main__":
    main()
