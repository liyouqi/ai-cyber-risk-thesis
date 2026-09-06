from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.prepare_manual_review import prepare_manual_review


ROOT = Path(__file__).resolve().parents[2]


class ManualReviewTest(unittest.TestCase):
    def test_pilot_forms_are_blank_and_provisions_are_split(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = prepare_manual_review(
                ROOT / "experiments/data/pilot_items.csv",
                Path(directory) / "manual",
            )

            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"provision_checks.csv", "item_summary.csv", "timing.csv"},
            )
            with (output / "provision_checks.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                mappings = list(csv.DictReader(handle))
            with (output / "item_summary.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                items = list(csv.DictReader(handle))

            self.assertEqual(len(mappings), 10)
            self.assertEqual(len(items), 4)
            self.assertTrue(all(not row["decision"] for row in mappings))
            self.assertIn(
                {
                    "item_id": "DORA-18",
                    "instrument": "Regulation (EU) 2022/2554",
                    "provision": "Article 11(6)",
                    "decision": "",
                    "reason": "",
                    "evidence_reference": "",
                    "evidence_excerpt": "",
                },
                mappings,
            )


if __name__ == "__main__":
    unittest.main()
