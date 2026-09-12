#!/usr/bin/env python3
"""Compare discovery-filter audit screeners and select conservative follow-up."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def kappa(a: list[str], b: list[str]) -> float | None:
    if not a:
        return None
    observed = sum(x == y for x, y in zip(a, b)) / len(a)
    count_a, count_b = Counter(a), Counter(b)
    labels = set(a) | set(b)
    expected = sum(
        (count_a[label] / len(a)) * (count_b[label] / len(b))
        for label in labels
    )
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    candidates = read_csv(args.candidates)
    reviewer_a = {row["audit_id"]: row for row in read_csv(args.reviewer_a)}
    reviewer_b = {row["audit_id"]: row for row in read_csv(args.reviewer_b)}
    candidate_ids = [row["audit_id"] for row in candidates]
    if set(candidate_ids) != set(reviewer_a) or set(candidate_ids) != set(reviewer_b):
        raise ValueError("Candidate and reviewer audit IDs are not aligned.")

    decisions_a = [reviewer_a[audit_id]["decision"] for audit_id in candidate_ids]
    decisions_b = [reviewer_b[audit_id]["decision"] for audit_id in candidate_ids]
    disagreements: list[dict[str, str]] = []
    follow_up: list[dict[str, str]] = []
    stratum_summary: dict[str, dict[str, int]] = {}
    for candidate in candidates:
        audit_id = candidate["audit_id"]
        a = reviewer_a[audit_id]
        b = reviewer_b[audit_id]
        stratum = candidate["stratum"]
        stats = stratum_summary.setdefault(
            stratum,
            {
                "records": 0,
                "consensus_exclude": 0,
                "consensus_include": 0,
                "other_follow_up": 0,
            },
        )
        stats["records"] += 1
        if a["decision"] == b["decision"] == "exclude":
            stats["consensus_exclude"] += 1
        elif a["decision"] == b["decision"] == "include":
            stats["consensus_include"] += 1
        else:
            stats["other_follow_up"] += 1
        if a["decision"] != b["decision"]:
            disagreements.append(
                {
                    "audit_id": audit_id,
                    "stratum": stratum,
                    "title": candidate["title"],
                    "reviewer_a_decision": a["decision"],
                    "reviewer_a_reason_code": a["reason_code"],
                    "reviewer_a_rationale": a["rationale"],
                    "reviewer_b_decision": b["decision"],
                    "reviewer_b_reason_code": b["reason_code"],
                    "reviewer_b_rationale": b["rationale"],
                }
            )
        if a["decision"] != "exclude" or b["decision"] != "exclude":
            row = dict(candidate)
            row.update(
                {
                    "reviewer_a_decision": a["decision"],
                    "reviewer_a_corpus_type": a["corpus_type"],
                    "reviewer_a_reason_code": a["reason_code"],
                    "reviewer_a_rationale": a["rationale"],
                    "reviewer_b_decision": b["decision"],
                    "reviewer_b_corpus_type": b["corpus_type"],
                    "reviewer_b_reason_code": b["reason_code"],
                    "reviewer_b_rationale": b["rationale"],
                }
            )
            follow_up.append(row)

    summary = {
        "records": len(candidates),
        "agreement_count": sum(
            x == y for x, y in zip(decisions_a, decisions_b)
        ),
        "raw_agreement": sum(
            x == y for x, y in zip(decisions_a, decisions_b)
        )
        / len(candidates),
        "cohen_kappa": kappa(decisions_a, decisions_b),
        "reviewer_a_distribution": dict(sorted(Counter(decisions_a).items())),
        "reviewer_b_distribution": dict(sorted(Counter(decisions_b).items())),
        "disagreements": len(disagreements),
        "conservative_full_text_follow_up": len(follow_up),
        "strata": stratum_summary,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "agreement-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(
        args.output_dir / "disagreements.csv",
        disagreements,
        [
            "audit_id",
            "stratum",
            "title",
            "reviewer_a_decision",
            "reviewer_a_reason_code",
            "reviewer_a_rationale",
            "reviewer_b_decision",
            "reviewer_b_reason_code",
            "reviewer_b_rationale",
        ],
    )
    fields = list(candidates[0]) + [
        "reviewer_a_decision",
        "reviewer_a_corpus_type",
        "reviewer_a_reason_code",
        "reviewer_a_rationale",
        "reviewer_b_decision",
        "reviewer_b_corpus_type",
        "reviewer_b_reason_code",
        "reviewer_b_rationale",
    ]
    write_csv(args.output_dir / "full-text-candidates.csv", follow_up, fields)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
