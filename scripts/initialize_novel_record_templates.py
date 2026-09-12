#!/usr/bin/env python3
"""Create provisional extraction/coding templates for newly merged records."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merged", type=Path, required=True)
    parser.add_argument("--existing-included", type=Path, required=True)
    parser.add_argument("--existing-extraction", type=Path, required=True)
    parser.add_argument("--existing-medwm", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    merged_fields, merged = read(args.merged)
    _, existing_included = read(args.existing_included)
    extraction_fields, extraction = read(args.existing_extraction)
    medwm_fields, medwm = read(args.existing_medwm)
    existing_ids = {row["candidate_id"] for row in existing_included}
    if existing_ids != {row["candidate_id"] for row in extraction} | {
        row["candidate_id"] for row in medwm
    } | {
        row["candidate_id"]
        for row in existing_included
        if row["final_corpus_type"] == "review"
    }:
        raise ValueError("Existing corpus, extraction, and coding IDs are inconsistent.")
    novel = [row for row in merged if row["candidate_id"] not in existing_ids]
    novel_empirical = [
        row for row in novel if row["final_corpus_type"] == "empirical"
    ]
    novel_reviews = [
        row for row in novel if row["final_corpus_type"] == "review"
    ]

    extraction_template: list[dict[str, str]] = []
    medwm_template: list[dict[str, str]] = []
    for row in novel_empirical:
        extraction_row = {field: "" for field in extraction_fields}
        extraction_row["candidate_id"] = row["candidate_id"]
        extraction_row["title"] = row["title"]
        if "primary_source_url" in extraction_row:
            extraction_row["primary_source_url"] = row.get("url", "")
        if "source_status" in extraction_row:
            extraction_row["source_status"] = row.get("source_status", "")
        extraction_template.append(extraction_row)

        medwm_row = {field: "" for field in medwm_fields}
        medwm_row["candidate_id"] = row["candidate_id"]
        medwm_row["title"] = row["title"]
        medwm_template.append(medwm_row)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / "novel-empirical.csv", novel_empirical, merged_fields)
    write(args.output_dir / "novel-reviews.csv", novel_reviews, merged_fields)
    write(
        args.output_dir / "study-extraction-template.csv",
        extraction_template,
        extraction_fields,
    )
    write(
        args.output_dir / "medwm-eval-template.csv",
        medwm_template,
        medwm_fields,
    )
    summary = {
        "merged_records": len(merged),
        "existing_included_ids": len(existing_ids),
        "novel_records": len(novel),
        "novel_empirical": len(novel_empirical),
        "novel_reviews": len(novel_reviews),
        "status": "provisional_templates_not_completed_extraction",
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
