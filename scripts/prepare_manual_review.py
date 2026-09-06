"""Create blank, spreadsheet-friendly forms for a manual review run."""

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


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare_manual_review(input_path: str | Path, output_dir: str | Path) -> Path:
    source = Path(input_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)

    items = load_items(source)

    mapping_rows: list[dict[str, object]] = []
    item_rows: list[dict[str, object]] = []
    timing_rows: list[dict[str, object]] = []
    for item in items:
        for reference in parse_mapping(item.existing_mapping, item.instrument):
            mapping_rows.append(
                {
                    "item_id": item.item_id,
                    "instrument": reference.instrument,
                    "provision": reference.provision,
                    "decision": "",
                    "reason": "",
                    "evidence_reference": "",
                    "evidence_excerpt": "",
                }
            )
        item_rows.append(
            {
                "item_id": item.item_id,
                "overall_assessment": "",
                "missing_mapping": "",
                "applicability_note": "",
                "challenge_comment": "",
            }
        )
        timing_rows.append(
            {
                "item_id": item.item_id,
                "start_time": "",
                "end_time": "",
                "total_time_min": "",
                "official_sources": "",
            }
        )

    _write_csv(
        output / "provision_checks.csv",
        [
            "item_id",
            "instrument",
            "provision",
            "decision",
            "reason",
            "evidence_reference",
            "evidence_excerpt",
        ],
        mapping_rows,
    )
    _write_csv(
        output / "item_summary.csv",
        [
            "item_id",
            "overall_assessment",
            "missing_mapping",
            "applicability_note",
            "challenge_comment",
        ],
        item_rows,
    )
    _write_csv(
        output / "timing.csv",
        ["item_id", "start_time", "end_time", "total_time_min", "official_sources"],
        timing_rows,
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare blank Manual review CSV files")
    parser.add_argument(
        "--input",
        default=str(ROOT / "experiments/pilot_items.csv"),
    )
    parser.add_argument("--output", required=True, help="New folder for the review forms")
    args = parser.parse_args()
    output = prepare_manual_review(args.input, args.output)
    print(f"Manual review files written to {output}")


if __name__ == "__main__":
    main()
