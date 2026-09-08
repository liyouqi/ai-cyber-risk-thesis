"""Evidence providers for development replay and the Regulatory RAG HTTP API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

import requests

from agent.models import AssessmentItem, Evidence, ProvisionRef


INSTRUMENT_DOCUMENT_IDS = {
    "Regulation (EU) 2024/1689": "EU-2024-1689",
    "Regulation (EU) 2022/2554": "EU-2022-2554",
    "Commission Delegated Regulation (EU) 2025/301": "EU-2025-301",
    "Commission Delegated Regulation (EU) 2024/1774": "EU-2024-1774",
    "Commission Delegated Regulation (EU) 2024/1773": "EU-2024-1773",
}

FRAMEWORK_IDS = {
    "EU AI Act": "ai_act",
    "DORA": "dora",
}


class RegulatoryRagHttpError(RuntimeError):
    """Raised when the independent Regulatory RAG service cannot be used safely."""


class EvidenceProvider(Protocol):
    name: str

    def retrieve(
        self,
        item: AssessmentItem,
        query: str,
        provision: ProvisionRef | None,
    ) -> list[Evidence]: ...


class ReplayEvidenceProvider:
    name = "development-replay"

    def __init__(self, path: str | Path) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self._items = {
            item_id: [Evidence.from_dict(entry) for entry in entries]
            for item_id, entries in data.items()
        }

    @property
    def metadata(self) -> dict[str, object]:
        return {"source": "local replay file"}

    def retrieve(
        self,
        item: AssessmentItem,
        query: str,
        provision: ProvisionRef | None,
    ) -> list[Evidence]:
        evidence = self._items.get(item.item_id, [])
        if provision is None:
            return evidence
        exact = [
            entry
            for entry in evidence
            if entry.instrument.casefold() == provision.instrument.casefold()
            and entry.provision.casefold() == provision.provision.casefold()
        ]
        return exact or evidence


class HttpRegulatoryRagAdapter:
    """Read-only client for the independent Regulatory RAG HTTP service."""

    name = "regulatory-rag-http"

    def __init__(
        self,
        api_url: str,
        *,
        api_key: str | None = None,
        retrieval_mode: str = "hybrid",
        top_k: int = 8,
        direct_timeout: float = 30.0,
        planned_timeout: float = 120.0,
        session: requests.Session | None = None,
    ) -> None:
        if not api_url.strip():
            raise ValueError("REGULATORY_RAG_API_URL must not be empty")
        if retrieval_mode not in {"bm25", "vector", "hybrid"}:
            raise ValueError(f"Unsupported retrieval mode: {retrieval_mode}")
        if not 1 <= top_k <= 20:
            raise ValueError("RAG top_k must be between 1 and 20")
        self._api_url = api_url.rstrip("/")
        self._retrieval_mode = retrieval_mode
        self._top_k = top_k
        self._direct_timeout = direct_timeout
        self._planned_timeout = planned_timeout
        self._session = session or requests.Session()
        self._headers = {"Accept": "application/json"}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"
        self._retrievals: list[dict[str, Any]] = []
        self._health = self._get_json("/health", timeout=self._direct_timeout)
        if self._health.get("status") != "ready":
            raise RegulatoryRagHttpError(
                "Regulatory RAG /health did not report status=ready"
            )
        self._status = self._get_json(
            "/api/v1/status", timeout=self._direct_timeout
        )
        supported_query_modes = self._status.get("supported_query_modes", [])
        if (
            "direct" not in supported_query_modes
            or "planned" not in supported_query_modes
        ):
            raise RegulatoryRagHttpError(
                "Regulatory RAG status must advertise direct and planned query modes"
            )
        if self._status.get("planner_available") is not True:
            raise RegulatoryRagHttpError(
                "Regulatory RAG planned retrieval is unavailable at startup"
            )
        if self._retrieval_mode not in self._status.get("supported_modes", []):
            raise RegulatoryRagHttpError(
                f"Regulatory RAG does not support retrieval mode: {self._retrieval_mode}"
            )
        if (
            self._retrieval_mode in {"vector", "hybrid"}
            and self._status.get("vector_index_available") is not True
        ):
            raise RegulatoryRagHttpError(
                f"Regulatory RAG vector index is unavailable for {self._retrieval_mode}"
            )

    @property
    def metadata(self) -> dict[str, object]:
        return {
            "api_url": self._api_url,
            "health": self._health,
            "status": self._status,
            "retrieval_mode": self._retrieval_mode,
            "top_k": self._top_k,
            "direct_timeout_seconds": self._direct_timeout,
            "planned_timeout_seconds": self._planned_timeout,
            "retrievals": list(self._retrievals),
        }

    def _get_json(self, path: str, *, timeout: float) -> dict[str, Any]:
        try:
            response = self._session.get(
                self._api_url + path,
                headers=self._headers,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise RegulatoryRagHttpError(
                f"Regulatory RAG request failed for GET {path}: {exc}"
            ) from exc
        return self._response_json(response, f"GET {path}")

    def _post_json(
        self,
        path: str,
        payload: dict[str, Any],
        *,
        timeout: float,
    ) -> dict[str, Any]:
        try:
            response = self._session.post(
                self._api_url + path,
                headers={**self._headers, "Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise RegulatoryRagHttpError(
                f"Regulatory RAG request failed for POST {path}: {exc}"
            ) from exc
        return self._response_json(response, f"POST {path}")

    @staticmethod
    def _response_json(response: Any, operation: str) -> dict[str, Any]:
        try:
            data = response.json()
        except (ValueError, TypeError) as exc:
            raise RegulatoryRagHttpError(
                f"{operation} returned a non-JSON response (HTTP {response.status_code})"
            ) from exc
        if not isinstance(data, dict):
            raise RegulatoryRagHttpError(f"{operation} returned a non-object JSON body")
        if not 200 <= response.status_code < 300:
            error = data.get("error", "http_error")
            if isinstance(error, dict):
                code = error.get("code", "http_error")
                message = error.get("message", "")
            else:
                code = error
                message = data.get("message", "")
            detail = f": {message}" if message else ""
            raise RegulatoryRagHttpError(
                f"{operation} failed with HTTP {response.status_code} ({code}){detail}"
            )
        return data

    @staticmethod
    def _scope(item: AssessmentItem, provision: ProvisionRef | None) -> dict[str, Any]:
        instrument = provision.instrument if provision else item.instrument
        document_id = INSTRUMENT_DOCUMENT_IDS.get(instrument)
        if not document_id:
            raise RegulatoryRagHttpError(
                f"No fixed Regulatory RAG document ID for instrument: {instrument}"
            )
        framework_id = FRAMEWORK_IDS.get(item.framework)
        if not framework_id:
            raise RegulatoryRagHttpError(
                f"No fixed Regulatory RAG framework ID for: {item.framework}"
            )
        return {
            "frameworks": [framework_id],
            "document_ids": [document_id],
            "jurisdictions": ["EU"],
            "entity_types": [],
            "topics": [],
        }

    @staticmethod
    def _evidence(
        raw: dict[str, Any],
        *,
        rank: int | None = None,
        score: float | None = None,
    ) -> Evidence:
        missing = [
            field
            for field in (
                "evidence_id",
                "document_id",
                "text",
                "source_locator",
                "source_url",
            )
            if field not in raw
        ]
        if missing:
            raise RegulatoryRagHttpError(
                "Regulatory RAG evidence is missing fields: " + ", ".join(missing)
            )
        return Evidence(
            evidence_id=str(raw["evidence_id"]),
            document_id=str(raw["document_id"]),
            text=str(raw["text"]),
            source_locator=str(raw["source_locator"]),
            source_url=str(raw["source_url"]),
            rank=(
                int(raw.get("rank", rank))
                if raw.get("rank", rank) is not None
                else None
            ),
            score=(
                float(raw.get("score", score))
                if raw.get("score", score) is not None
                else None
            ),
        )

    def retrieve(
        self,
        item: AssessmentItem,
        query: str,
        provision: ProvisionRef | None,
    ) -> list[Evidence]:
        query_mode = "direct" if provision else "planned"
        payload = {
            "schema_version": "1.0",
            "query": query,
            "query_mode": query_mode,
            "retrieval_mode": self._retrieval_mode,
            "top_k": self._top_k,
            "scope": self._scope(item, provision),
        }
        body = self._post_json(
            "/api/v1/retrieve",
            payload,
            timeout=(
                self._direct_timeout
                if query_mode == "direct"
                else self._planned_timeout
            ),
        )
        if query_mode == "direct":
            hits = body.get("hits")
            if not isinstance(hits, list):
                raise RegulatoryRagHttpError(
                    "Direct retrieval response is missing the hits list"
                )
            evidence = []
            for hit in hits:
                if not isinstance(hit, dict) or not isinstance(
                    hit.get("evidence"), dict
                ):
                    raise RegulatoryRagHttpError("Direct retrieval returned an invalid hit")
                evidence.append(
                    self._evidence(
                        hit["evidence"],
                        rank=hit.get("rank"),
                        score=hit.get("score"),
                    )
                )
            self._retrievals.append(
                {
                    "query": query,
                    "query_mode": query_mode,
                    "scope": payload["scope"],
                    "status": "retrieved" if evidence else "empty",
                    "index_version": body.get("index_version"),
                    "retrieval_metadata": body.get("retrieval_metadata"),
                }
            )
            return evidence

        status = body.get("status")
        if status != "retrieved":
            message = (
                body.get("clarifying_question")
                or body.get("message")
                or "Planned retrieval did not return evidence"
            )
            raise RegulatoryRagHttpError(
                f"Planned retrieval returned status={status!r}: {message}"
            )
        planned = body.get("planned_result")
        if not isinstance(planned, dict):
            raise RegulatoryRagHttpError(
                "Planned retrieval response is missing planned_result"
            )
        claim_coverage = planned.get("claims")
        if not isinstance(claim_coverage, list):
            raise RegulatoryRagHttpError(
                "Planned retrieval response is missing claim coverage"
            )
        admitted_refs: set[str] = set()
        for coverage in claim_coverage:
            if not isinstance(coverage, dict):
                raise RegulatoryRagHttpError(
                    "Planned retrieval returned invalid claim coverage"
                )
            refs = coverage.get("evidence_refs")
            if not isinstance(refs, list):
                raise RegulatoryRagHttpError(
                    "Planned claim coverage is missing evidence_refs"
                )
            if coverage.get("status") in {"covered", "partially_covered"}:
                admitted_refs.update(str(ref) for ref in refs)

        raw_evidence = planned.get("evidence")
        if not isinstance(raw_evidence, list):
            raise RegulatoryRagHttpError(
                "Planned retrieval response is missing the evidence list"
            )
        all_evidence = [
            self._evidence(entry)
            for entry in raw_evidence
            if isinstance(entry, dict)
        ]
        if len(all_evidence) != len(raw_evidence):
            raise RegulatoryRagHttpError("Planned retrieval returned invalid evidence")
        available_refs = {entry.evidence_id for entry in all_evidence}
        missing_refs = admitted_refs - available_refs
        if missing_refs:
            raise RegulatoryRagHttpError(
                "Planned claim coverage references missing evidence: "
                + ", ".join(sorted(missing_refs))
            )
        evidence = [
            entry for entry in all_evidence if entry.evidence_id in admitted_refs
        ]
        self._retrievals.append(
            {
                "query": query,
                "query_mode": query_mode,
                "scope": payload["scope"],
                "status": "retrieved" if evidence else "empty",
                "planning_ms": body.get("planning_ms"),
                "plan": planned.get("plan"),
                "claim_coverage": claim_coverage,
                "retrieval_metadata": planned.get("metadata"),
            }
        )
        return evidence
