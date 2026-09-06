from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agent.evidence import validate_experiment_profile
from agent.models import AssessmentItem


def item(instrument: str = "Regulation (EU) 2024/1689") -> AssessmentItem:
    return AssessmentItem(
        item_id="DEV-01",
        framework="Test",
        instrument=instrument,
        domain="Test",
        control_statement="Test statement",
        expected_evidence="",
        applicability="",
        existing_mapping="Article 9",
        source_row=1,
    )


class ExperimentProfileTest(unittest.TestCase):
    def test_frozen_profile_must_cover_the_item(self) -> None:
        profile = {
            "corpus_status": "frozen",
            "frozen_at": "2026-09-06",
            "processed_corpus": {"chunk_count": 1, "chunk_set_hash": "sha256:test"},
            "document_ids": ["EU-2024-1689"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps(profile), encoding="utf-8")
            validate_experiment_profile(path, [item()])

    def test_development_profile_is_rejected(self) -> None:
        profile = {
            "corpus_status": "development",
            "frozen_at": None,
            "processed_corpus": {"chunk_count": 1, "chunk_set_hash": "sha256:test"},
            "document_ids": ["EU-2024-1689"],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps(profile), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be frozen"):
                validate_experiment_profile(path, [item()])


if __name__ == "__main__":
    unittest.main()
