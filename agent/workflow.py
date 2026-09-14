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


COVERAGE_DECISIONS = {"Yes", "No"}


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
        # Keep Direct requests as canonical legal citations so Regulatory RAG's
        # own citation parser can resolve the provision deterministically.  The
        # control statement belongs in the later LLM assessment prompt, not in
        # the citation lookup query.
        citation_names = {
            "Regulation (EU) 2024/1689": "AI Act",
            "Regulation (EU) 2022/2554": "DORA",
        }
        instrument = citation_names.get(provision.instrument, provision.instrument)
        return f"{instrument} {provision.provision}"
    scope = (
        "DORA and its related delegated regulations"
        if item.framework == "DORA"
        else item.instrument
    )
    return (
        f"Within {scope}, which important provision is materially necessary for "
        f"this requirement but absent from the existing mapping: "
        f"{item.control_statement}"
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
    existing_mapping_evidence: list[Evidence],
    gap_search_evidence: list[Evidence] | None = None,
) -> str:
    data = {
        "assessment_item": item.as_dict(),
        "existing_provisions_to_review": [entry.as_dict() for entry in provisions],
        "existing_mapping_evidence": [
            entry.as_dict() for entry in existing_mapping_evidence
        ],
        "gap_search_evidence": [
            entry.as_dict() for entry in (gap_search_evidence or [])
        ],
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

    cited = corrected.get("evidence_ids", [])
    valid = (
        [evidence_id for evidence_id in cited if evidence_id in known]
        if isinstance(cited, list)
        else []
    )
    if valid != cited:
        corrected["evidence_ids"] = valid
        changes.append("Removed unknown evidence IDs from the coverage decision")
    if corrected.get("coverage") == "Yes" and not valid:
        corrected["coverage"] = "No"
        corrected["reason"] = "The retrieved evidence was insufficient to confirm coverage."
        changes.append("Changed an uncited Yes coverage decision to No")

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
        "coverage",
        "reason",
        "evidence_ids",
        "missing_mappings",
        "applicability_note",
        "challenge_comment",
    }
    if not required.issubset(response):
        missing = ", ".join(sorted(required - response.keys()))
        raise ValueError(f"LLM output is missing fields: {missing}")

    evidence_ids = {entry.evidence_id for entry in evidence}
    if response["coverage"] not in COVERAGE_DECISIONS:
        raise ValueError("coverage must be Yes or No")
    if not str(response["reason"]).strip():
        raise ValueError("reason must be non-empty text")
    cited = response["evidence_ids"]
    if not isinstance(cited, list):
        raise ValueError("evidence_ids must be a list")
    if require_retrieved_evidence and not set(cited).issubset(evidence_ids):
        raise ValueError("The coverage decision cites an unknown evidence ID")
    if require_retrieved_evidence and response["coverage"] == "Yes" and not cited:
        raise ValueError("A Yes coverage decision must cite retrieved evidence")
    if not require_retrieved_evidence and cited:
        raise ValueError("LLM-only output must not invent retrieved evidence IDs")

    missing_mappings = response["missing_mappings"]
    if not isinstance(missing_mappings, list):
        raise ValueError("missing_mappings must be a list")
    if response["coverage"] == "Yes" and missing_mappings:
        raise ValueError("A Yes coverage decision cannot contain missing mappings")
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
    initial_provider_details = getattr(evidence_provider, "metadata", {})
    retrieval_start = len(initial_provider_details.get("retrievals", []))
    provisions = parse_mapping(item.existing_mapping, item.instrument)
    queries: list[dict[str, str]] = []
    validation_evidence: list[Evidence] = []

    for provision in provisions:
        query = _query(item, provision)
        queries.append(
            {
                "purpose": "validate",
                "query_mode": "direct",
                "provision": provision.provision,
                "query": query,
            }
        )
        validation_evidence.extend(evidence_provider.retrieve(item, query, provision))

    gap_query = _query(item, None)
    queries.append(
        {
            "purpose": "gap",
            "query_mode": "planned",
            "provision": "",
            "query": gap_query,
        }
    )
    gap_evidence = evidence_provider.retrieve(item, gap_query, None)
    validation_evidence = _deduplicate(validation_evidence)
    gap_evidence = _deduplicate(gap_evidence)
    evidence = _deduplicate(validation_evidence + gap_evidence)

    user_prompt = _user_prompt(item, provisions, validation_evidence, gap_evidence)
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
    provider_details = copy.deepcopy(getattr(evidence_provider, "metadata", {}))
    if isinstance(provider_details.get("retrievals"), list):
        provider_details["retrievals"] = provider_details["retrievals"][
            retrieval_start:
        ]
    return ReviewRun(
        item=item,
        method=(
            "development_replay"
            if evidence_provider.name == "development-replay"
            else "agentic_rag"
        ),
        provider=evidence_provider.name,
        provider_details=provider_details,
        model=llm.model,
        model_settings=getattr(llm, "metadata", {"model": llm.model}),
        provisions=provisions,
        queries=queries,
        evidence=evidence,
        response=response,
        raw_attempts=raw_attempts,
        guardrail_changes=guardrail_changes,
        elapsed_seconds=round(time.perf_counter() - started, 3),
        prompt_version="agent-review-v0.5",
    )


def run_llm_only(
    item: AssessmentItem,
    llm: JsonLlm,
    system_prompt: str,
) -> ReviewRun:
    """Review one item with model knowledge only and no retrieved evidence."""
    started = time.perf_counter()
    provisions = parse_mapping(item.existing_mapping, item.instrument)
    user_prompt = _user_prompt(item, provisions, [])
    response = llm.generate_json(system_prompt, user_prompt)
    raw_attempts = [response]
    try:
        _validate_response(
            response,
            provisions,
            [],
            require_retrieved_evidence=False,
        )
    except ValueError as error:
        response = llm.generate_json(
            system_prompt,
            _repair_prompt(user_prompt, response, str(error)),
        )
        raw_attempts.append(response)
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
        raw_attempts=raw_attempts,
        guardrail_changes=[],
        elapsed_seconds=round(time.perf_counter() - started, 3),
        prompt_version="llm-only-v0.4",
    )


def write_run(run: ReviewRun, output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)

    run_record = {
        "item_id": run.item.item_id,
        "method": run.method,
        "evidence_provider": run.provider,
        "evidence_provider_details": run.provider_details,
        "workflow_version": "0.7" if run.method == "agentic_rag" else "0.4",
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

    with (output / "item_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "item_id",
            "coverage",
            "reason",
            "missing_mapping",
            "evidence_reference",
            "evidence_excerpt",
            "applicability_note",
            "challenge_comment",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        cited = run.response.get("evidence_ids", [])
        by_id = {entry.evidence_id: entry for entry in run.evidence}
        writer.writerow(
            {
                "item_id": run.item.item_id,
                "coverage": run.response["coverage"],
                "reason": run.response["reason"],
                "missing_mapping": json.dumps(
                    run.response["missing_mappings"], ensure_ascii=False
                ),
                "evidence_reference": "; ".join(cited),
                "evidence_excerpt": " | ".join(
                    by_id[evidence_id].text[:300]
                    for evidence_id in cited
                    if evidence_id in by_id
                ),
                "applicability_note": run.response["applicability_note"],
                "challenge_comment": run.response["challenge_comment"],
            }
        )
    return output
