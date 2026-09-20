from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_manual_review import prepare_manual_review


ROOT = Path(__file__).resolve().parents[2]


class ManualReviewTest(unittest.TestCase):
    def test_manual_form_is_blank(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = prepare_manual_review(
                ROOT / "agent/tests/fixtures/dev_items.csv",
                Path(directory) / "manual",
            )

            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"item_summary.csv"},
            )
            with (output / "item_summary.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                items = list(csv.DictReader(handle))

            self.assertEqual(len(items), 1)
            self.assertEqual(
                list(items[0]),
                [
                    "item_id",
                    "coverage",
                    "missing_mapping",
                    "time_min",
                ],
            )
            self.assertTrue(all(not row["coverage"] for row in items))


if __name__ == "__main__":
    unittest.main()
