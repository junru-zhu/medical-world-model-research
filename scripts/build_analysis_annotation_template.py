#!/usr/bin/env python3
"""Build a reviewable analysis-annotation ledger for a merged corpus."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "candidate_id",
    "title",
    "domain_group",
    "corpus_boundary",
    "source_tier",
    "annotation_status",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--included", type=Path, required=True)
    parser.add_argument("--existing-annotations", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    included = [
        row
        for row in read(args.included)
        if row["final_corpus_type"] == "empirical"
    ]
    existing: dict[str, dict[str, str]] = {}
    if args.existing_annotations:
        existing = {
            row["candidate_id"]: row
            for row in read(args.existing_annotations)
        }

    rows: list[dict[str, str]] = []
    for study in included:
        prior = existing.get(study["candidate_id"], {})
        complete = all(
            prior.get(field, "").strip()
            for field in ("domain_group", "corpus_boundary", "source_tier")
        )
        rows.append(
            {
                "candidate_id": study["candidate_id"],
                "title": study["title"],
                "domain_group": prior.get("domain_group", ""),
                "corpus_boundary": prior.get("corpus_boundary", ""),
                "source_tier": prior.get("source_tier", ""),
                "annotation_status": (
                    "carried_forward" if complete else "needs_review"
                ),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "empirical_records": len(rows),
        "carried_forward": sum(
            row["annotation_status"] == "carried_forward" for row in rows
        ),
        "needs_review": sum(
            row["annotation_status"] == "needs_review" for row in rows
        ),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
