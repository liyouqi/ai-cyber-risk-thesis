"""Build the pilot and main datasets from the two candidate files."""

from __future__ import annotations

import csv
from pathlib import Path


DATASET_DIR = Path("experiments/datasets")
CANDIDATES = (
    DATASET_DIR / "candidates" / "ai_act.csv",
    DATASET_DIR / "candidates" / "dora.csv",
)

AI_ACT_IDS = [
    *(f"TC{i:02d}" for i in range(5, 18)),
    *(f"TC{i:02d}" for i in range(19, 26)),
]
DORA_IDS = [
    *(f"DORA-{i:02d}" for i in range(1, 9)),
    "DORA-10",
    *(f"DORA-{i:02d}" for i in range(12, 23)),
]
MAIN_IDS = AI_ACT_IDS + DORA_IDS
PILOT_IDS = ["TC05", "TC20", "DORA-15", "DORA-18"]


def read_candidates() -> tuple[list[str], dict[str, dict[str, str]]]:
    fieldnames: list[str] = []
    items: dict[str, dict[str, str]] = {}
    for path in CANDIDATES:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not fieldnames:
                fieldnames = list(reader.fieldnames or [])
            elif list(reader.fieldnames or []) != fieldnames:
                raise ValueError(f"Candidate schema differs: {path}")
            for row in reader:
                item_id = row["item_id"]
                if item_id in items:
                    raise ValueError(f"Duplicate item ID: {item_id}")
                items[item_id] = row
    return fieldnames, items


def write_dataset(
    path: Path,
    item_ids: list[str],
    fieldnames: list[str],
    items: dict[str, dict[str, str]],
) -> None:
    missing = [item_id for item_id in item_ids if item_id not in items]
    if missing:
        raise ValueError(f"Missing candidate items: {', '.join(missing)}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(items[item_id] for item_id in item_ids)


def main() -> None:
    fieldnames, items = read_candidates()
    write_dataset(DATASET_DIR / "items.csv", MAIN_IDS, fieldnames, items)
    write_dataset(DATASET_DIR / "pilot_items.csv", PILOT_IDS, fieldnames, items)
    print("Wrote 40 main items and 4 pilot items")


if __name__ == "__main__":
    main()
