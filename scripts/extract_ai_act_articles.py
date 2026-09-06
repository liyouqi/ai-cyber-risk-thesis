"""Extract article paragraphs from a downloaded EUR-Lex AI Act HTML file."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning


SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689"


def extract(source: Path) -> dict[str, object]:
    raw = source.read_bytes()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(raw, "lxml")
    chunks: list[dict[str, str]] = []
    for article in soup.select("div.eli-subdivision[id^=art_]"):
        match = re.fullmatch(r"art_(\d+)", str(article.get("id", "")))
        if not match:
            continue
        article_number = int(match.group(1))
        title_node = article.select_one("div.eli-title")
        title = " ".join(title_node.stripped_strings) if title_node else ""
        paragraph_number = 0
        for child in article.find_all("div", recursive=False):
            child_id = str(child.get("id", ""))
            paragraph_match = re.fullmatch(r"\d{3}\.(\d{3})", child_id)
            if not paragraph_match:
                continue
            paragraph_number = int(paragraph_match.group(1))
            text = " ".join(child.stripped_strings)
            chunks.append(
                {
                    "evidence_id": (
                        f"eu-2024-1689-article-{article_number}-{paragraph_number}"
                    ),
                    "instrument": "Regulation (EU) 2024/1689",
                    "provision": f"Article {article_number}({paragraph_number})",
                    "text": f"Article {article_number} — {title}. {text}",
                    "source": f"{SOURCE_URL}#art_{article_number}",
                }
            )
    if not chunks:
        raise ValueError("No AI Act article paragraphs found")
    return {
        "document": "Regulation (EU) 2024/1689",
        "celex": "32024R1689",
        "source_url": SOURCE_URL,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "chunks": chunks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = extract(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(data['chunks'])} legal-text chunks to {args.output}")


if __name__ == "__main__":
    main()
