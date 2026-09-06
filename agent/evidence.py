"""Replaceable evidence sources for development replay and Regulatory RAG."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from agent.models import AssessmentItem, Evidence, ProvisionRef


INSTRUMENT_DOCUMENT_IDS = {
    "Regulation (EU) 2024/1689": "EU-2024-1689",
    "Regulation (EU) 2022/2554": "EU-2022-2554",
    "Commission Delegated Regulation (EU) 2025/301": "EU-2025-301",
    "Commission Delegated Regulation (EU) 2024/1774": "EU-2024-1774",
    "Commission Delegated Regulation (EU) 2024/1773": "EU-2024-1773",
}


def validate_experiment_profile(
    profile: str | Path | None,
    items: list[AssessmentItem],
) -> None:
    """Fail before a formal run if its frozen corpus cannot cover the items."""
    if not profile:
        raise ValueError("A specific frozen RAG profile is required for an experiment run")
    path = Path(profile).expanduser().resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("corpus_status") != "frozen" or not data.get("frozen_at"):
        raise ValueError("The RAG profile must be frozen before an experiment run")
    if not data.get("processed_corpus"):
        raise ValueError("The frozen RAG profile has no processed-corpus fingerprint")

    required: set[str] = set()
    for item in items:
        try:
            required.add(INSTRUMENT_DOCUMENT_IDS[item.instrument])
        except KeyError as exc:
            raise ValueError(f"Unknown experiment instrument: {item.instrument}") from exc
        if "DORA Article" in item.existing_mapping:
            required.add("EU-2022-2554")
    available = set(data.get("document_ids", []))
    missing = sorted(required - available)
    if missing:
        raise ValueError("The RAG profile is missing documents: " + ", ".join(missing))


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
        self._profile = Path(profile).expanduser().resolve() if profile else None
        if self._profile:
            overrides["corpus_profile_path"] = self._profile
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
            "profile": str(self._profile) if self._profile else "default",
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
