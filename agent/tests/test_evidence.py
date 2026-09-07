from __future__ import annotations

import unittest

from agent.evidence import HttpRegulatoryRagAdapter, RegulatoryRagHttpError
from agent.models import AssessmentItem, ProvisionRef


class FakeResponse:
    def __init__(self, status_code: int, body: object) -> None:
        self.status_code = status_code
        self._body = body

    def json(self) -> object:
        return self._body


class FakeSession:
    def __init__(self, posts: list[FakeResponse] | None = None) -> None:
        self.posts = list(posts or [])
        self.calls: list[dict[str, object]] = []

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": "GET", "url": url, **kwargs})
        if url.endswith("/health"):
            return FakeResponse(200, {"status": "ready"})
        return FakeResponse(
            200,
            {
                "schema_version": "1.0",
                "corpus_id": "test-corpus",
                "corpus_version": "test-release",
                "document_count": 2,
                "chunk_count": 20,
                "supported_modes": ["bm25", "hybrid"],
                "vector_index_available": True,
                "supported_query_modes": ["direct", "planned"],
                "planner_available": True,
            },
        )

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"method": "POST", "url": url, **kwargs})
        return self.posts.pop(0)


def item() -> AssessmentItem:
    return AssessmentItem(
        item_id="TC05",
        framework="EU AI Act",
        instrument="Regulation (EU) 2024/1689",
        domain="IAM",
        control_statement="Use least privilege and access reviews.",
        expected_evidence="Access matrix",
        applicability="All systems",
        existing_mapping="Article 9",
        source_row=9,
    )


def chunk(evidence_id: str = "eu-2024-1689-article-9-1") -> dict[str, object]:
    return {
        "evidence_id": evidence_id,
        "document_id": "EU-2024-1689",
        "text": "A risk management system shall be established.",
        "source_locator": "Article 9(1)",
        "source_url": "http://data.europa.eu/eli/reg/2024/1689/oj",
        "frameworks": ["ai_act"],
    }


class HttpRegulatoryRagAdapterTest(unittest.TestCase):
    def test_checks_health_and_status_then_uses_direct_with_complete_evidence(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    200,
                    {
                        "schema_version": "1.0",
                        "query": "q",
                        "index_version": "test-bm25",
                        "hits": [
                            {
                                "rank": 1,
                                "score": 2.5,
                                "retriever": "bm25",
                                "retriever_ranks": {"bm25": 1},
                                "evidence": chunk(),
                            }
                        ],
                        "retrieval_metadata": {
                            "retrieval_mode": "bm25",
                            "candidate_count": 1,
                            "retrieval_ms": 2,
                        },
                    },
                )
            ]
        )
        adapter = HttpRegulatoryRagAdapter(
            "http://rag.test/",
            api_key="secret",
            session=session,  # type: ignore[arg-type]
        )
        evidence = adapter.retrieve(
            item(),
            "Does Article 9 support least privilege?",
            ProvisionRef("Regulation (EU) 2024/1689", "Article 9"),
        )

        self.assertEqual(
            [call["method"] for call in session.calls], ["GET", "GET", "POST"]
        )
        post = session.calls[-1]
        self.assertEqual(post["timeout"], 30.0)
        self.assertEqual(
            post["headers"]["Authorization"], "Bearer secret"  # type: ignore[index]
        )
        payload = post["json"]
        self.assertEqual(payload["query_mode"], "direct")  # type: ignore[index]
        self.assertEqual(
            payload["scope"]["frameworks"], ["ai_act"]  # type: ignore[index]
        )
        self.assertEqual(
            payload["scope"]["document_ids"],  # type: ignore[index]
            ["EU-2024-1689"],
        )
        self.assertEqual(evidence[0].rank, 1)
        self.assertEqual(evidence[0].score, 2.5)
        self.assertEqual(evidence[0].document_id, "EU-2024-1689")
        self.assertEqual(evidence[0].source_locator, "Article 9(1)")

    def test_planned_preserves_plan_claim_coverage_and_uses_long_timeout(self) -> None:
        plan = {
            "question": "Which provision is missing?",
            "claims": [{"claim_id": "c1"}],
        }
        claims = [
            {
                "claim": {"claim_id": "c1"},
                "status": "covered",
                "evidence_refs": ["eu-2024-1689-article-9-1"],
            }
        ]
        session = FakeSession(
            [
                FakeResponse(
                    200,
                    {
                        "schema_version": "1.0",
                        "query_mode": "planned",
                        "status": "retrieved",
                        "query": "Which provision is missing?",
                        "planned_result": {
                            "plan": plan,
                            "claims": claims,
                            "evidence": [chunk()],
                            "metadata": {"index_version": "test-bm25"},
                        },
                        "planning_ms": 12,
                    },
                )
            ]
        )
        adapter = HttpRegulatoryRagAdapter(
            "http://rag.test", session=session  # type: ignore[arg-type]
        )
        evidence = adapter.retrieve(item(), "Which provision is missing?", None)

        self.assertEqual(session.calls[-1]["timeout"], 120.0)
        self.assertEqual(
            session.calls[-1]["json"]["query_mode"], "planned"  # type: ignore[index]
        )
        self.assertEqual(evidence[0].evidence_id, "eu-2024-1689-article-9-1")
        trace = adapter.metadata["retrievals"][0]  # type: ignore[index]
        self.assertEqual(trace["plan"], plan)
        self.assertEqual(trace["claim_coverage"], claims)

    def test_empty_result_is_recorded_without_scope_expansion(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    200,
                    {
                        "query": "q",
                        "index_version": "test-bm25",
                        "hits": [],
                        "retrieval_metadata": {},
                    },
                )
            ]
        )
        adapter = HttpRegulatoryRagAdapter(
            "http://rag.test", session=session  # type: ignore[arg-type]
        )
        evidence = adapter.retrieve(
            item(),
            "Does Article 9 support least privilege?",
            ProvisionRef("Regulation (EU) 2024/1689", "Article 9"),
        )

        self.assertEqual(evidence, [])
        self.assertEqual(
            len([call for call in session.calls if call["method"] == "POST"]), 1
        )
        self.assertEqual(
            adapter.metadata["retrievals"][0]["status"], "empty"  # type: ignore[index]
        )

    def test_service_error_is_explicit(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    503,
                    {"error": "planner_unavailable", "message": "not configured"},
                )
            ]
        )
        adapter = HttpRegulatoryRagAdapter(
            "http://rag.test", session=session  # type: ignore[arg-type]
        )
        with self.assertRaisesRegex(RegulatoryRagHttpError, "planner_unavailable"):
            adapter.retrieve(item(), "Which provision is missing?", None)

    def test_unknown_instrument_fails_instead_of_broadening_scope(self) -> None:
        session = FakeSession()
        adapter = HttpRegulatoryRagAdapter(
            "http://rag.test", session=session  # type: ignore[arg-type]
        )
        with self.assertRaisesRegex(RegulatoryRagHttpError, "document ID"):
            adapter.retrieve(
                item(),
                "Does Article 9 support least privilege?",
                ProvisionRef("Unknown Regulation", "Article 9"),
            )
        self.assertEqual(
            len([call for call in session.calls if call["method"] == "POST"]), 0
        )


if __name__ == "__main__":
    unittest.main()
