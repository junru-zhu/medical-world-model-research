#!/usr/bin/env python3
"""Audit the PhysioNet 2019 training cohorts and freeze a data fingerprint."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_COLUMNS = [
    "HR",
    "O2Sat",
    "Temp",
    "SBP",
    "MAP",
    "DBP",
    "Resp",
    "EtCO2",
    "BaseExcess",
    "HCO3",
    "FiO2",
    "pH",
    "PaCO2",
    "SaO2",
    "AST",
    "BUN",
    "Alkalinephos",
    "Calcium",
    "Chloride",
    "Creatinine",
    "Bilirubin_direct",
    "Glucose",
    "Lactate",
    "Magnesium",
    "Phosphate",
    "Potassium",
    "Bilirubin_total",
    "TroponinI",
    "Hct",
    "Hgb",
    "PTT",
    "WBC",
    "Fibrinogen",
    "Platelets",
    "Age",
    "Gender",
    "Unit1",
    "Unit2",
    "HospAdmTime",
    "ICULOS",
    "SepsisLabel",
]
DYNAMIC_COLUMNS = EXPECTED_COLUMNS[:34]
STATIC_COLUMNS = EXPECTED_COLUMNS[34:39]
EXPECTED_PATIENT_COUNTS = {"A": 20336, "B": 20000}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_cohort(root: Path, cohort: str) -> dict[str, Any]:
    cohort_dir = root / "training" / f"training_set{cohort}"
    files = sorted(cohort_dir.glob("*.psv"))
    nonmissing = Counter({column: 0 for column in EXPECTED_COLUMNS})
    total_rows = 0
    row_counts: list[int] = []
    septic_patients = 0
    septic_rows = 0
    invalid_headers: list[str] = []
    malformed_rows: list[str] = []
    nonmonotonic_iculos: list[str] = []
    changing_static: list[str] = []
    aggregate_digest = hashlib.sha256()

    for path in files:
        raw = path.read_bytes()
        file_digest = hashlib.sha256(raw).hexdigest()
        relative = path.relative_to(root).as_posix()
        aggregate_digest.update(relative.encode("utf-8"))
        aggregate_digest.update(b"\0")
        aggregate_digest.update(str(len(raw)).encode("ascii"))
        aggregate_digest.update(b"\0")
        aggregate_digest.update(file_digest.encode("ascii"))
        aggregate_digest.update(b"\n")

        reader = csv.reader(io.StringIO(raw.decode("utf-8")), delimiter="|")
        try:
            header = next(reader)
        except StopIteration:
            malformed_rows.append(f"{relative}:empty")
            continue
        if header != EXPECTED_COLUMNS:
            invalid_headers.append(relative)
            continue

        patient_rows = 0
        patient_septic = False
        previous_iculos: float | None = None
        static_reference: dict[int, str] = {}
        static_changed = False
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(EXPECTED_COLUMNS):
                malformed_rows.append(f"{relative}:{line_number}")
                continue
            patient_rows += 1
            total_rows += 1
            for column, value in zip(EXPECTED_COLUMNS, row, strict=True):
                if value != "NaN" and value != "":
                    nonmissing[column] += 1
            try:
                iculos = float(row[39])
                if previous_iculos is not None and iculos <= previous_iculos:
                    nonmonotonic_iculos.append(relative)
                previous_iculos = iculos
            except ValueError:
                malformed_rows.append(f"{relative}:{line_number}:ICULOS")
            if row[40] == "1":
                patient_septic = True
                septic_rows += 1
            elif row[40] != "0":
                malformed_rows.append(f"{relative}:{line_number}:SepsisLabel")
            for index in range(34, 39):
                value = row[index]
                if value in ("", "NaN"):
                    continue
                if index not in static_reference:
                    static_reference[index] = value
                elif static_reference[index] != value:
                    static_changed = True

        row_counts.append(patient_rows)
        septic_patients += int(patient_septic)
        if static_changed:
            changing_static.append(relative)

    expected_count = EXPECTED_PATIENT_COUNTS[cohort]
    return {
        "cohort": cohort,
        "directory": f"training/training_set{cohort}",
        "patient_files": len(files),
        "expected_patient_files": expected_count,
        "download_complete": len(files) == expected_count,
        "total_patient_hours": total_rows,
        "hours_per_patient": {
            "minimum": min(row_counts) if row_counts else 0,
            "median": statistics.median(row_counts) if row_counts else 0,
            "mean": statistics.fmean(row_counts) if row_counts else 0,
            "maximum": max(row_counts) if row_counts else 0,
        },
        "septic_patients": septic_patients,
        "septic_patient_fraction": septic_patients / len(files) if files else None,
        "septic_patient_hours": septic_rows,
        "nonmissing_counts": dict(nonmissing),
        "nonmissing_fractions": {
            column: count / total_rows if total_rows else None
            for column, count in nonmissing.items()
        },
        "invalid_header_files": invalid_headers,
        "malformed_rows": malformed_rows,
        "nonmonotonic_iculos_files": sorted(set(nonmonotonic_iculos)),
        "changing_static_files": changing_static,
        "aggregate_file_fingerprint_sha256": aggregate_digest.hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Write a partial audit instead of failing when cohort counts are incomplete.",
    )
    args = parser.parse_args()

    root = args.data_root.resolve()
    cohorts = [audit_cohort(root, cohort) for cohort in ("A", "B")]
    license_path = root / "LICENSE.txt"
    payload = {
        "dataset": "PhysioNet/Computing in Cardiology Challenge 2019 v1.0.0",
        "doi": "10.13026/v64v-d857",
        "audit_date": "2026-09-12",
        "expected_columns": EXPECTED_COLUMNS,
        "dynamic_columns": DYNAMIC_COLUMNS,
        "static_columns": STATIC_COLUMNS,
        "license_sha256": sha256(license_path) if license_path.exists() else None,
        "cohorts": cohorts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    complete = all(cohort["download_complete"] for cohort in cohorts)
    clean = all(
        not cohort[key]
        for cohort in cohorts
        for key in (
            "invalid_header_files",
            "malformed_rows",
            "nonmonotonic_iculos_files",
            "changing_static_files",
        )
    )
    print(
        json.dumps(
            {
                "download_complete": complete,
                "integrity_clean": clean,
                "patient_files": {
                    cohort["cohort"]: cohort["patient_files"] for cohort in cohorts
                },
                "output": str(args.output),
            },
            indent=2,
        )
    )
    if not complete and not args.allow_incomplete:
        return 2
    return 0 if clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
