"""Replaceable evidence sources for development replay and Regulatory RAG."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Protocol

from agent.models import AssessmentItem, Evidence, ProvisionRef


INSTRUMENT_DOCUMENT_IDS = {
    "Regulation (EU) 2024/1689": "EU-2024-1689",
    "Regulation (EU) 2022/2554": "EU-2022-2554",
    "Commission Delegated Regulation (EU) 2025/301": "EU-2025-301",
    "Commission Delegated Regulation (EU) 2024/1774": "EU-2024-1774",
    "Commission Delegated Regulation (EU) 2024/1773": "EU-2024-1773",
}


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
        output = self._direct_evidence(provision) if provision else []
        for hit in result.evidence:
            chunk = self._engine.get(hit.evidence_id)
            output.append(self._as_evidence(chunk))
        return output

    @staticmethod
    def _as_evidence(chunk: Any) -> Evidence:
        return Evidence(
            evidence_id=chunk.evidence_id,
            instrument=chunk.document_id,
            provision=chunk.source_locator,
            text=chunk.text,
            source=str(chunk.source_url),
        )

    def _direct_evidence(self, provision: ProvisionRef) -> list[Evidence]:
        document_id = INSTRUMENT_DOCUMENT_IDS.get(provision.instrument)
        if not document_id:
            return []
        locator = provision.provision.casefold()
        slug = re.sub(r"[^a-z0-9]+", "-", locator).strip("-")
        base = f"{document_id.casefold()}-{slug}"
        evidence_ids = [base]
        if re.fullmatch(r"article-\d+", slug):
            evidence_ids.extend(f"{base}-{paragraph}" for paragraph in range(1, 21))

        output: list[Evidence] = []
        found_child = False
        for evidence_id in evidence_ids:
            try:
                chunk = self._engine.get(evidence_id)
            except KeyError:
                if found_child and evidence_id != base:
                    break
                continue
            output.append(self._as_evidence(chunk))
            if evidence_id != base:
                found_child = True
        return output
