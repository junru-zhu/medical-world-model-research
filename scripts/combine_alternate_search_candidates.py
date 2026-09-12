#!/usr/bin/env python3
"""Combine primary-search misses and fresh alternate-query records for screening."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "audit_id",
    "route",
    "title",
    "abstract",
    "authors",
    "year",
    "publication_date",
    "venue",
    "doi",
    "arxiv_id",
    "url",
    "record_type",
    "sources",
    "query_labels",
    "source_status",
    "original_exclusion_reason",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-misses", type=Path, required=True)
    parser.add_argument("--fresh-search", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    combined: list[dict[str, str]] = []
    for route, path in [
        ("primary_search_alternate_filter", args.primary_misses),
        ("fresh_alternate_public_search", args.fresh_search),
    ]:
        for row in read(path):
            combined.append(
                {
                    "audit_id": row["audit_id"],
                    "route": route,
                    "title": row.get("title", ""),
                    "abstract": row.get("abstract", ""),
                    "authors": row.get("authors", ""),
                    "year": row.get("year", ""),
                    "publication_date": row.get("publication_date", ""),
                    "venue": row.get("venue", ""),
                    "doi": row.get("doi", ""),
                    "arxiv_id": row.get("arxiv_id", ""),
                    "url": row.get("url", ""),
                    "record_type": row.get("record_type", ""),
                    "sources": row.get("sources", ""),
                    "query_labels": row.get("query_labels", ""),
                    "source_status": row.get("source_status", ""),
                    "original_exclusion_reason": row.get(
                        "original_exclusion_reason", ""
                    ),
                }
            )
    ids = [row["audit_id"] for row in combined]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate audit IDs across alternate-search routes.")
    combined.sort(key=lambda row: (row["route"], row["title"].lower()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(combined)
    summary = {
        "records": len(combined),
        "primary_search_alternate_filter": sum(
            row["route"] == "primary_search_alternate_filter"
            for row in combined
        ),
        "fresh_alternate_public_search": sum(
            row["route"] == "fresh_alternate_public_search"
            for row in combined
        ),
    }
    (args.output.parent / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
