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
        required = ["total_time_min"]
        if row["method"] in AI_METHODS:
            required.extend(
                [
                    "existing_mapping_correct",
                    "existing_mapping_total",
                    "missing_mapping_true_positive",
                    "missing_mapping_proposed",
                    "missing_mapping_reference_total",
                    "evidence_errors",
                    "unsupported_claims",
                    "execution_time_min",
                    "human_review_time_min",
                ]
            )
        absent = [field for field in required if number(row, field) is None]
        if absent:
            raise ValueError(
                f"{row['item_id']} {row['method']} has blank required values: "
                + ", ".join(absent)
            )
        if row["method"] in AI_METHODS:
            correct = number(row, "existing_mapping_correct") or 0
            total = number(row, "existing_mapping_total") or 0
            true_positive = number(row, "missing_mapping_true_positive") or 0
            proposed = number(row, "missing_mapping_proposed") or 0
            reference = number(row, "missing_mapping_reference_total") or 0
            if correct > total:
                raise ValueError(f"{row['item_id']}: mapping correct exceeds total")
            if true_positive > proposed or true_positive > reference:
                raise ValueError(f"{row['item_id']}: missing-mapping counts are inconsistent")
            execution = number(row, "execution_time_min") or 0
            human = number(row, "human_review_time_min") or 0
            total_time = number(row, "total_time_min") or 0
            if abs(execution + human - total_time) > 0.05:
                raise ValueError(
                    f"{row['item_id']} {row['method']}: total time does not equal "
                    "execution plus human review time"
                )

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
    total_times = [value for row in rows if (value := number(row, "total_time_min")) is not None]
    human_times = [
        value for row in rows if (value := number(row, "human_review_time_min")) is not None
    ]
    correct = sum(number(row, "existing_mapping_correct") or 0 for row in rows)
    mapped = sum(number(row, "existing_mapping_total") or 0 for row in rows)
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
        "mean_total_time_min": statistics.mean(total_times) if total_times else None,
        "median_total_time_min": statistics.median(total_times) if total_times else None,
        "mapping_accuracy": ratio(correct, mapped),
        "missing_precision": precision,
        "missing_recall": recall,
        "missing_f1": f1,
        "evidence_errors_per_item": ratio(
            sum(number(row, "evidence_errors") or 0 for row in rows), len(rows)
        ),
        "unsupported_claims_per_item": ratio(
            sum(number(row, "unsupported_claims") or 0 for row in rows), len(rows)
        ),
        "mean_human_review_time_min": statistics.mean(human_times) if human_times else None,
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
    write_table(table_dir / "table_dataset_summary.csv", dataset_table(dataset, rows))

    overall = []
    for method in METHODS:
        values = aggregate(row for row in rows if row["method"] == method)
        if method == "manual":
            for field in (
                "mapping_accuracy",
                "missing_precision",
                "missing_recall",
                "missing_f1",
                "evidence_errors_per_item",
                "unsupported_claims_per_item",
                "mean_human_review_time_min",
            ):
                values[field] = None
        overall.append({"method": METHOD_LABELS[method], **values})
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
                    "mapping_accuracy",
                    "missing_precision",
                    "missing_recall",
                    "missing_f1",
                    "evidence_errors_per_item",
                    "unsupported_claims_per_item",
                    "mean_human_review_time_min",
                ):
                    values[field] = None
            frameworks.append(
                {"framework": framework, "method": METHOD_LABELS[method], **values}
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
        "mean_total_time_min": None,
        "median_total_time_min": None,
        "mapping_accuracy": None,
        "missing_precision": None,
        "missing_recall": None,
        "missing_f1": None,
        "evidence_errors_per_item": None,
        "unsupported_claims_per_item": None,
        "mean_human_review_time_min": None,
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

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    time_data = [values(rows, method, "total_time_min") for method in METHODS]
    ax.boxplot(
        time_data,
        tick_labels=[METHOD_LABELS[m] for m in METHODS],
        showmeans=True,
    )
    ax.set_ylabel("Total review time (minutes)")
    ax.set_title("Review time by method")
    save(fig, figure_dir / "fig_5_1_review_time.svg")

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    labels, scores, colors = [], [], []
    for method in AI_METHODS:
        for framework in FRAMEWORKS:
            subset = [
                row for row in rows if row["method"] == method and row["framework"] == framework
            ]
            score = aggregate(subset)["mapping_accuracy"] if subset else None
            labels.append(f"{METHOD_LABELS[method]}\n{framework}")
            scores.append(score or 0)
            colors.append(COLORS[framework])
    ax.bar(labels, scores, color=colors)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Existing-mapping accuracy")
    ax.set_title("Mapping accuracy by AI method and framework")
    save(fig, figure_dir / "fig_5_2_mapping_accuracy.svg")

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    metric_names = ("missing_precision", "missing_recall", "missing_f1")
    x = range(len(AI_METHODS))
    width = 0.24
    for index, metric in enumerate(metric_names):
        scores = [
            aggregate(row for row in rows if row["method"] == method)[metric] or 0
            for method in AI_METHODS
        ]
        ax.bar(
            [position + (index - 1) * width for position in x],
            scores,
            width,
            label=metric.removeprefix("missing_").title(),
        )
    ax.set_xticks(list(x), [METHOD_LABELS[method] for method in AI_METHODS])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Material missing-mapping detection")
    ax.legend(frameon=False)
    save(fig, figure_dir / "fig_5_3_missing_detection.svg")

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6))
    for ax, field, title in (
        (axes[0], "evidence_errors", "Evidence errors per item"),
        (axes[1], "unsupported_claims", "Unsupported claims per item"),
    ):
        means = [statistics.mean(values(rows, method, field)) for method in AI_METHODS]
        ax.bar([METHOD_LABELS[m] for m in AI_METHODS], means, color=("#8E6C8A", "#5B8C85"))
        ax.set_title(title)
        ax.set_ylabel("Mean count")
    save(fig, figure_dir / "fig_5_4_reliability_errors.svg")

    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    correction_data = [values(rows, method, "human_review_time_min") for method in AI_METHODS]
    ax.boxplot(
        correction_data,
        tick_labels=[METHOD_LABELS[m] for m in AI_METHODS],
        showmeans=True,
    )
    ax.set_ylabel("Human correction time (minutes)")
    ax.set_title("Human correction effort")
    save(fig, figure_dir / "fig_5_5_correction_time.svg")

    by_item: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_item[row["item_id"]][row["method"]] = row
    fig, ax = plt.subplots(figsize=(5, 4.5))
    for framework in FRAMEWORKS:
        points = []
        for methods in by_item.values():
            if methods["manual"]["framework"] != framework:
                continue
            manual = number(methods["manual"], "total_time_min")
            agent = number(methods["agentic_rag"], "total_time_min")
            if manual is not None and agent is not None:
                points.append((manual, agent))
        if points:
            ax.scatter(
                [point[0] for point in points],
                [point[1] for point in points],
                label=framework,
                color=COLORS[framework],
            )
    limits = ax.get_xlim()
    upper = max(limits[1], ax.get_ylim()[1])
    ax.plot([0, upper], [0, upper], linestyle="--", color="grey", linewidth=1)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Manual total time (minutes)")
    ax.set_ylabel("Agentic RAG total time (minutes)")
    ax.set_title("Paired review time by item")
    ax.legend(frameon=False)
    save(fig, figure_dir / "fig_5_6_paired_time.svg")


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
        args.output.mkdir(parents=True, exist_ok=False)
        table_dir = args.output / "tables"
        table_dir.mkdir()
        skeleton_tables(table_dir, args.dataset)
        print(f"Wrote thesis table skeletons to {args.output}")
        return

    try:
        rows = read_results(args.results)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.output.mkdir(parents=True, exist_ok=False)
    table_dir = args.output / "tables"
    figure_dir = args.output / "figures"
    table_dir.mkdir()
    figure_dir.mkdir()
    result_tables(rows, table_dir, args.dataset)
    figures(rows, figure_dir)
    print(f"Wrote thesis outputs to {args.output}")


if __name__ == "__main__":
    main()
