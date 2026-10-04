"""Build Figure 5.2 from the current item-level experiment results."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_thesis_outputs import (
    METHODS,
    METHOD_LABELS,
    aggregate,
    plt,
    read_results,
)
from scripts.thesis_figure_style import FIGURE_STYLE, WORKFLOW_STYLES, save_publication_figure


STEM = "fig_5_2_coverage_and_missing_detection"
TITLE = "Coverage decision and missing-provision detection performance"
PANELS = (
    (
        "(a) Coverage Decision",
        (("Accuracy", "coverage_accuracy"), ("CCA", "coverage_cca")),
    ),
    (
        "(b) Missing-Provision Detection",
        (
            ("Precision", "missing_precision"),
            ("Recall", "missing_recall"),
            ("F1", "missing_f1"),
        ),
    ),
)


def performance_scores(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    """Use observed class marginals for CCA and pooled provision counts for P/R/F1."""
    scores = {}
    labels = ("Yes", "No")
    for method in METHODS:
        subset = [row for row in rows if row["method"] == method]
        if not subset:
            raise ValueError(f"No results for {METHOD_LABELS[method]}")
        for row in subset:
            gold = row.get("gold_coverage")
            predicted = row.get("predicted_coverage")
            if gold not in labels or predicted not in labels:
                raise ValueError(f"{row['item_id']} {method}: coverage labels must be Yes/No")
            if float(row["coverage_correct"]) != float(gold == predicted):
                raise ValueError(f"{row['item_id']} {method}: coverage_correct disagrees with labels")

        count = len(subset)
        accuracy = sum(
            row["gold_coverage"] == row["predicted_coverage"] for row in subset
        ) / count
        chance_agreement = sum(
            sum(row["gold_coverage"] == label for row in subset)
            * sum(row["predicted_coverage"] == label for row in subset)
            for label in labels
        ) / count**2
        if math.isclose(chance_agreement, 1.0):
            raise ValueError(f"CCA is undefined for {METHOD_LABELS[method]}")
        cca = (accuracy - chance_agreement) / (1 - chance_agreement)
        pooled = aggregate(subset)
        metrics = {"coverage_accuracy": accuracy, "coverage_cca": cca}
        for field in ("missing_precision", "missing_recall", "missing_f1"):
            value = pooled[field]
            if value is None:
                raise ValueError(f"{field} is undefined for {METHOD_LABELS[method]}")
            metrics[field] = float(value)
        scores[method] = {field: value * 100 for field, value in metrics.items()}
    return scores


def build_figure(rows: list[dict[str, str]], output: Path) -> list[Path]:
    scores = performance_scores(rows)
    output.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(FIGURE_STYLE):
        fig, axes = plt.subplots(
            1, 2, figsize=(10.8, 4.0), gridspec_kw={"width_ratios": [1, 1.2]}
        )
        fig.subplots_adjust(left=0.065, right=0.99, bottom=0.22, top=0.91, wspace=0.24)
        legend_handles = []
        for panel_index, (ax, (title, metrics)) in enumerate(zip(axes, PANELS)):
            for method_index, method in enumerate(METHODS):
                label, color = WORKFLOW_STYLES[method]
                positions = [index + (method_index - 1) * 0.24 for index in range(len(metrics))]
                heights = [scores[method][field] for _, field in metrics]
                bars = ax.bar(positions, heights, width=0.22, color=color, label=label)
                if panel_index == 0:
                    legend_handles.append(bars)
                for position, value in zip(positions, heights):
                    ax.annotate(
                        f"{value:.1f}".replace("-", "\N{MINUS SIGN}"),
                        (position, value), xytext=(0, 4 if value >= 0 else -4),
                        textcoords="offset points", ha="center",
                        va="bottom" if value >= 0 else "top", fontsize=9.5,
                        fontweight="bold" if value < 0 else "normal",
                    )
            ax.set_title(title, loc="left", fontsize=11, fontweight="bold", pad=10)
            ax.set_xticks(range(len(metrics)), [label for label, _ in metrics])
            ax.set_xlim(-0.6, len(metrics) - 0.4)
            ax.set_ylim(-30 if panel_index == 0 else 0, 105)
            ax.set_yticks(range(-20 if panel_index == 0 else 0, 101, 20))
            ax.set_ylabel("Metric value (%)")
            if panel_index == 0:
                ax.axhline(0, color="black", linewidth=0.6)
        fig.legend(
            legend_handles, [WORKFLOW_STYLES[method][0] for method in METHODS],
            loc="center", bbox_to_anchor=(0.53, 0.055), ncol=3,
            frameon=False, handlelength=1.8, columnspacing=2.5,
        )
        paths = save_publication_figure(fig, output / f"{STEM}.svg", TITLE)
        plt.close(fig)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results", type=Path, default=ROOT / "experiments/results/item_results.csv"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "thesis_outputs/generated/figures"
    )
    args = parser.parse_args()
    try:
        rows = read_results(args.results)
        paths = build_figure(rows, args.output)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
