"""Prepare the item-level scoring sheet for the three methods."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from agent.workflow import load_items


ROOT = Path(__file__).resolve().parents[1]
METHODS = ("manual", "llm_only", "agentic_rag")
FIELDS = [
    "item_id",
    "framework",
    "method",
    "gold_coverage",
    "predicted_coverage",
    "coverage_correct",
    "missing_mapping_true_positive",
    "missing_mapping_proposed",
    "missing_mapping_reference_total",
    "evidence_errors",
    "unsupported_claims",
    "execution_time_min",
    "human_review_time_min",
    "total_time_min",
    "short_note",
]


def prepare_result_table(input_path: str | Path, output_path: str | Path) -> Path:
    output = Path(output_path)
    rows: list[dict[str, str]] = []
    for item in load_items(input_path):
        for method in METHODS:
            row = {field: "" for field in FIELDS}
            row.update(
                {"item_id": item.item_id, "framework": item.framework, "method": method}
            )
            rows.append(row)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the blank scoring table")
    parser.add_argument("--input", default=str(ROOT / "experiments/data/items.csv"))
    parser.add_argument(
        "--output", default=str(ROOT / "experiments/results/item_results.csv")
    )
    args = parser.parse_args()
    print(f"Scoring table written to {prepare_result_table(args.input, args.output)}")


if __name__ == "__main__":
    main()
