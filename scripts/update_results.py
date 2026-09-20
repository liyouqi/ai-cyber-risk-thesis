"""Score saved item-level outputs against the independent gold standard."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path


METHOD_FOLDERS = {
    "manual": "manual",
    "llm_only": "llm_only",
    "agentic_rag": "agentic_rag_http",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _canonical_reference(instrument: str, provision: str = "") -> str:
    text = f"{instrument} {provision}".strip()
    if "::" in text:
        instrument, provision = text.split("::", 1)
        text = f"{instrument} {provision}"
    match = re.search(r"(20\d{2})\s*[-/]\s*0*(\d+)", instrument)
    if match:
        document = f"eu{match.group(1)}{int(match.group(2))}"
    elif "dora" in instrument.casefold():
        document = "eu20222554"
    elif "ai act" in instrument.casefold():
        document = "eu20241689"
    else:
        document = re.sub(r"[^a-z0-9]", "", instrument.casefold())
    locator = re.sub(r"\b(article|art)\.?\b", "article", provision.casefold())
    locator = re.sub(r"[^a-z0-9]", "", locator)
    return f"{document}::{locator}"


def _gold_references(value: str) -> set[str]:
    return {
        _canonical_reference(*part.strip().split("::", 1))
        for part in value.split(";")
        if part.strip()
    }


def _predicted_references(value: str) -> set[str]:
    if not value.strip():
        return set()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return _gold_references(value)
    if not isinstance(parsed, list):
        raise ValueError("missing_mapping must be a JSON list or semicolon-separated refs")
    output: set[str] = set()
    for entry in parsed:
        if isinstance(entry, str):
            output.update(_gold_references(entry))
        elif isinstance(entry, dict):
            output.add(
                _canonical_reference(
                    str(entry.get("instrument", "")), str(entry.get("provision", ""))
                )
            )
        else:
            raise ValueError("Invalid missing_mapping entry")
    return output


def update_results(results_path: Path, outputs_dir: Path, gold_path: Path) -> int:
    rows = _read_csv(results_path)
    by_key = {(row["item_id"], row["method"]): row for row in rows}
    gold = {row["item_id"]: row for row in _read_csv(gold_path)}
    updated = 0

    for method, folder_name in METHOD_FOLDERS.items():
        output = outputs_dir / folder_name
        summary_path = output / "item_summary.csv"
        if not summary_path.exists():
            continue
        summaries = {row["item_id"]: row for row in _read_csv(summary_path)}
        for item_id, summary in summaries.items():
            row = by_key[(item_id, method)]
            reference = gold[item_id]
            prediction = summary["coverage"].strip()
            if prediction not in {"Yes", "No"}:
                continue
            expected_refs = _gold_references(reference["missing_provisions"])
            proposed_refs = _predicted_references(summary.get("missing_mapping", ""))
            row["gold_coverage"] = reference["coverage"]
            row["predicted_coverage"] = prediction
            row["coverage_correct"] = str(int(prediction == reference["coverage"]))
            row["missing_mapping_true_positive"] = str(
                len(expected_refs & proposed_refs)
            )
            row["missing_mapping_proposed"] = str(len(proposed_refs))
            row["missing_mapping_reference_total"] = str(len(expected_refs))

            if method == "manual":
                raw_time = summary.get("time_min", "").strip()
                try:
                    execution = float(raw_time)
                except ValueError as exc:
                    raise ValueError(
                        f"{item_id}: Manual time_min must be a number"
                    ) from exc
                if not math.isfinite(execution) or execution <= 0:
                    raise ValueError(
                        f"{item_id}: Manual time_min must be greater than zero"
                    )
                row["execution_time_min"] = f"{execution:.3f}"
            else:
                run_path = output / "records" / item_id / "run.json"
                if run_path.exists():
                    run = json.loads(run_path.read_text(encoding="utf-8"))
                    execution = run["elapsed_seconds"] / 60
                    row["execution_time_min"] = f"{execution:.3f}"
            updated += 1

    with results_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Score saved experiment outputs")
    parser.add_argument(
        "--results", type=Path, default=Path("experiments/results/item_results.csv")
    )
    parser.add_argument("--outputs", type=Path, default=Path("experiments/outputs"))
    parser.add_argument(
        "--gold", type=Path, default=Path("experiments/data/gold_standard.csv")
    )
    args = parser.parse_args()
    print(f"Scored {update_results(args.results, args.outputs, args.gold)} rows")


if __name__ == "__main__":
    main()
