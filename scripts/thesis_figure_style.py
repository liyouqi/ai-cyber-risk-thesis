"""Shared workflow colors, typography and export settings for thesis figures."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure


WORKFLOW_STYLES = {
    "manual": ("Manual Review", "#3B5B7A"),
    "llm_only": ("LLM-only Review", "#C96A3D"),
    "agentic_rag": ("Agentic RAG Review", "#4F8A83"),
}
FIGURE_STYLE = {
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "svg.fonttype": "none",
    "svg.hashsalt": "thesis-figures",
    "pdf.fonttype": 42,
}


def save_publication_figure(fig: Figure, path: Path, title: str) -> list[Path]:
    """Export SVG, PDF and 300 dpi PNG with matching, tightly cropped geometry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    paths = []
    for extension in ("svg", "pdf", "png"):
        target = path.with_suffix(f".{extension}")
        if extension == "pdf":
            metadata = {"Title": title, "CreationDate": None, "ModDate": None}
        else:
            metadata = {"Title": title}
            if extension == "svg":
                metadata["Date"] = None
        fig.savefig(
            target, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.04,
            metadata=metadata,
        )
        if extension == "svg":
            target.write_text(
                "\n".join(line.rstrip() for line in target.read_text(encoding="utf-8").splitlines())
                + "\n", encoding="utf-8",
            )
        paths.append(target)
    return paths
