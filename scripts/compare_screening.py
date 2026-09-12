#!/usr/bin/env python3
"""Validate two screening files and report pre-adjudication agreement."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


DECISIONS = ("include", "exclude", "uncertain")
REQUIRED_COLUMNS = (
    "candidate_id",
    "title",
    "decision",
    "corpus_type",
    "reason_code",
    "rationale",
    "full_text_needed",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != REQUIRED_COLUMNS:
            raise ValueError(
                f"{path} has columns {reader.fieldnames}; expected {REQUIRED_COLUMNS}"
            )
        return list(reader)


def read_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate(
    candidates: list[dict[str, str]],
    reviews: list[dict[str, str]],
    label: str,
) -> dict[str, dict[str, str]]:
    expected = {row["candidate_id"]: row for row in candidates}
    observed: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for row_number, row in enumerate(reviews, start=2):
        candidate_id = row["candidate_id"]
        if candidate_id in observed:
            errors.append(f"{label} row {row_number}: duplicate {candidate_id}")
            continue
        if candidate_id not in expected:
            errors.append(f"{label} row {row_number}: unknown {candidate_id}")
            continue
        if row["title"] != expected[candidate_id]["title"]:
            errors.append(f"{label} row {row_number}: title mismatch for {candidate_id}")
        if row["decision"] not in DECISIONS:
            errors.append(
                f"{label} row {row_number}: invalid decision {row['decision']!r}"
            )
        observed[candidate_id] = row
    missing = sorted(set(expected) - set(observed))
    if missing:
        errors.append(f"{label}: missing {len(missing)} candidates: {missing[:10]}")
    if errors:
        raise ValueError("\n".join(errors))
    return observed


def kappa(labels_a: list[str], labels_b: list[str]) -> float:
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("Kappa requires two non-empty, equal-length label lists.")
    total = len(labels_a)
    observed = sum(a == b for a, b in zip(labels_a, labels_b, strict=True)) / total
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    expected = sum(
        (counts_a[label] / total) * (counts_b[label] / total) for label in DECISIONS
    )
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    candidates = read_candidates(args.candidates)
    reviews_a = validate(candidates, read_csv(args.reviewer_a), "reviewer A")
    reviews_b = validate(candidates, read_csv(args.reviewer_b), "reviewer B")

    labels_a: list[str] = []
    labels_b: list[str] = []
    disagreements: list[dict[str, str]] = []
    confusion: Counter[tuple[str, str]] = Counter()
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        row_a = reviews_a[candidate_id]
        row_b = reviews_b[candidate_id]
        labels_a.append(row_a["decision"])
        labels_b.append(row_b["decision"])
        confusion[(row_a["decision"], row_b["decision"])] += 1
        if row_a["decision"] != row_b["decision"]:
            disagreements.append(
                {
                    "candidate_id": candidate_id,
                    "title": candidate["title"],
                    "abstract": candidate.get("abstract", ""),
                    "reviewer_a_decision": row_a["decision"],
                    "reviewer_a_reason": row_a["reason_code"],
                    "reviewer_a_rationale": row_a["rationale"],
                    "reviewer_b_decision": row_b["decision"],
                    "reviewer_b_reason": row_b["reason_code"],
                    "reviewer_b_rationale": row_b["rationale"],
                }
            )

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    disagreement_path = output_dir / "disagreements.csv"
    disagreement_columns = [
        "candidate_id",
        "title",
        "abstract",
        "reviewer_a_decision",
        "reviewer_a_reason",
        "reviewer_a_rationale",
        "reviewer_b_decision",
        "reviewer_b_reason",
        "reviewer_b_rationale",
    ]
    with disagreement_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=disagreement_columns)
        writer.writeheader()
        writer.writerows(disagreements)

    agreement_count = sum(a == b for a, b in zip(labels_a, labels_b, strict=True))
    summary = {
        "candidate_count": len(candidates),
        "reviewer_a_decisions": dict(sorted(Counter(labels_a).items())),
        "reviewer_b_decisions": dict(sorted(Counter(labels_b).items())),
        "agreement_count": agreement_count,
        "agreement_fraction": agreement_count / len(candidates),
        "cohen_kappa": kappa(labels_a, labels_b),
        "disagreement_count": len(disagreements),
        "confusion_matrix": {
            f"a_{a}__b_{b}": confusion[(a, b)] for a in DECISIONS for b in DECISIONS
        },
    }
    summary_path = output_dir / "agreement-summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
