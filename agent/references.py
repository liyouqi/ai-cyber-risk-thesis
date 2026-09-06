"""Parse the article formats used by the two experiment workbooks."""

from __future__ import annotations

import re

from agent.models import ProvisionRef


DORA_LEVEL_1 = "Regulation (EU) 2022/2554"


def _article_refs(text: str, instrument: str) -> list[ProvisionRef]:
    text = text.strip().replace("–", "-")
    if text.casefold().startswith("annex "):
        return [ProvisionRef(instrument, text)]

    match = re.fullmatch(r"(?:Articles|Article|Art\.)\s*(.+)", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Unsupported provision format: {text}")
    body = match.group(1).strip()

    article_range = re.fullmatch(r"(\d+)-(\d+)", body)
    if article_range:
        start, end = map(int, article_range.groups())
        if end < start or end - start > 20:
            raise ValueError(f"Invalid article range: {text}")
        return [ProvisionRef(instrument, f"Article {number}") for number in range(start, end + 1)]

    article = re.match(r"(\d+)(.*)", body)
    if not article:
        raise ValueError(f"Missing article number: {text}")
    number, suffix = article.groups()
    suffix = suffix.strip()
    if not suffix:
        return [ProvisionRef(instrument, f"Article {number}")]

    if re.search(r"\)\s*[,\-]\s*\(", suffix):
        groups = re.findall(r"\(([^()]*)\)", suffix)
        if groups and all(group.isdigit() for group in groups):
            if "-" in suffix and len(groups) == 2:
                start, end = map(int, groups)
                if end >= start and end - start <= 20:
                    return [
                        ProvisionRef(instrument, f"Article {number}({paragraph})")
                        for paragraph in range(start, end + 1)
                    ]
            return [
                ProvisionRef(instrument, f"Article {number}({paragraph})")
                for paragraph in groups
            ]

    return [ProvisionRef(instrument, f"Article {number}{suffix}")]


def parse_mapping(mapping: str, default_instrument: str) -> list[ProvisionRef]:
    """Split one workbook mapping into individually reviewable provisions."""
    normalized = mapping.replace("–", "-")
    parts: list[str] = []
    for semicolon_part in normalized.split(";"):
        parts.extend(re.split(r",\s*together with\s+", semicolon_part, flags=re.IGNORECASE))

    references: list[ProvisionRef] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        instrument = default_instrument
        if part.casefold().startswith("dora article"):
            instrument = DORA_LEVEL_1
            part = part[5:].strip()

        annex_parts = re.split(r"\s*&\s*(?=Annex\s+)", part, flags=re.IGNORECASE)
        for annex_part in annex_parts:
            references.extend(_article_refs(annex_part.strip(), instrument))

    if not references:
        raise ValueError(f"No provisions found in mapping: {mapping}")
    return references
