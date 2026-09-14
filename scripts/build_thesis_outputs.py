"""Build the small set of tables and draft figures used in the thesis."""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable

PLOT_CACHE = Path(tempfile.gettempdir()) / "thesis-plot-cache"
PLOT_CACHE.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(PLOT_CACHE / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(PLOT_CACHE))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.references import parse_mapping


METHODS = ("manual", "llm_only", "agentic_rag")
AI_METHODS = ("llm_only", "agentic_rag")
METHOD_LABELS = {
    "manual": "Manual",
    "llm_only": "LLM-only",
    "agentic_rag": "Agentic RAG",
}
FRAMEWORKS = ("EU AI Act", "DORA")
COLORS = {"EU AI Act": "#4878A8", "DORA": "#E08B3E"}
NUMERIC_FIELDS = {
    "coverage_correct",
    "missing_mapping_true_positive",
    "missing_mapping_proposed",
    "missing_mapping_reference_total",
    "evidence_errors",
    "unsupported_claims",
    "execution_time_min",
    "human_review_time_min",
    "total_time_min",
}


def number(row: dict[str, str], field: str) -> float | None:
    value = row.get(field, "").strip()
    if not value:
        return None
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError(f"{row.get('item_id')}: invalid {field}: {value}")
    return parsed


def read_results(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = (NUMERIC_FIELDS | {"item_id", "framework", "method"}) - fields
        if missing:
            raise ValueError("Missing result columns: " + ", ".join(sorted(missing)))
        rows = list(reader)
    if not rows:
        raise ValueError("item_results.csv has no experiment rows yet")
    for row in rows:
        if row["method"] not in METHODS:
            raise ValueError(f"Unknown method: {row['method']}")
        if row["framework"] not in FRAMEWORKS:
            raise ValueError(f"Unknown framework: {row['framework']}")
        for field in NUMERIC_FIELDS:
            number(row, field)
        required = [
            "coverage_correct",
            "missing_mapping_true_positive",
            "missing_mapping_proposed",
            "missing_mapping_reference_total",
        ]
        if row["method"] in AI_METHODS:
            required.extend(
                [
                    "evidence_errors",
                    "unsupported_claims",
                    "execution_time_min",
                ]
            )
        absent = [field for field in required if number(row, field) is None]
        if absent:
            raise ValueError(
                f"{row['item_id']} {row['method']} has blank required values: "
                + ", ".join(absent)
            )
        if row["method"] in AI_METHODS:
            true_positive = number(row, "missing_mapping_true_positive") or 0
            proposed = number(row, "missing_mapping_proposed") or 0
            reference = number(row, "missing_mapping_reference_total") or 0
            if true_positive > proposed or true_positive > reference:
                raise ValueError(f"{row['item_id']}: missing-mapping counts are inconsistent")

    grouped: dict[str, set[str]] = defaultdict(set)
    seen: set[tuple[str, str]] = set()
    frameworks: dict[str, str] = {}
    for row in rows:
        key = (row["item_id"], row["method"])
        if key in seen:
            raise ValueError(f"Duplicate result row: {row['item_id']} {row['method']}")
        seen.add(key)
        prior_framework = frameworks.setdefault(row["item_id"], row["framework"])
        if prior_framework != row["framework"]:
            raise ValueError(f"Framework differs across methods for {row['item_id']}")
        grouped[row["item_id"]].add(row["method"])
    incomplete = [item_id for item_id, methods in grouped.items() if methods != set(METHODS)]
    if incomplete:
        raise ValueError("Items without all three methods: " + ", ".join(incomplete))
    return rows


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def aggregate(rows: Iterable[dict[str, str]]) -> dict[str, float | int | None]:
    rows = list(rows)
    execution_times_sec = [
        value * 60
        for row in rows
        if (value := number(row, "execution_time_min")) is not None
    ]
    correct = sum(number(row, "coverage_correct") or 0 for row in rows)
    gold_yes = sum(row.get("gold_coverage") == "Yes" for row in rows)
    gold_no = sum(row.get("gold_coverage") == "No" for row in rows)
    correct_yes = sum(
        row.get("gold_coverage") == "Yes" and row.get("predicted_coverage") == "Yes"
        for row in rows
    )
    correct_no = sum(
        row.get("gold_coverage") == "No" and row.get("predicted_coverage") == "No"
        for row in rows
    )
    yes_recall = ratio(correct_yes, gold_yes)
    no_recall = ratio(correct_no, gold_no)
    missing_tp = sum(number(row, "missing_mapping_true_positive") or 0 for row in rows)
    missing_proposed = sum(number(row, "missing_mapping_proposed") or 0 for row in rows)
    missing_reference = sum(number(row, "missing_mapping_reference_total") or 0 for row in rows)
    precision = ratio(missing_tp, missing_proposed)
    recall = ratio(missing_tp, missing_reference)
    if precision is not None and recall is not None:
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    else:
        f1 = None
    return {
        "items": len({row["item_id"] for row in rows}),
        "mean_execution_time_sec": (
            statistics.mean(execution_times_sec) if execution_times_sec else None
        ),
        "median_execution_time_sec": (
            statistics.median(execution_times_sec) if execution_times_sec else None
        ),
        "coverage_accuracy": ratio(correct, len(rows)),
        "yes_recall": yes_recall,
        "no_recall": no_recall,
        "balanced_accuracy": (
            (yes_recall + no_recall) / 2
            if yes_recall is not None and no_recall is not None
            else None
        ),
        "missing_precision": precision,
        "missing_recall": recall,
        "missing_f1": f1,
        "evidence_errors_per_item": ratio(
            sum(number(row, "evidence_errors") or 0 for row in rows), len(rows)
        ),
        "unsupported_claims_per_item": ratio(
            sum(number(row, "unsupported_claims") or 0 for row in rows), len(rows)
        ),
    }


def text(value: float | int | None) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return f"{value:.3f}"


def write_table(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows available for {path.name}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: text(value) if isinstance(value, (int, float)) else value
                    for key, value in row.items()
                }
            )


