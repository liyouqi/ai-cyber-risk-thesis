"""Replaceable evidence sources for development replay and Regulatory RAG."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from agent.models import AssessmentItem, Evidence, ProvisionRef


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
            item_id: [Evidence(**entry) for entry in entries]
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


class RegulatoryRagProvider:
    name = "regulatory-rag"

    def __init__(
        self,
        project_root: str | Path,
        *,
        profile: str | Path | None = None,
        mode: str = "hybrid",
        top_k: int = 8,
    ) -> None:
        try:
            from regulatory_rag import RegulatoryRagEngine
        except ImportError as exc:
            raise RuntimeError("regulatory-rag is not installed in this environment") from exc

        overrides: dict[str, object] = {}
        if profile:
            overrides["corpus_profile_path"] = Path(profile).expanduser().resolve()
        self._engine = RegulatoryRagEngine.from_project_root(project_root, **overrides)
        self._mode = mode
        self._top_k = top_k

    @property
    def status(self) -> dict[str, object]:
        return self._engine.describe().model_dump(mode="json")

    @property
    def metadata(self) -> dict[str, object]:
        status = self.status
        return {
            "corpus_id": status.get("corpus_id"),
            "corpus_version": status.get("corpus_version"),
            "document_count": status.get("document_count"),
            "chunk_count": status.get("chunk_count"),
            "retrieval_mode": self._mode,
            "top_k": self._top_k,
        }

    def retrieve(
        self,
        item: AssessmentItem,
        query: str,
        provision: ProvisionRef | None,
    ) -> list[Evidence]:
        from regulatory_rag import RetrievalRequest

        result = self._engine.retrieve(
            RetrievalRequest(
                query=query,
                retrieval_mode=self._mode,
                top_k=self._top_k,
            )
        )
        output: list[Evidence] = []
        for hit in result.evidence:
            chunk = self._engine.get(hit.evidence_id)
            output.append(
                Evidence(
                    evidence_id=chunk.evidence_id,
                    instrument=chunk.document_id,
                    provision=chunk.source_locator,
                    text=chunk.text,
                    source=str(chunk.source_url),
                )
            )
        return output
