"""One-item regulatory mapping review workflow."""

from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent.evidence import EvidenceProvider
from agent.llm import JsonLlm
from agent.models import AssessmentItem, Evidence, ProvisionRef
from agent.references import parse_mapping


MAPPING_DECISIONS = {
    "Supported",
    "Partially supported",
    "Unsupported",
    "Unable to determine",
}
OVERALL_DECISIONS = {
    "Correct",
    "Partially correct",
    "Incorrect",
    "Unable to determine",
}


@dataclass(frozen=True)
class ReviewRun:
    item: AssessmentItem
    method: str
    provider: str
    provider_details: dict[str, Any]
    model: str
    model_settings: dict[str, Any]
    provisions: list[ProvisionRef]
    queries: list[dict[str, str]]
    evidence: list[Evidence]
    response: dict[str, Any]
    elapsed_seconds: float
    eligible_for_experiment: bool
    prompt_version: str


def load_item(path: str | Path, item_id: str) -> AssessmentItem:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        matches = [
            AssessmentItem.from_dict(row)
            for row in csv.DictReader(handle)
            if row["item_id"].strip() == item_id
        ]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {item_id}; found {len(matches)}")
    return matches[0]


def load_items(path: str | Path) -> list[AssessmentItem]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        items = [AssessmentItem.from_dict(row) for row in csv.DictReader(handle)]
    if not items:
        raise ValueError(f"No assessment items found in {path}")
    if len({item.item_id for item in items}) != len(items):
        raise ValueError(f"Duplicate item IDs in {path}")
    return items


def _query(item: AssessmentItem, provision: ProvisionRef | None) -> str:
    if provision:
        return (
            f"Does {provision.provision} of {provision.instrument} support this "
            f"requirement: {item.control_statement}"
        )
    return (
        f"Which provision of {item.instrument} is materially necessary for this "
        f"requirement but absent from the existing mapping: {item.control_statement}"
    )


def _deduplicate(evidence: list[Evidence]) -> list[Evidence]:
    seen: set[str] = set()
    output: list[Evidence] = []
    for entry in evidence:
        if entry.evidence_id not in seen:
            output.append(entry)
            seen.add(entry.evidence_id)
    return output


