#!/usr/bin/env python3
"""Promote a validated corrected review corpus from staging to canonical."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import tempfile
from pathlib import Path


EXPECTED = {
    "included_total": 93,
    "included_empirical": 85,
    "included_reviews": 8,
    "extraction_records": 85,
    "medwm_final_records": 85,
    "reviewer_a_records": 85,
    "reviewer_b_records": 85,
}

FILES = [
    "included.csv",
    "study-extraction.csv",
    "medwm-eval-final.csv",
    "medwm-pilot-reviewer-a.csv",
    "medwm-pilot-reviewer-b.csv",
    "medwm-eval-summary.json",
    "medwm-eval-summary.md",
    "reliability-analysis.json",
    "reliability-analysis.md",
    "included-reference-ledger.md",
    "included-reference-map.json",
    "analysis/analysis-annotations.csv",
    "analysis/claim-provenance-audit.csv",
    "analysis/claim-provenance-audit.md",
    "analysis/claim-provenance-summary.json",
    "analysis/methodological-appraisal.csv",
    "analysis/methodological-appraisal.json",
    "analysis/methodological-appraisal.md",
    "analysis/review-sensitivity-analysis.json",
    "analysis/review-sensitivity-analysis.md",
    "analysis/study-characteristics.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def validate(staging: Path) -> dict[str, object]:
    summary = json.loads(
        (staging / "summary.json").read_text(encoding="utf-8")
    )
    for field, expected in EXPECTED.items():
        if summary.get(field) != expected:
            raise ValueError(
                f"Staging {field}={summary.get(field)!r}; expected {expected}"
            )

    included = read_csv(staging / "included.csv")
    empirical_ids = {
        row["candidate_id"]
        for row in included
        if row["final_corpus_type"] == "empirical"
    }
    review_ids = {
        row["candidate_id"]
        for row in included
        if row["final_corpus_type"] == "review"
    }
    if len(included) != 93 or len(empirical_ids) != 85 or len(review_ids) != 8:
        raise ValueError("Staging corpus counts do not match the corrected freeze")

    for name in (
        "study-extraction.csv",
        "medwm-eval-final.csv",
        "medwm-pilot-reviewer-a.csv",
        "medwm-pilot-reviewer-b.csv",
    ):
        rows = read_csv(staging / name)
        ids = {row["candidate_id"] for row in rows}
        if len(rows) != 85 or ids != empirical_ids:
            raise ValueError(f"{name} is not aligned to the empirical corpus")

    annotations = read_csv(staging / "analysis/analysis-annotations.csv")
    if len(annotations) != 85:
        raise ValueError("Analysis annotations must contain 85 studies")
    incomplete = [
        row["candidate_id"]
        for row in annotations
        if not all(
            row.get(field, "").strip()
            for field in ("domain_group", "corpus_boundary", "source_tier")
        )
    ]
    if incomplete:
        raise ValueError(f"Incomplete analysis annotations: {incomplete}")

    missing = [name for name in FILES if not (staging / name).is_file()]
    if missing:
        raise ValueError(f"Missing staging artifacts: {missing}")
    return summary


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=target.parent, prefix=f".{target.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--canonical", type=Path, required=True)
    args = parser.parse_args()

    summary = validate(args.staging)
    for relative in FILES:
        atomic_copy(args.staging / relative, args.canonical / relative)

    canonical_summary = dict(summary)
    canonical_summary["status"] = "corrected_canonical_promoted"
    canonical_summary["source_staging"] = str(args.staging)
    target = args.canonical / "summary.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=target.parent,
        prefix=f".{target.name}.",
        delete=False,
    ) as handle:
        json.dump(canonical_summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    try:
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)

    print(json.dumps(canonical_summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
