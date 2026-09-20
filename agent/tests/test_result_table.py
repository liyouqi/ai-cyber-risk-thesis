from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_result_table import prepare_result_table
from scripts.update_results import update_results


ROOT = Path(__file__).resolve().parents[2]


class ResultTableTest(unittest.TestCase):
    def test_main_table_contains_three_blank_method_rows_per_item(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = prepare_result_table(
                ROOT / "experiments/data/items.csv", Path(directory) / "item_results.csv"
            )
            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 120)
            self.assertEqual(
                {row["method"] for row in rows if row["item_id"] == "DORA-18"},
                {"manual", "llm_only", "agentic_rag"},
            )
            self.assertTrue(all(not row["coverage_correct"] for row in rows))

    def test_saved_output_is_scored_against_gold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results = prepare_result_table(
                ROOT / "experiments/data/items.csv", root / "results.csv"
            )
            output = root / "outputs/llm_only"
            record = output / "records/DORA-15"
            record.mkdir(parents=True)
            (output / "item_summary.csv").write_text(
                "item_id,coverage,missing_mapping\nDORA-15,Yes,\n", encoding="utf-8"
            )
            (record / "run.json").write_text(
                json.dumps(
                    {
                        "elapsed_seconds": 6,
                        "workflow_version": "test",
                        "prompt_version": "test",
                        "model": "test",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                update_results(
                    results,
                    root / "outputs",
                    ROOT / "experiments/data/gold_standard.csv",
                ),
                1,
            )
            with results.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            row = next(
                row
                for row in rows
                if row["item_id"] == "DORA-15" and row["method"] == "llm_only"
            )
            self.assertEqual(row["coverage_correct"], "1")
            self.assertEqual(row["execution_time_min"], "0.100")
            self.assertEqual(row["missing_mapping_proposed"], "0")

    def test_manual_time_is_copied_to_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results = prepare_result_table(
                ROOT / "experiments/data/items.csv", root / "results.csv"
            )
            output = root / "outputs/manual"
            output.mkdir(parents=True)
            (output / "item_summary.csv").write_text(
                "item_id,coverage,missing_mapping,time_min\nDORA-15,Yes,,17\n",
                encoding="utf-8",
            )
            self.assertEqual(
                update_results(
                    results,
                    root / "outputs",
                    ROOT / "experiments/data/gold_standard.csv",
                ),
                1,
            )
            with results.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            row = next(
                row
                for row in rows
                if row["item_id"] == "DORA-15" and row["method"] == "manual"
            )
            self.assertEqual(row["execution_time_min"], "17.000")


if __name__ == "__main__":
    unittest.main()
