from __future__ import annotations

import unittest
from pathlib import Path

from agent.evidence import LocalArticleProvider
from agent.models import AssessmentItem, ProvisionRef


ROOT = Path(__file__).resolve().parents[2]


class LocalArticleProviderTest(unittest.TestCase):
    def test_returns_exact_paragraph_and_ranked_gap_evidence(self) -> None:
        provider = LocalArticleProvider(
            ROOT / "experiments/data/ai_act_legal_text.json",
            top_k=5,
        )
        item = AssessmentItem(
            item_id="TC01",
            framework="EU AI Act",
            instrument="Regulation (EU) 2024/1689",
            domain="Transparency",
            control_statement="Inform a person that they are interacting with AI.",
            expected_evidence="Notice",
            applicability="Direct interaction",
            existing_mapping="Article 50(1)",
            source_row=5,
        )

        exact = provider.retrieve(
            item,
            item.control_statement,
            ProvisionRef(item.instrument, "Article 50(1)"),
        )
        gaps = provider.retrieve(item, item.control_statement, None)

        self.assertEqual([entry.provision for entry in exact], ["Article 50(1)"])
        self.assertEqual(len(gaps), 5)
        self.assertTrue(provider.metadata["provisional"])


if __name__ == "__main__":
    unittest.main()
