#!/usr/bin/env python3
"""Build a field-level adjudication sheet for two study extractions."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


IDENTITY_FIELDS = {"candidate_id", "title"}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {path}")
        return list(reader.fieldnames), list(reader)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    fields_a, rows_a = read_rows(args.reviewer_a)
    fields_b, rows_b = read_rows(args.reviewer_b)
    if fields_a != fields_b:
        raise ValueError("Reviewer schemas differ.")
    if len(rows_a) != len(rows_b):
        raise ValueError("Reviewer row counts differ.")

    comparison_fields = [field for field in fields_a if field not in IDENTITY_FIELDS]
    output_rows: list[dict[str, str]] = []
    field_summary: dict[str, dict[str, int]] = {
        field: {"exact_agreement": 0, "normalized_agreement": 0, "differences": 0}
        for field in comparison_fields
    }
    records_with_difference: set[str] = set()

    for index, (row_a, row_b) in enumerate(zip(rows_a, rows_b, strict=True), start=2):
        if row_a["candidate_id"] != row_b["candidate_id"]:
            raise ValueError(f"Candidate ID mismatch at row {index}")
        if row_a["title"] != row_b["title"]:
            raise ValueError(f"Title mismatch at row {index}")
        for field in comparison_fields:
            value_a = row_a[field]
            value_b = row_b[field]
            if value_a == value_b:
                field_summary[field]["exact_agreement"] += 1
                field_summary[field]["normalized_agreement"] += 1
                continue
            if normalized(value_a) == normalized(value_b):
                field_summary[field]["normalized_agreement"] += 1
                continue
            field_summary[field]["differences"] += 1
            records_with_difference.add(row_a["candidate_id"])
            output_rows.append(
                {
                    "candidate_id": row_a["candidate_id"],
                    "title": row_a["title"],
                    "field": field,
                    "reviewer_a": value_a,
                    "reviewer_b": value_b,
                    "adjudicated_value": "",
                    "adjudication_notes": "",
                }
            )

    total_decisions = len(rows_a) * len(comparison_fields)
    summary: dict[str, Any] = {
        "records": len(rows_a),
        "comparison_fields": len(comparison_fields),
        "field_decisions": total_decisions,
        "differences": len(output_rows),
        "records_with_difference": len(records_with_difference),
        "field_summary": field_summary,
        "interpretation": (
            "Narrative wording differences are expected and are not reliability "
            "statistics. Every listed field requires source-grounded adjudication."
        ),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "adjudication-required.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        fieldnames = [
            "candidate_id",
            "title",
            "field",
            "reviewer_a",
            "reviewer_b",
            "adjudicated_value",
            "adjudication_notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    (args.output_dir / "comparison-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: summary[key] for key in summary if key != "field_summary"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
