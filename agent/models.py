"""Small data objects used by the review workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AssessmentItem:
    item_id: str
    framework: str
    instrument: str
    domain: str
    control_statement: str
    expected_evidence: str
    applicability: str
    existing_mapping: str
    source_row: int

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> "AssessmentItem":
        return cls(
            item_id=row["item_id"].strip(),
            framework=row["framework"].strip(),
            instrument=row["instrument"].strip(),
            domain=row["domain"].strip(),
            control_statement=row["control_statement"].strip(),
            expected_evidence=row.get("expected_evidence", "").strip(),
            applicability=row.get("applicability", "").strip(),
            existing_mapping=row["existing_mapping"].strip(),
            source_row=int(row["source_row"]),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProvisionRef:
    instrument: str
    provision: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.instrument.casefold(), self.provision.casefold())

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    document_id: str
    text: str
    source_locator: str
    source_url: str
    rank: int | None = None
    score: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evidence":
        """Load canonical HTTP evidence or a legacy development fixture."""
        return cls(
            evidence_id=str(data["evidence_id"]),
            document_id=str(data.get("document_id", data.get("instrument", ""))),
            text=str(data["text"]),
            source_locator=str(
                data.get("source_locator", data.get("provision", ""))
            ),
            source_url=str(data.get("source_url", data.get("source", ""))),
            rank=(int(data["rank"]) if data.get("rank") is not None else None),
            score=(float(data["score"]) if data.get("score") is not None else None),
        )

    @property
    def instrument(self) -> str:
        """Backward-compatible alias used by development replay filtering."""
        return self.document_id

    @property
    def provision(self) -> str:
        """Backward-compatible alias for source_locator."""
        return self.source_locator

    @property
    def source(self) -> str:
        """Backward-compatible alias for source_url."""
        return self.source_url

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
