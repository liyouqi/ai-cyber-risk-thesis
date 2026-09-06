from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent.evidence import ReplayEvidenceProvider
from agent.models import AssessmentItem
from agent.workflow import run_llm_only, run_review, write_run


ROOT = Path(__file__).resolve().parents[2]


class FakeLlm:
    model = "test-model"

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        return {
            "mapping_reviews": [
                {
                    "instrument": "Test Regulation",
                    "provision": "Article 1",
                    "decision": "Supported",
                    "reason": "The evidence expressly requires an access review record.",
                    "evidence_ids": ["test-article-1"],
                }
            ],
            "missing_mappings": [],
            "applicability_note": "No extra condition is stated in the supplied text.",
            "overall_assessment": "Correct",
            "challenge_comment": "Retain the reference and confirm the review record.",
        }


class FakeLlmOnly(FakeLlm):
    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        response = super().generate_json(system_prompt, user_prompt)
        response["mapping_reviews"][0]["evidence_ids"] = []
        return response


class RepairingFakeLlm(FakeLlm):
    def __init__(self) -> None:
        self.calls = 0

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        self.calls += 1
        response = super().generate_json(system_prompt, user_prompt)
        if self.calls == 1:
            response["mapping_reviews"][0]["evidence_ids"] = []
        return response


class AlwaysUncitedFakeLlm(FakeLlm):
    def __init__(self) -> None:
        self.calls = 0

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        self.calls += 1
        response = super().generate_json(system_prompt, user_prompt)
        response["mapping_reviews"][0]["evidence_ids"] = []
        return response


class WorkflowTest(unittest.TestCase):
    def test_replay_run_is_written_with_audit_files(self) -> None:
        item = AssessmentItem(
            item_id="DEV-01",
            framework="Test",
            instrument="Test Regulation",
            domain="Access control",
            control_statement="Keep an access review record.",
            expected_evidence="Access review record",
            applicability="Test organisations",
            existing_mapping="Article 1",
            source_row=1,
        )
        provider = ReplayEvidenceProvider(ROOT / "agent/tests/fixtures/replay_evidence.json")
        run = run_review(item, provider, FakeLlm(), "test prompt")
        self.assertEqual(run.response["overall_assessment"], "Correct")

        with tempfile.TemporaryDirectory() as directory:
            output = write_run(run, Path(directory) / "run")
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {
                    "run.json",
                    "evidence.json",
                    "raw_response.json",
                    "provision_checks.csv",
                    "item_summary.csv",
                },
            )
            self.assertEqual(
                (output / "item_summary.csv").read_text(encoding="utf-8").splitlines()[0],
                "item_id,overall_assessment,missing_mapping,applicability_note,challenge_comment",
            )

    def test_llm_only_uses_no_retrieved_evidence(self) -> None:
        item = AssessmentItem(
            item_id="DEV-01",
            framework="Test",
            instrument="Test Regulation",
            domain="Access control",
            control_statement="Keep an access review record.",
            expected_evidence="Access review record",
            applicability="Test organisations",
            existing_mapping="Article 1",
            source_row=1,
        )
        run = run_llm_only(item, FakeLlmOnly(), "test prompt")
        self.assertEqual(run.method, "llm_only")
        self.assertEqual(run.evidence, [])

        with tempfile.TemporaryDirectory() as directory:
            output = write_run(run, Path(directory) / "run")
            self.assertFalse((output / "evidence.json").exists())
            self.assertTrue((output / "raw_response.json").exists())

    def test_agent_preserves_one_correction_retry(self) -> None:
        item = AssessmentItem(
            item_id="DEV-01",
            framework="Test",
            instrument="Test Regulation",
            domain="Access control",
            control_statement="Keep an access review record.",
            expected_evidence="Access review record",
            applicability="Test organisations",
            existing_mapping="Article 1",
            source_row=1,
        )
        provider = ReplayEvidenceProvider(ROOT / "agent/tests/fixtures/replay_evidence.json")
        llm = RepairingFakeLlm()
        run = run_review(item, provider, llm, "test prompt")
        self.assertEqual(llm.calls, 2)
        self.assertEqual(len(run.raw_attempts), 2)

        with tempfile.TemporaryDirectory() as directory:
            output = write_run(run, Path(directory) / "run")
            self.assertTrue((output / "raw_attempts.json").exists())

    def test_agent_downgrades_an_uncited_decision_after_retry(self) -> None:
        item = AssessmentItem(
            item_id="DEV-01",
            framework="Test",
            instrument="Test Regulation",
            domain="Access control",
            control_statement="Keep an access review record.",
            expected_evidence="Access review record",
            applicability="Test organisations",
            existing_mapping="Article 1",
            source_row=1,
        )
        provider = ReplayEvidenceProvider(ROOT / "agent/tests/fixtures/replay_evidence.json")
        llm = AlwaysUncitedFakeLlm()
        run = run_review(item, provider, llm, "test prompt")
        self.assertEqual(llm.calls, 2)
        self.assertEqual(
            run.response["mapping_reviews"][0]["decision"],
            "Unable to determine",
        )
        self.assertTrue(run.guardrail_changes)


if __name__ == "__main__":
    unittest.main()
