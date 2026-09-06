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
    instrument: str
    provision: str
    text: str
    source: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)
