#!/usr/bin/env python3
"""Generate a numbered reference ledger for all included review records."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from reference_overrides import apply_reference_override


REVIEW_ORDER = ["MWM-0234", "MWM-0117", "MWM-0116"]


def format_reference(number: int, row: dict[str, str]) -> str:
    row = apply_reference_override(row)
    author_parts = [
        author.strip()
        for author in row["authors"].split(";")
        if author.strip() and author.strip() != ":"
    ]
    if len(author_parts) > 6:
        authors = ", ".join(author_parts[:6]) + ", et al"
    else:
        authors = ", ".join(author_parts)
    doi = row["doi"].strip()
    venue = (
        "arXiv preprint"
        if row["arxiv_id"].strip()
        and doi.casefold().startswith("10.48550/")
        and not row.get("booktitle", "").strip()
        else (
            row.get("venue", "").strip()
            or row.get("booktitle", "").strip()
            or row["record_type"]
        )
    )
    locator = (
        f"doi:{doi}"
        if doi
        else (
            row["url"]
            if row.get("booktitle", "").strip() and row["url"].strip()
            else (
                f"arXiv:{row['arxiv_id']}"
                if row["arxiv_id"].strip()
                else row["url"]
            )
        )
    )
    volume = row.get("volume", "").strip()
    issue = row.get("issue", "").strip()
    pages = row.get("pages", "").strip().replace("--", "-")
    article_number = row.get("article_number", "").strip()
    publication = row["year"]
    if volume:
        publication += f";{volume}"
        if issue:
            publication += f"({issue})"
        if pages or article_number:
            publication += f":{pages or article_number}"
    elif pages:
        publication += f":{pages}"
    note = row.get("note", "").strip()
    suffix = f" {locator}." if locator else ""
    if note:
        suffix += f" {note.rstrip('.')}."
    return (
        f"{number}. {authors.rstrip('.')}. {row['title'].rstrip('.')}. "
        f"*{venue}*. {publication}.{suffix}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--included", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    with args.included.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["candidate_id"]: row for row in rows}
    review_rows = [
        row for row in rows if row["final_corpus_type"] == "review"
    ]
    priority_reviews = [
        by_id[candidate_id]
        for candidate_id in REVIEW_ORDER
        if candidate_id in by_id
        and by_id[candidate_id]["final_corpus_type"] == "review"
    ]
    priority_ids = {row["candidate_id"] for row in priority_reviews}
    additional_reviews = sorted(
        [
            row
            for row in review_rows
            if row["candidate_id"] not in priority_ids
        ],
        key=lambda row: (
            row.get("year", ""),
            row.get("publication_date", ""),
            row["title"].casefold(),
        ),
    )
    reviews = priority_reviews + additional_reviews
    empirical = [
        row for row in rows if row["final_corpus_type"] == "empirical"
    ]
    ordered = reviews + empirical

    mapping = {
        row["candidate_id"]: {
            "number": index,
            "title": apply_reference_override(row)["title"],
            "url": apply_reference_override(row)["url"],
        }
        for index, row in enumerate(ordered, start=1)
    }
    lines = ["# Included-Study Reference Ledger", ""]
    lines.extend(
        format_reference(index, row)
        for index, row in enumerate(ordered, start=1)
    )
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    args.output_json.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(ordered)} references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
