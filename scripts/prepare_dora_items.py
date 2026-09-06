"""Extract the DORA KPI workbook into the common experiment format."""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import load_workbook


SOURCE = Path("source_files/DORA KPI.xlsx")
OUTPUT = Path("experiments/data/candidates/dora.csv")
SHEET = "Sheet1"

INSTRUMENT_ROWS = {
    1: "Regulation (EU) 2022/2554",
    13: "Commission Delegated Regulation (EU) 2025/301",
    21: "Commission Delegated Regulation (EU) 2024/1774",
    28: "Commission Delegated Regulation (EU) 2024/1773",
}

TRANSLATIONS = {
    3: (
        "ICT risk management framework review",
        "Review at least once a year; also review following a major ICT incident, a supervisory instruction or a finding from testing",
    ),
    4: (
        "ICT business continuity testing",
        "Test the ICT business continuity plans and response and recovery plans at least once a year; also test them following a major change to a critical or important function",
    ),
    5: (
        "Crisis communication testing",
        "Include communication plans in ICT business continuity testing, but there is no uniform timing requirement",
    ),
    6: (
        "General digital operational resilience testing",
        "Test all ICT systems and applications supporting critical or important functions appropriately at least once a year",
    ),
    7: (
        "ICT third-party register reporting",
        "Report at least yearly to the competent authority the number of new ICT service arrangements, the categories of providers, the types of contracts and the functions supported",
    ),
    8: (
        "Management body training",
        "Members of the management body should regularly receive training on ICT risk and digital operational resilience, but no uniform number of sessions or hours is specified",
    ),
    9: (
        "Staff training",
        "ICT security and digital operational resilience training should be mandatory, but no minimum number of training hours per year is specified",
    ),
    10: (
        "Major ICT-related incident reporting",
        "Initial notification, an intermediate report and a final report are required; the specific four-hour, 24-hour and 72-hour deadlines are specified by RTS 2025/301",
    ),
    11: (
        "Penalty for a critical ICT provider",
        "If a critical ICT third-party service provider does not cooperate with oversight, a daily penalty of up to 1% of its average daily worldwide turnover in the preceding business year may be imposed for no more than six months",
    ),
    15: (
        "Initial notification",
        "Submit within four hours after classification as a major incident and no later than 24 hours after first becoming aware of the incident",
    ),
    16: (
        "Late classification",
        "If the incident is classified as major more than 24 hours after it was first known, submit within four hours after classification",
    ),
    17: (
        "Intermediate report",
        "Submit within 72 hours after the initial notification, even if the incident status or handling has not changed",
    ),
    18: (
        "Updated intermediate report",
        "Submit without undue delay after regular activities have recovered, when the incident status changes materially, or when the competent authority requests it",
    ),
    19: (
        "Final report",
        "Submit no later than one month after the intermediate report or the latest updated intermediate report",
    ),
    23: (
        "Vulnerability scanning and assessment",
        "Perform automated vulnerability scanning and assessment at least weekly for ICT assets supporting critical or important functions",
    ),
    24: (
        "Access rights review for ordinary systems",
        "At least once a year",
    ),
    25: (
        "Access rights review for systems supporting critical or important functions",
        "At least once every six months",
    ),
    26: (
        "ICT business continuity plan testing",
        "At least once a year, taking into account severe but plausible scenarios",
    ),
    30: (
        "Review of the policy on the use of ICT third-party services",
        "At least once a year",
    ),
    31: (
        "Independent review of critical or important ICT services",
        "Include it in the audit plan; determine the audit frequency based on risk, with no uniform requirement for an annual audit",
    ),
    32: (
        "Provider performance and risk monitoring",
        "Perform continuously; there is no requirement to perform it monthly or quarterly",
    ),
    33: (
        "Exit plan testing",
        "Test periodically based on risk and criticality, but no uniform annual frequency is specified",
    ),
}


def text(value: object) -> str:
    return "" if value is None else str(value).strip()


def main() -> None:
    workbook = load_workbook(SOURCE, read_only=True, data_only=True)
    try:
        sheet = workbook[SHEET]
        rows = []
        instrument = ""
        item_number = 0

        for row_number in range(1, sheet.max_row + 1):
            if row_number in INSTRUMENT_ROWS:
                instrument = INSTRUMENT_ROWS[row_number]
                continue

            domain = text(sheet.cell(row_number, 1).value)
            statement = text(sheet.cell(row_number, 2).value)
            mapping = text(sheet.cell(row_number, 3).value)
            if not instrument or not domain or not statement or not mapping:
                continue
            if not (mapping.startswith("Article") or mapping.startswith("DORA Article")):
                continue

            try:
                domain, statement = TRANSLATIONS[row_number]
            except KeyError as exc:
                raise ValueError(f"Missing English translation for source row {row_number}") from exc
            if row_number == 26:
                mapping = "Article 26, together with DORA Article 11(6)"

            item_number += 1
            rows.append(
                {
                    "item_id": f"DORA-{item_number:02d}",
                    "framework": "DORA",
                    "instrument": instrument,
                    "domain": domain,
                    "control_statement": statement,
                    "expected_evidence": "",
                    "applicability": "",
                    "existing_mapping": mapping,
                    "source_row": row_number,
                }
            )
    finally:
        workbook.close()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} items to {OUTPUT}")


if __name__ == "__main__":
    main()