def _user_prompt(
    item: AssessmentItem,
    provisions: list[ProvisionRef],
    evidence: list[Evidence],
) -> str:
    data = {
        "assessment_item": item.as_dict(),
        "existing_provisions_to_review": [entry.as_dict() for entry in provisions],
        "retrieved_evidence": [entry.as_dict() for entry in evidence],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def _validate_response(
    response: dict[str, Any],
    provisions: list[ProvisionRef],
    evidence: list[Evidence],
    *,
    require_retrieved_evidence: bool,
) -> None:
    required = {
        "mapping_reviews",
        "missing_mappings",
        "applicability_note",
        "overall_assessment",
        "challenge_comment",
    }
    if not required.issubset(response):
        missing = ", ".join(sorted(required - response.keys()))
        raise ValueError(f"LLM output is missing fields: {missing}")

    reviews = response["mapping_reviews"]
    if not isinstance(reviews, list):
        raise ValueError("mapping_reviews must be a list")
    expected = {entry.key for entry in provisions}
    actual: list[tuple[str, str]] = []
    evidence_ids = {entry.evidence_id for entry in evidence}

    for review in reviews:
        if review.get("decision") not in MAPPING_DECISIONS:
            raise ValueError(f"Invalid mapping decision: {review.get('decision')}")
        key = (
            str(review.get("instrument", "")).casefold(),
            str(review.get("provision", "")).casefold(),
        )
        actual.append(key)
        cited = review.get("evidence_ids", [])
        if not isinstance(cited, list):
            raise ValueError("evidence_ids must be a list")
        if require_retrieved_evidence and not set(cited).issubset(evidence_ids):
            raise ValueError("A mapping review cites an unknown evidence ID")
        if (
            require_retrieved_evidence
            and review.get("decision") != "Unable to determine"
            and not cited
        ):
            raise ValueError("A substantive mapping decision must cite retrieved evidence")
        if not require_retrieved_evidence and cited:
            raise ValueError("LLM-only output must not invent retrieved evidence IDs")

    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("LLM output must review each existing provision exactly once")

    missing_mappings = response["missing_mappings"]
    if not isinstance(missing_mappings, list):
        raise ValueError("missing_mappings must be a list")
    for mapping in missing_mappings:
        cited = mapping.get("evidence_ids", [])
        if not isinstance(cited, list):
            raise ValueError("evidence_ids must be a list")
        if require_retrieved_evidence and (not cited or not set(cited).issubset(evidence_ids)):
            raise ValueError("Each missing mapping must cite retrieved evidence")
        if not require_retrieved_evidence and cited:
            raise ValueError("LLM-only output must not invent retrieved evidence IDs")

    if response["overall_assessment"] not in OVERALL_DECISIONS:
        raise ValueError("Invalid overall_assessment")
    for field in ("applicability_note", "challenge_comment"):
        if not isinstance(response[field], str):
            raise ValueError(f"{field} must be text")


def run_review(
    item: AssessmentItem,
    evidence_provider: EvidenceProvider,
    llm: JsonLlm,
    system_prompt: str,
    *,
    eligible_for_experiment: bool,
) -> ReviewRun:
    started = time.perf_counter()
    provisions = parse_mapping(item.existing_mapping, item.instrument)
    queries: list[dict[str, str]] = []
    retrieved: list[Evidence] = []

    for provision in provisions:
        query = _query(item, provision)
        queries.append({"purpose": "validate", "provision": provision.provision, "query": query})
        retrieved.extend(evidence_provider.retrieve(item, query, provision))

    gap_query = _query(item, None)
    queries.append({"purpose": "gap", "provision": "", "query": gap_query})
    retrieved.extend(evidence_provider.retrieve(item, gap_query, None))
    evidence = _deduplicate(retrieved)

    response = llm.generate_json(system_prompt, _user_prompt(item, provisions, evidence))
    _validate_response(
        response,
        provisions,
        evidence,
        require_retrieved_evidence=True,
    )
    return ReviewRun(
        item=item,
        method=(
            "agentic_rag"
            if evidence_provider.name == "regulatory-rag"
            else "development_replay"
        ),
        provider=evidence_provider.name,
        provider_details=getattr(evidence_provider, "metadata", {}),
        model=llm.model,
        model_settings=getattr(llm, "metadata", {"model": llm.model}),
        provisions=provisions,
        queries=queries,
        evidence=evidence,
        response=response,
        elapsed_seconds=round(time.perf_counter() - started, 3),
        eligible_for_experiment=eligible_for_experiment,
        prompt_version="agent-review-v0.1",
    )


def run_llm_only(
    item: AssessmentItem,
    llm: JsonLlm,
    system_prompt: str,
    *,
    eligible_for_experiment: bool,
) -> ReviewRun:
    """Review one item with model knowledge only and no retrieved evidence."""
    started = time.perf_counter()
    provisions = parse_mapping(item.existing_mapping, item.instrument)
    response = llm.generate_json(system_prompt, _user_prompt(item, provisions, []))
    _validate_response(
        response,
        provisions,
        [],
        require_retrieved_evidence=False,
    )
    return ReviewRun(
        item=item,
        method="llm_only",
        provider="none",
        provider_details={},
        model=llm.model,
        model_settings=getattr(llm, "metadata", {"model": llm.model}),
        provisions=provisions,
        queries=[],
        evidence=[],
        response=response,
        elapsed_seconds=round(time.perf_counter() - started, 3),
        eligible_for_experiment=eligible_for_experiment,
        prompt_version="llm-only-v0.1",
    )


def write_run(run: ReviewRun, output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)

    run_record = {
        "item_id": run.item.item_id,
        "method": run.method,
        "evidence_provider": run.provider,
        "evidence_provider_details": run.provider_details,
        "workflow_version": "0.1",
        "prompt_version": run.prompt_version,
        "model": run.model,
        "model_settings": run.model_settings,
        "elapsed_seconds": run.elapsed_seconds,
        "eligible_for_experiment": run.eligible_for_experiment,
        "queries": run.queries,
        "item": run.item.as_dict(),
    }
    (output / "run.json").write_text(
        json.dumps(run_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if run.evidence:
        (output / "evidence.json").write_text(
            json.dumps(
                [entry.as_dict() for entry in run.evidence],
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    (output / "raw_response.json").write_text(
        json.dumps(run.response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with (output / "mapping_reviews.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "item_id",
            "instrument",
            "provision",
            "decision",
            "reason",
            "evidence_reference",
            "evidence_excerpt",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        by_id = {entry.evidence_id: entry for entry in run.evidence}
        for review in run.response["mapping_reviews"]:
            cited = review.get("evidence_ids", [])
            excerpts = [by_id[evidence_id].text[:300] for evidence_id in cited]
            writer.writerow(
                {
                    "item_id": run.item.item_id,
                    "instrument": review["instrument"],
                    "provision": review["provision"],
                    "decision": review["decision"],
                    "reason": review["reason"],
                    "evidence_reference": "; ".join(cited),
                    "evidence_excerpt": " | ".join(excerpts),
                }
            )

    with (output / "item_reviews.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "item_id",
            "overall_assessment",
            "missing_mapping",
            "applicability_note",
            "challenge_comment",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "item_id": run.item.item_id,
                "overall_assessment": run.response["overall_assessment"],
                "missing_mapping": json.dumps(
                    run.response["missing_mappings"], ensure_ascii=False
                ),
                "applicability_note": run.response["applicability_note"],
                "challenge_comment": run.response["challenge_comment"],
            }
        )
    return output