def dataset_table(
    dataset_path: Path,
    result_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    included = {row["item_id"] for row in result_rows}
    by_framework: dict[str, list[dict[str, str]]] = defaultdict(list)
    with dataset_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["item_id"] in included:
                by_framework[row["framework"]].append(row)
    return [
        {
            "framework": framework,
            "items": len(items),
            "existing_provisions": sum(
                len(parse_mapping(item["existing_mapping"], item["instrument"]))
                for item in items
            ),
        }
        for framework, items in by_framework.items()
    ]


def result_tables(rows: list[dict[str, str]], table_dir: Path, dataset: Path) -> None:
    status = (
        "PREVIEW ONLY — NOT EXPERIMENT RESULTS"
        if any("PIPELINE_PREVIEW" in row.get("short_note", "") for row in rows)
        else "FINAL"
    )
    write_table(table_dir / "table_dataset_summary.csv", dataset_table(dataset, rows))

    overall = []
    for method in METHODS:
        values = aggregate(row for row in rows if row["method"] == method)
        if method == "manual":
            for field in (
                "evidence_errors_per_item",
                "unsupported_claims_per_item",
            ):
                values[field] = None
        overall.append({"result_status": status, "method": METHOD_LABELS[method], **values})
    write_table(table_dir / "table_overall_results.csv", overall)

    frameworks = []
    for framework in FRAMEWORKS:
        for method in METHODS:
            subset = [
                row for row in rows if row["framework"] == framework and row["method"] == method
            ]
            if not subset:
                continue
            values = aggregate(subset)
            if method == "manual":
                for field in (
                    "evidence_errors_per_item",
                    "unsupported_claims_per_item",
                ):
                    values[field] = None
            frameworks.append(
                {
                    "result_status": status,
                    "framework": framework,
                    "method": METHOD_LABELS[method],
                    **values,
                }
            )
    write_table(table_dir / "table_framework_results.csv", frameworks)


def skeleton_tables(table_dir: Path, dataset: Path) -> None:
    """Write table layouts before scores and timing data are available."""
    with dataset.open(newline="", encoding="utf-8-sig") as handle:
        dataset_rows = list(csv.DictReader(handle))
    if not dataset_rows:
        raise ValueError(f"No items found in {dataset}")

    result_stub = [{"item_id": row["item_id"]} for row in dataset_rows]
    write_table(
        table_dir / "table_dataset_summary.csv",
        dataset_table(dataset, result_stub),
    )
    metric_fields = {
        "mean_execution_time_sec": None,
        "median_execution_time_sec": None,
        "coverage_accuracy": None,
        "yes_recall": None,
        "no_recall": None,
        "balanced_accuracy": None,
        "missing_precision": None,
        "missing_recall": None,
        "missing_f1": None,
        "evidence_errors_per_item": None,
        "unsupported_claims_per_item": None,
    }
    write_table(
        table_dir / "table_overall_results.csv",
        [
            {
                "method": METHOD_LABELS[method],
                "items": len(dataset_rows),
                **metric_fields,
            }
            for method in METHODS
        ],
    )
    write_table(
        table_dir / "table_framework_results.csv",
        [
            {
                "framework": framework,
                "method": METHOD_LABELS[method],
                "items": sum(row["framework"] == framework for row in dataset_rows),
                **metric_fields,
            }
            for framework in FRAMEWORKS
            for method in METHODS
        ],
    )


def save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)


