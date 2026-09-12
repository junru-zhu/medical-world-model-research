#!/usr/bin/env python3
"""Validate and merge disjoint study-extraction batches in canonical order."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--included",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/"
            "screening/fulltext-adjudicated/included.csv"
        ),
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/screening/extraction"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/study-extraction.csv"
        ),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/"
            "study-extraction-completeness.json"
        ),
    )
    parser.add_argument("--allow-incomplete", action="store_true")
    return parser.parse_args()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return reader.fieldnames, list(reader)


def main() -> int:
    args = parse_args()
    _, included_rows = read_csv(args.included)
    empirical = [
        row for row in included_rows if row["final_corpus_type"] == "empirical"
    ]
    canonical_ids = [row["candidate_id"] for row in empirical]

    batch_paths = sorted(args.batch_dir.glob("extraction-batch-*.csv"))
    if not batch_paths:
        raise ValueError(f"No extraction batches found in {args.batch_dir}")

    expected_fields: list[str] | None = None
    extracted: dict[str, dict[str, str]] = {}
    batch_counts: dict[str, int] = {}
    for path in batch_paths:
        fields, rows = read_csv(path)
        if expected_fields is None:
            expected_fields = fields
        elif fields != expected_fields:
            raise ValueError(f"Schema mismatch in {path}")
        batch_counts[path.name] = len(rows)
        for row in rows:
            candidate_id = row["candidate_id"]
            if candidate_id in extracted:
                raise ValueError(f"Duplicate extracted candidate: {candidate_id}")
            extracted[candidate_id] = row

    if expected_fields is None:
        raise AssertionError("Unreachable: no extraction schema.")

    missing_ids = [candidate_id for candidate_id in canonical_ids if candidate_id not in extracted]
    unexpected_ids = sorted(set(extracted) - set(canonical_ids))
    ordered_rows = [extracted[candidate_id] for candidate_id in canonical_ids if candidate_id in extracted]

    blank_counts = {
        field: sum(not row[field].strip() for row in ordered_rows)
        for field in expected_fields
    }
    marker_counts = {
        field: dict(
            sorted(
                Counter(
                    row[field].strip()
                    for row in ordered_rows
                    if row[field].strip() in {"NI", "NA"}
                ).items()
            )
        )
        for field in expected_fields
    }
    marker_counts = {field: counts for field, counts in marker_counts.items() if counts}
    incomplete_rows = [
        row["candidate_id"]
        for row in ordered_rows
        if any(
            not row[field].strip()
            for field in expected_fields
            if field not in {"appraisal_strengths", "appraisal_limitations"}
        )
    ]

    report = {
        "expected_empirical_records": len(canonical_ids),
        "merged_records": len(ordered_rows),
        "batch_counts": batch_counts,
        "missing_candidate_ids": missing_ids,
        "unexpected_candidate_ids": unexpected_ids,
        "blank_counts_by_field": blank_counts,
        "ni_na_counts_by_field": marker_counts,
        "rows_with_blank_required_fields": incomplete_rows,
        "status": (
            "complete"
            if not missing_ids and not unexpected_ids and not incomplete_rows
            else "incomplete"
        ),
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=expected_fields)
        writer.writeheader()
        writer.writerows(ordered_rows)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.allow_incomplete:
        return 0
    return 0 if report["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
