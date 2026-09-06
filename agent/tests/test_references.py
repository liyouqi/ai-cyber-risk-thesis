from __future__ import annotations

import unittest

from agent.references import DORA_LEVEL_1, parse_mapping


class ReferenceParserTest(unittest.TestCase):
    def test_semicolon_list(self) -> None:
        refs = parse_mapping("Art. 9; Art. 15; Art. 17", "AI Act")
        self.assertEqual(
            [ref.provision for ref in refs],
            ["Article 9", "Article 15", "Article 17"],
        )

    def test_paragraph_list(self) -> None:
        refs = parse_mapping("Art. 50(1),(5)", "AI Act")
        self.assertEqual([ref.provision for ref in refs], ["Article 50(1)", "Article 50(5)"])

    def test_paragraph_range(self) -> None:
        refs = parse_mapping("Article 35(6)-(7)", "Regulation")
        self.assertEqual([ref.provision for ref in refs], ["Article 35(6)", "Article 35(7)"])

    def test_article_range(self) -> None:
        refs = parse_mapping("Articles 8-9", "Regulation")
        self.assertEqual([ref.provision for ref in refs], ["Article 8", "Article 9"])

    def test_second_instrument(self) -> None:
        refs = parse_mapping(
            "Article 26, together with DORA Article 11(6)",
            "Commission Delegated Regulation (EU) 2024/1774",
        )
        self.assertEqual(refs[0].instrument, "Commission Delegated Regulation (EU) 2024/1774")
        self.assertEqual(refs[1].instrument, DORA_LEVEL_1)

    def test_annex(self) -> None:
        refs = parse_mapping("Art. 6 & Annex III", "AI Act")
        self.assertEqual([ref.provision for ref in refs], ["Article 6", "Annex III"])


if __name__ == "__main__":
    unittest.main()
