from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from agent.batch import combine_review_tables


class BatchOutputTest(unittest.TestCase):
    def test_combines_item_tables_for_spreadsheet_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            records = output / "records"
            records.mkdir()
            for item_id in ("A", "B"):
                folder = records / item_id
                folder.mkdir()
                (folder / "provision_checks.csv").write_text(
                    f"item_id,decision\n{item_id},Supported\n",
                    encoding="utf-8",
                )
                (folder / "item_summary.csv").write_text(
                    f"item_id,overall_assessment\n{item_id},Correct\n",
                    encoding="utf-8",
                )

            combine_review_tables(output, ["A", "B"])
            with (output / "provision_checks.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["item_id"] for row in rows], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
