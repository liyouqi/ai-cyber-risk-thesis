"""Prepare the item-level scoring sheet before experiment results exist."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.references import parse_mapping
from agent.workflow import load_items


METHODS = ("manual", "llm_only", "agentic_rag")
FIELDS = [
    "item_id",
    "framework",
    "method",
    "existing_mapping_correct",
    "existing_mapping_total",
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
    if output.exists():
        with output.open(newline="", encoding="utf-8-sig") as handle:
            if any(csv.DictReader(handle)):
                raise FileExistsError(f"Result table already contains rows: {output}")

    rows: list[dict[str, object]] = []
    for item in load_items(input_path):
        mapping_total = len(parse_mapping(item.existing_mapping, item.instrument))
        for method in METHODS:
            row: dict[str, object] = {field: "" for field in FIELDS}
            row.update(
                {
                    "item_id": item.item_id,
                    "framework": item.framework,
                    "method": method,
                    "existing_mapping_total": mapping_total,
                }
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
    parser.add_argument(
        "--input",
        default=str(ROOT / "experiments/datasets/items.csv"),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "experiments/results/item_results.csv"),
    )
    args = parser.parse_args()
    output = prepare_result_table(args.input, args.output)
    print(f"Scoring table written to {output}")


if __name__ == "__main__":
    main()
