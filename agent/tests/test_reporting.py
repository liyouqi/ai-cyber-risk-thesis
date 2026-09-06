from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

cache = Path(tempfile.gettempdir()) / "thesis-plot-cache"
cache.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(cache))

from scripts.build_thesis_outputs import figures, read_results, result_tables, skeleton_tables


ROOT = Path(__file__).resolve().parents[2]


class ThesisReportingTest(unittest.TestCase):
    def test_tables_and_figures_are_generated_from_results(self) -> None:
        rows = read_results(ROOT / "agent/tests/fixtures/report_results.csv")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            tables = output / "tables"
            charts = output / "figures"
            tables.mkdir()
            charts.mkdir()
            result_tables(rows, tables, ROOT / "experiments/data/items.csv")
            figures(rows, charts)
            self.assertEqual(len(list(tables.glob("*.csv"))), 3)
            self.assertEqual(len(list(charts.glob("*.svg"))), 6)

    def test_table_skeletons_do_not_require_scores(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tables = Path(directory)
            skeleton_tables(tables, ROOT / "experiments/data/items.csv")
            self.assertEqual(len(list(tables.glob("*.csv"))), 3)
            overall = (tables / "table_overall_results.csv").read_text(encoding="utf-8")
            self.assertIn("Agentic RAG,40", overall)


if __name__ == "__main__":
    unittest.main()
