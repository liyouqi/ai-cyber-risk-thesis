"""Copy objective values from saved AI runs into the scoring table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


METHOD_FOLDERS = {
    "llm_only": "llm_only",
    "agentic_rag": "agentic_rag",
}


def update_results(results_path: Path, outputs_dir: Path) -> int:
    with results_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    by_key = {(row["item_id"], row["method"]): row for row in rows}

    updated = 0
    for method, folder_name in METHOD_FOLDERS.items():
        records = outputs_dir / folder_name / "records"
        if not records.exists():
            continue
        for folder in sorted(path for path in records.iterdir() if path.is_dir()):
            run = json.loads((folder / "run.json").read_text(encoding="utf-8"))
            response = json.loads((folder / "raw_response.json").read_text(encoding="utf-8"))
            key = (run["item_id"], method)
            if key not in by_key:
                raise ValueError(f"Run is not present in the scoring table: {key}")
            row = by_key[key]
            row["execution_time_min"] = f"{run['elapsed_seconds'] / 60:.3f}"
            row["missing_mapping_proposed"] = str(len(response["missing_mappings"]))
            updated += 1

    with results_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Update results from saved AI runs")
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("experiments/results/item_results.csv"),
    )
    parser.add_argument("--outputs", type=Path, default=Path("experiments/outputs"))
    args = parser.parse_args()
    count = update_results(args.results, args.outputs)
    print(f"Updated {count} AI result rows in {args.results}")


if __name__ == "__main__":
    main()
