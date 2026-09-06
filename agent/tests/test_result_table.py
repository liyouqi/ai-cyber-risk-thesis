from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_result_table import prepare_result_table


ROOT = Path(__file__).resolve().parents[2]


class ResultTableTest(unittest.TestCase):
    def test_main_table_contains_three_blank_method_rows_per_item(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = prepare_result_table(
                ROOT / "experiments/datasets/items.csv",
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


if __name__ == "__main__":
    unittest.main()
