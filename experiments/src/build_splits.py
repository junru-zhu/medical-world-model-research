#!/usr/bin/env python3
"""Create deterministic patient-level splits for PhysioNet 2019."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


EXPECTED_COUNTS = {"A": 20336, "B": 20000}


def uniform_hash(seed: str, cohort: str, patient_id: str) -> tuple[str, float]:
    digest = hashlib.sha256(f"{seed}|{cohort}|{patient_id}".encode("utf-8")).hexdigest()
    return digest, int(digest, 16) / 2**256


def split_name(cohort: str, value: float) -> str:
    if cohort == "A":
        if value < 0.70:
            return "train"
        if value < 0.85:
            return "validation"
        return "internal_test"
    return "external_calibration" if value < 0.10 else "external_test"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", default="medwm-eval-icu-v1")
    args = parser.parse_args()

    root = args.data_root.resolve()
    rows: list[dict[str, str]] = []
    for cohort in ("A", "B"):
        cohort_dir = root / "training" / f"training_set{cohort}"
        files = sorted(cohort_dir.glob("*.psv"))
        if len(files) != EXPECTED_COUNTS[cohort]:
            raise SystemExit(
                f"Cohort {cohort} is incomplete: {len(files)} files, "
                f"expected {EXPECTED_COUNTS[cohort]}."
            )
        for path in files:
            patient_id = path.stem
            digest, value = uniform_hash(args.seed, cohort, patient_id)
            rows.append(
                {
                    "patient_id": patient_id,
                    "cohort": cohort,
                    "split": split_name(cohort, value),
                    "relative_path": path.relative_to(root).as_posix(),
                    "split_hash_sha256": digest,
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "patient_id",
                "cohort",
                "split",
                "relative_path",
                "split_hash_sha256",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["split"]] = counts.get(row["split"], 0) + 1
    print(f"Wrote {len(rows)} patients to {args.output}")
    for split, count in sorted(counts.items()):
        print(f"{split}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