def values(rows: list[dict[str, str]], method: str, field: str) -> list[float]:
    return [
        value
        for row in rows
        if row["method"] == method and (value := number(row, field)) is not None
    ]


def figures(rows: list[dict[str, str]], figure_dir: Path) -> None:
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    preview = any("PIPELINE_PREVIEW" in row.get("short_note", "") for row in rows)
    title_prefix = "PREVIEW ONLY — " if preview else ""

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    time_data = [
        [value * 60 for value in values(rows, method, "execution_time_min")]
        for method in AI_METHODS
    ]
    ax.boxplot(
        time_data,
        tick_labels=[METHOD_LABELS[m] for m in AI_METHODS],
        showmeans=True,
    )
    ax.set_ylabel("Execution time (seconds)")
    ax.set_title("Measured system execution time")
    save(fig, figure_dir / "fig_5_1_execution_time.svg")

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    labels, scores, colors = [], [], []
    for method in METHODS:
        for framework in FRAMEWORKS:
            subset = [
                row for row in rows if row["method"] == method and row["framework"] == framework
            ]
            score = aggregate(subset)["coverage_accuracy"] if subset else None
            labels.append(f"{METHOD_LABELS[method]}\n{framework}")
            scores.append(score or 0)
            colors.append(COLORS[framework])
    ax.bar(labels, scores, color=colors)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Coverage accuracy")
    ax.set_title(title_prefix + "Item-level coverage accuracy by method and framework")
    save(fig, figure_dir / "fig_5_2_mapping_accuracy.svg")

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    metric_names = ("missing_precision", "missing_recall", "missing_f1")
    x = range(len(METHODS))
    width = 0.24
    for index, metric in enumerate(metric_names):
        scores = [
            aggregate(row for row in rows if row["method"] == method)[metric] or 0
            for method in METHODS
        ]
        ax.bar(
            [position + (index - 1) * width for position in x],
            scores,
            width,
            label=metric.removeprefix("missing_").title(),
        )
    ax.set_xticks(list(x), [METHOD_LABELS[method] for method in METHODS])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title(title_prefix + "Material missing-mapping detection")
    ax.legend(frameon=False)
    if not any(
        aggregate(row for row in rows if row["method"] == method)["missing_f1"]
        for method in METHODS
    ):
        ax.text(
            0.5,
            0.5,
            "No exact matches to reference omissions",
            transform=ax.transAxes,
            ha="center",
            va="center",
            color="#555555",
        )
    save(fig, figure_dir / "fig_5_3_missing_detection.svg")

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6))
    for ax, field, title in (
        (axes[0], "evidence_errors", "Evidence errors per item"),
        (axes[1], "unsupported_claims", "Unsupported claims per item"),
    ):
        means = [statistics.mean(values(rows, method, field)) for method in AI_METHODS]
        ax.bar([METHOD_LABELS[m] for m in AI_METHODS], means, color=("#8E6C8A", "#5B8C85"))
        ax.set_title(title_prefix + title)
        ax.set_ylabel("Mean count")
        if not any(means):
            ax.set_ylim(0, 1)
            ax.text(
                0.5,
                0.5,
                "No scored errors",
                transform=ax.transAxes,
                ha="center",
                va="center",
                color="#555555",
            )
    save(fig, figure_dir / "fig_5_4_reliability_errors.svg")



def main() -> None:
    parser = argparse.ArgumentParser(description="Build thesis tables and draft figures")
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("experiments/results/item_results.csv"),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("experiments/data/items.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("thesis_outputs/generated"),
    )
    parser.add_argument(
        "--skeleton",
        action="store_true",
        help="Write the three table layouts without requiring completed results",
    )
    args = parser.parse_args()

    if args.skeleton:
        args.output.mkdir(parents=True, exist_ok=True)
        table_dir = args.output / "tables"
        table_dir.mkdir(exist_ok=True)
        skeleton_tables(table_dir, args.dataset)
        print(f"Wrote thesis table skeletons to {args.output}")
        return

    try:
        rows = read_results(args.results)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.output.mkdir(parents=True, exist_ok=True)
    table_dir = args.output / "tables"
    figure_dir = args.output / "figures"
    table_dir.mkdir(exist_ok=True)
    figure_dir.mkdir(exist_ok=True)
    result_tables(rows, table_dir, args.dataset)
    figures(rows, figure_dir)
    print(f"Wrote thesis outputs to {args.output}")


if __name__ == "__main__":
    main()
