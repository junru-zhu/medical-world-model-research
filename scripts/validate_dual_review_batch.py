#!/usr/bin/env python3
"""Validate one independent extraction and MedWM-Eval review batch."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from validate_provisional_new_records import ALLOWED, EXTRACTION_FIELDS, MEDWM_FIELDS


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--medwm", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    errors: list[str] = []

    _, records = read_rows(args.records)
    extraction_fields, extraction = read_rows(args.extraction)
    medwm_fields, medwm = read_rows(args.medwm)
    expected_ids = [row["candidate_id"] for row in records]
    expected_titles = {row["candidate_id"]: row["title"] for row in records}

    if extraction_fields != EXTRACTION_FIELDS:
        errors.append("Unexpected study-extraction field order")
    if medwm_fields != MEDWM_FIELDS:
        errors.append("Unexpected MedWM-Eval field order")
    for label, rows in (("extraction", extraction), ("medwm", medwm)):
        ids = [row.get("candidate_id", "") for row in rows]
        if ids != expected_ids:
            errors.append(f"{label}: candidate IDs or row order differ from records.csv")
        if len(ids) != len(set(ids)):
            errors.append(f"{label}: duplicate candidate IDs")
        for line, row in enumerate(rows, start=2):
            candidate_id = row.get("candidate_id", "")
            if row.get("title", "") != expected_titles.get(candidate_id):
                errors.append(f"{label}:{line}: title mismatch")
            blanks = [field for field in row if not row[field].strip()]
            if blanks:
                errors.append(f"{label}:{line}: blank fields {blanks}")

    for line, row in enumerate(extraction, start=2):
        if row.get("reviewer_confidence") not in {"high", "medium", "low"}:
            errors.append(
                f"extraction:{line}: invalid reviewer_confidence="
                f"{row.get('reviewer_confidence')!r}"
            )
    for line, row in enumerate(medwm, start=2):
        for field, allowed in ALLOWED.items():
            if row.get(field) not in allowed:
                errors.append(
                    f"medwm:{line}: invalid {field}={row.get(field)!r}"
                )

    result = {
        "status": "pass" if not errors else "fail",
        "records": len(expected_ids),
        "extraction_fields": len(extraction_fields),
        "medwm_fields": len(medwm_fields),
        "errors": errors,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
