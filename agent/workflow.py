"""One-item regulatory mapping review workflow."""

from __future__ import annotations

import csv
import copy
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
    raw_attempts: list[dict[str, Any]]
    guardrail_changes: list[str]
    elapsed_seconds: float
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


def _repair_prompt(
    original_prompt: str,
    response: dict[str, Any],
    error: str,
) -> str:
    repair = {
        "validation_error": error,
        "previous_response": response,
        "instruction": (
            "Return a corrected JSON object. Keep the substantive conclusions "
            "unless the validation error requires a change. Use only evidence IDs "
            "present in the original input."
        ),
    }
    return original_prompt + "\n\nCORRECTION REQUEST\n" + json.dumps(
        repair,
        ensure_ascii=False,
        indent=2,
    )


def _apply_evidence_guardrail(
    response: dict[str, Any],
    evidence: list[Evidence],
) -> tuple[dict[str, Any], list[str]]:
    """Remove unsupported evidence claims after the single model retry."""
    corrected = copy.deepcopy(response)
    changes: list[str] = []
    known = {entry.evidence_id for entry in evidence}

    reviews = corrected.get("mapping_reviews", [])
    if isinstance(reviews, list):
        for review in reviews:
            if not isinstance(review, dict):
                continue
            cited = review.get("evidence_ids", [])
            valid = (
                [evidence_id for evidence_id in cited if evidence_id in known]
                if isinstance(cited, list)
                else []
            )
            if valid != cited:
                review["evidence_ids"] = valid
                changes.append(
                    f"Removed unknown evidence IDs from {review.get('provision', 'a review')}"
                )
            if review.get("decision") != "Unable to determine" and not valid:
                review["decision"] = "Unable to determine"
                review["reason"] = "No retrieved evidence was cited for this decision."
                changes.append(
                    f"Downgraded {review.get('provision', 'a review')} because "
                    "no evidence was cited"
                )

    missing = corrected.get("missing_mappings", [])
    if isinstance(missing, list):
        retained = []
        for mapping in missing:
            cited = mapping.get("evidence_ids", []) if isinstance(mapping, dict) else []
            if isinstance(cited, list) and cited and set(cited).issubset(known):
                retained.append(mapping)
            else:
                changes.append("Removed a missing-mapping proposal without valid evidence")
        corrected["missing_mappings"] = retained

    if not str(corrected.get("applicability_note", "")).strip():
        corrected["applicability_note"] = (
            "No additional applicability condition could be determined from the evidence."
        )
        changes.append("Filled an empty applicability note")
    if not str(corrected.get("challenge_comment", "")).strip():
        corrected["challenge_comment"] = (
            "No additional challenge can be supported by the retrieved evidence."
        )
        changes.append("Filled an empty challenge comment")
    return corrected, changes


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
        if not isinstance(review, dict):
            raise ValueError("Each mapping review must be an object")
        if review.get("decision") not in MAPPING_DECISIONS:
            raise ValueError(f"Invalid mapping decision: {review.get('decision')}")
        if not str(review.get("reason", "")).strip():
            raise ValueError("Each mapping review must contain a reason")
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
        if not isinstance(mapping, dict):
            raise ValueError("Each missing mapping must be an object")
        for field in ("instrument", "provision", "reason"):
            if not str(mapping.get(field, "")).strip():
                raise ValueError(f"Each missing mapping must contain {field}")
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
        if not isinstance(response[field], str) or not response[field].strip():
            raise ValueError(f"{field} must be non-empty text")


def run_review(
    item: AssessmentItem,
    evidence_provider: EvidenceProvider,
    llm: JsonLlm,
    system_prompt: str,
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

    user_prompt = _user_prompt(item, provisions, evidence)
    response = llm.generate_json(system_prompt, user_prompt)
    raw_attempts = [response]
    guardrail_changes: list[str] = []
    try:
        _validate_response(
            response,
            provisions,
            evidence,
            require_retrieved_evidence=True,
        )
    except ValueError as error:
        response = llm.generate_json(
            system_prompt,
            _repair_prompt(user_prompt, response, str(error)),
        )
        raw_attempts.append(response)
        try:
            _validate_response(
                response,
                provisions,
                evidence,
                require_retrieved_evidence=True,
            )
        except ValueError:
            response, guardrail_changes = _apply_evidence_guardrail(response, evidence)
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
        raw_attempts=raw_attempts,
        guardrail_changes=guardrail_changes,
        elapsed_seconds=round(time.perf_counter() - started, 3),
        prompt_version="agent-review-v0.2",
    )


def run_llm_only(
    item: AssessmentItem,
    llm: JsonLlm,
    system_prompt: str,
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
        raw_attempts=[response],
        guardrail_changes=[],
        elapsed_seconds=round(time.perf_counter() - started, 3),
        prompt_version="llm-only-v0.2",
    )


def write_run(run: ReviewRun, output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)

    run_record = {
        "item_id": run.item.item_id,
        "method": run.method,
        "evidence_provider": run.provider,
        "evidence_provider_details": run.provider_details,
        "workflow_version": "0.3",
        "prompt_version": run.prompt_version,
        "model": run.model,
        "model_settings": run.model_settings,
        "elapsed_seconds": run.elapsed_seconds,
        "model_attempts": len(run.raw_attempts),
        "guardrail_changes": run.guardrail_changes,
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
    if len(run.raw_attempts) > 1:
        (output / "raw_attempts.json").write_text(
            json.dumps(run.raw_attempts, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    with (output / "provision_checks.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "item_id",
            "instrument",
            "provision",
            "decision",
            "reason",
            "evidence_reference",
            "evidence_excerpt",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
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

    with (output / "item_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "item_id",
            "overall_assessment",
            "missing_mapping",
            "applicability_note",
            "challenge_comment",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
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
