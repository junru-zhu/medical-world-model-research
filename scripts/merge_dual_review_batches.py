#!/usr/bin/env python3
"""Merge validated, disjoint corrected-record review batches."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


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
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument(
        "--reviewer", choices=("reviewer-a", "reviewer-b"), required=True
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads((args.base / "manifest.json").read_text(encoding="utf-8"))
    extraction_fields: list[str] | None = None
    medwm_fields: list[str] | None = None
    extraction_rows: list[dict[str, str]] = []
    medwm_rows: list[dict[str, str]] = []
    expected_ids: list[str] = []

    for batch in manifest["batches"]:
        batch_dir = args.base / batch["batch"]
        ids = list(batch["candidate_ids"])
        expected_ids.extend(ids)
        current_extraction_fields, current_extraction = read_rows(
            batch_dir / args.reviewer / "study-extraction.csv"
        )
        current_medwm_fields, current_medwm = read_rows(
            batch_dir / args.reviewer / "medwm-eval.csv"
        )
        if extraction_fields is None:
            extraction_fields = current_extraction_fields
            medwm_fields = current_medwm_fields
        if (
            current_extraction_fields != extraction_fields
            or current_medwm_fields != medwm_fields
        ):
            raise ValueError(f"Inconsistent schema in {batch['batch']}")
        if [row["candidate_id"] for row in current_extraction] != ids:
            raise ValueError(f"Extraction order mismatch in {batch['batch']}")
        if [row["candidate_id"] for row in current_medwm] != ids:
            raise ValueError(f"MedWM-Eval order mismatch in {batch['batch']}")
        extraction_rows.extend(current_extraction)
        medwm_rows.extend(current_medwm)

    if extraction_fields is None or medwm_fields is None:
        raise ValueError("Manifest contains no batches")
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("Manifest contains duplicate candidate IDs")
    write_rows(
        args.output_dir / f"study-extraction-{args.reviewer}.csv",
        extraction_fields,
        extraction_rows,
    )
    write_rows(
        args.output_dir / f"medwm-eval-{args.reviewer}.csv",
        medwm_fields,
        medwm_rows,
    )
    summary = {
        "reviewer": args.reviewer,
        "records": len(expected_ids),
        "batches": len(manifest["batches"]),
        "candidate_ids_unique": True,
    }
    (args.output_dir / f"merge-{args.reviewer}.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
