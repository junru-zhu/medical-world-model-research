#!/usr/bin/env python3
"""Assemble all corrected novel empirical adjudications in canonical order."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from validate_provisional_new_records import (
    ALLOWED,
    EXTRACTION_FIELDS,
    MEDWM_ADJUDICATED_FIELDS,
)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def write_rows(
    path: Path, fields: list[str], rows: list[dict[str, str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--novel-empirical", type=Path, required=True)
    parser.add_argument("--completed-extraction", type=Path, required=True)
    parser.add_argument("--completed-medwm", type=Path, required=True)
    parser.add_argument("--dual-review-base", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    _, novel = read_rows(args.novel_empirical)
    extraction_fields, completed_extraction = read_rows(args.completed_extraction)
    medwm_fields, completed_medwm = read_rows(args.completed_medwm)
    if extraction_fields != EXTRACTION_FIELDS:
        raise ValueError("Completed extraction schema is unexpected")
    if medwm_fields != MEDWM_ADJUDICATED_FIELDS:
        raise ValueError("Completed MedWM-Eval schema is unexpected")

    extraction_by_id = {
        row["candidate_id"]: row for row in completed_extraction
    }
    medwm_by_id = {row["candidate_id"]: row for row in completed_medwm}
    manifest = json.loads(
        (args.dual_review_base / "manifest.json").read_text(encoding="utf-8")
    )
    for batch in manifest["batches"]:
        adjudication_dir = (
            args.dual_review_base / batch["batch"] / "adjudication"
        )
        current_extraction_fields, current_extraction = read_rows(
            adjudication_dir / "study-extraction-adjudicated.csv"
        )
        current_medwm_fields, current_medwm = read_rows(
            adjudication_dir / "medwm-eval-adjudicated.csv"
        )
        if current_extraction_fields != EXTRACTION_FIELDS:
            raise ValueError(f"{batch['batch']}: extraction schema mismatch")
        if current_medwm_fields != MEDWM_ADJUDICATED_FIELDS:
            raise ValueError(f"{batch['batch']}: MedWM schema mismatch")
        expected_ids = list(batch["candidate_ids"])
        if [row["candidate_id"] for row in current_extraction] != expected_ids:
            raise ValueError(f"{batch['batch']}: extraction order mismatch")
        if [row["candidate_id"] for row in current_medwm] != expected_ids:
            raise ValueError(f"{batch['batch']}: MedWM order mismatch")
        for row in current_extraction:
            if row["candidate_id"] in extraction_by_id:
                raise ValueError(f"Duplicate extraction ID: {row['candidate_id']}")
            extraction_by_id[row["candidate_id"]] = row
        for row in current_medwm:
            if row["candidate_id"] in medwm_by_id:
                raise ValueError(f"Duplicate MedWM ID: {row['candidate_id']}")
            medwm_by_id[row["candidate_id"]] = row

    expected_ids = [row["candidate_id"] for row in novel]
    if set(extraction_by_id) != set(expected_ids):
        raise ValueError("Assembled extraction candidate-ID set mismatch")
    if set(medwm_by_id) != set(expected_ids):
        raise ValueError("Assembled MedWM candidate-ID set mismatch")
    extraction = [extraction_by_id[candidate_id] for candidate_id in expected_ids]
    medwm = [medwm_by_id[candidate_id] for candidate_id in expected_ids]
    errors: list[str] = []
    for label, rows, fields in (
        ("extraction", extraction, EXTRACTION_FIELDS),
        ("medwm", medwm, MEDWM_ADJUDICATED_FIELDS),
    ):
        for line, row in enumerate(rows, start=2):
            allowed_blank = {"disagreement_fields"} if label == "medwm" else set()
            blanks = [
                field
                for field in fields
                if field not in allowed_blank and not row[field].strip()
            ]
            if blanks:
                errors.append(f"{label}:{line}: blank fields {blanks}")
    for line, row in enumerate(medwm, start=2):
        for field, allowed in ALLOWED.items():
            if row[field] not in allowed:
                errors.append(
                    f"medwm:{line}: invalid {field}={row[field]!r}"
                )

    write_rows(
        args.output_dir / "study-extraction-adjudicated.csv",
        EXTRACTION_FIELDS,
        extraction,
    )
    write_rows(
        args.output_dir / "medwm-eval-adjudicated.csv",
        MEDWM_ADJUDICATED_FIELDS,
        medwm,
    )
    result = {
        "status": "pass" if not errors else "fail",
        "records": len(expected_ids),
        "completed_prior_sample": len(completed_extraction),
        "completed_current_batches": len(expected_ids) - len(completed_extraction),
        "errors": errors,
    }
    (args.output_dir / "validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
