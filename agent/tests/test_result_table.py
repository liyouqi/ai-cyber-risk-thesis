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
                ROOT / "experiments/data/items.csv",
                Path(directory) / "item_results.csv",
            )
            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(len(rows), 120)
            dora_18 = [row for row in rows if row["item_id"] == "DORA-18"]
            self.assertEqual(
                {row["method"] for row in dora_18},
                {"manual", "llm_only", "agentic_rag"},
            )
            self.assertTrue(all(row["existing_mapping_total"] == "2" for row in dora_18))
            self.assertTrue(all(not row["total_time_min"] for row in rows))

    def test_saved_run_updates_only_objective_result_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results = prepare_result_table(
                ROOT / "experiments/data/pilot_items.csv",
                root / "results.csv",
            )
            record = root / "outputs/llm_only/records/DORA-15"
            record.mkdir(parents=True)
            (record / "run.json").write_text(
                json.dumps({"item_id": "DORA-15", "elapsed_seconds": 6}),
                encoding="utf-8",
            )
            (record / "raw_response.json").write_text(
                json.dumps({"missing_mappings": []}),
                encoding="utf-8",
            )

            self.assertEqual(update_results(results, root / "outputs"), 1)
            with results.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            row = next(
                row
                for row in rows
                if row["item_id"] == "DORA-15" and row["method"] == "llm_only"
            )
            self.assertEqual(row["execution_time_min"], "0.100")
            self.assertEqual(row["missing_mapping_proposed"], "0")
            self.assertEqual(row["existing_mapping_correct"], "")


if __name__ == "__main__":
    unittest.main()
