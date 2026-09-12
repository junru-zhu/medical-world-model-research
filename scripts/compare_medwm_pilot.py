#!/usr/bin/env python3
"""Compare two independent MedWM-Eval pilot coding files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


NONCODE_FIELDS = {
    "candidate_id",
    "title",
    "evidence_anchors",
    "reviewer_notes",
    "confidence",
}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {path}")
        return reader.fieldnames, list(reader)


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    if len(a) != len(b) or not a:
        raise ValueError("Kappa requires equal nonempty vectors.")
    labels = sorted(set(a) | set(b))
    observed = sum(left == right for left, right in zip(a, b, strict=True)) / len(a)
    left_counts = Counter(a)
    right_counts = Counter(b)
    expected = sum(
        (left_counts[label] / len(a)) * (right_counts[label] / len(b))
        for label in labels
    )
    if expected == 1:
        return None
    return (observed - expected) / (1 - expected)


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

    code_fields = [field for field in fields_a if field not in NONCODE_FIELDS]
    disagreements: list[dict[str, str]] = []
    summary: dict[str, Any] = {
        "records": len(rows_a),
        "code_fields": code_fields,
        "fields": {},
    }

    for index, (row_a, row_b) in enumerate(zip(rows_a, rows_b, strict=True)):
        if row_a["candidate_id"] != row_b["candidate_id"]:
            raise ValueError(f"Candidate ID mismatch at row {index + 1}")
        if row_a["title"] != row_b["title"]:
            raise ValueError(f"Title mismatch at row {index + 1}")
        for field in code_fields:
            if row_a[field] != row_b[field]:
                disagreements.append(
                    {
                        "candidate_id": row_a["candidate_id"],
                        "title": row_a["title"],
                        "field": field,
                        "reviewer_a": row_a[field],
                        "reviewer_b": row_b[field],
                        "reviewer_a_notes": row_a["reviewer_notes"],
                        "reviewer_b_notes": row_b["reviewer_notes"],
                        "reviewer_a_anchors": row_a["evidence_anchors"],
                        "reviewer_b_anchors": row_b["evidence_anchors"],
                    }
                )

    for field in code_fields:
        values_a = [row[field] for row in rows_a]
        values_b = [row[field] for row in rows_b]
        agreement = sum(
            left == right for left, right in zip(values_a, values_b, strict=True)
        )
        summary["fields"][field] = {
            "agreement_count": agreement,
            "raw_agreement": agreement / len(rows_a),
            "cohen_kappa": cohen_kappa(values_a, values_b),
            "reviewer_a_distribution": dict(sorted(Counter(values_a).items())),
            "reviewer_b_distribution": dict(sorted(Counter(values_b).items())),
        }

    total_decisions = len(rows_a) * len(code_fields)
    summary["overall"] = {
        "decisions": total_decisions,
        "agreement_count": total_decisions - len(disagreements),
        "raw_agreement": (total_decisions - len(disagreements)) / total_decisions,
        "disagreements": len(disagreements),
        "records_with_disagreement": len(
            {row["candidate_id"] for row in disagreements}
        ),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "disagreements.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        fieldnames = [
            "candidate_id",
            "title",
            "field",
            "reviewer_a",
            "reviewer_b",
            "reviewer_a_notes",
            "reviewer_b_notes",
            "reviewer_a_anchors",
            "reviewer_b_anchors",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(disagreements)
    (args.output_dir / "agreement-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary["overall"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
