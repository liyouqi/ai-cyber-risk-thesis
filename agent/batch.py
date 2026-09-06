"""Run one AI method over every row in a dataset."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from dotenv import dotenv_values

from agent.evidence import RegulatoryRagProvider
from agent.llm import LlmConfig, OpenAiCompatibleLlm
from agent.workflow import load_items, run_llm_only, run_review, write_run


ROOT = Path(__file__).resolve().parents[1]


def combine_review_tables(output: Path, item_ids: list[str]) -> None:
    """Create two spreadsheet-friendly batch files from the per-item records."""
    records = output / "records"
    for filename in ("provision_checks.csv", "item_summary.csv"):
        rows: list[dict[str, str]] = []
        fields: list[str] | None = None
        for item_id in item_ids:
            with (records / item_id / filename).open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                if fields is None:
                    fields = list(reader.fieldnames or [])
                rows.extend(reader)
        if not fields:
            raise ValueError(f"No rows found for {filename}")
        with (output / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one AI method over a CSV dataset")
    parser.add_argument("--method", choices=("llm-only", "agentic-rag"), required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--framework", help="Run only rows with this framework name")
    parser.add_argument(
        "--output",
        required=True,
        help="New folder containing one folder per item",
    )
    parser.add_argument("--env-file", default=str(ROOT / ".env"))
    parser.add_argument("--rag-root", help="Path to the regulatory-rag project")
    parser.add_argument("--rag-profile", help="Optional RAG corpus profile")
    parser.add_argument("--rag-mode", choices=("bm25", "vector", "hybrid"))
    parser.add_argument("--rag-top-k", type=int)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Continue an interrupted batch and skip complete item folders",
    )
    args = parser.parse_args()

    all_items = load_items(args.input)
    items = all_items
    if args.framework:
        items = [item for item in items if item.framework == args.framework]
        if not items:
            raise SystemExit(f"No items found for framework: {args.framework}")
    llm = OpenAiCompatibleLlm(LlmConfig.from_env_file(args.env_file))

    provider = None
    if args.method == "agentic-rag":
        env = dotenv_values(args.env_file)
        rag_root = args.rag_root or env.get("REGULATORY_RAG_ROOT")
        if not rag_root:
            raise SystemExit("Set --rag-root or REGULATORY_RAG_ROOT")
        rag_profile = args.rag_profile or env.get("REGULATORY_RAG_PROFILE") or None
        provider = RegulatoryRagProvider(
            rag_root,
            profile=rag_profile,
            mode=args.rag_mode or str(env.get("REGULATORY_RAG_MODE") or "hybrid"),
            top_k=args.rag_top_k or int(env.get("REGULATORY_RAG_TOP_K") or 8),
        )

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=args.resume)
    records = output / "records"
    records.mkdir(exist_ok=args.resume)

    def should_skip(item_id: str) -> bool:
        folder = records / item_id
        if not folder.exists():
            return False
        required = {
            "run.json",
            "raw_response.json",
            "provision_checks.csv",
            "item_summary.csv",
        }
        if args.resume and required.issubset(path.name for path in folder.iterdir()):
            print(f"Skipping complete item {item_id}")
            return True
        raise FileExistsError(f"Output already exists or is incomplete: {folder}")

    if args.method == "llm-only":
        prompt = (ROOT / "agent/prompts/llm_only_system.md").read_text(encoding="utf-8")
        for item in items:
            if should_skip(item.item_id):
                continue
            run = run_llm_only(item, llm, prompt)
            write_run(run, records / item.item_id)
    else:
        assert provider is not None
        prompt = (ROOT / "agent/prompts/review_system.md").read_text(encoding="utf-8")
        for item in items:
            if should_skip(item.item_id):
                continue
            run = run_review(item, provider, llm, prompt)
            write_run(run, records / item.item_id)

    available = [item.item_id for item in all_items if (records / item.item_id).is_dir()]
    combine_review_tables(output, available)
    print(f"Completed {len(items)} items in {output}")


if __name__ == "__main__":
    main()
