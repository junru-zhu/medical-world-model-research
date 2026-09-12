#!/usr/bin/env python3
"""Compare two independent full-text reviews.

The input candidate file may use either ``stratum`` (discovery-filter audit)
or ``route`` (expanded alternate-term search) as its screening-route field.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def kappa(a: list[str], b: list[str]) -> float | None:
    observed = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = Counter(a), Counter(b)
    expected = sum(
        (ca[label] / len(a)) * (cb[label] / len(b))
        for label in set(a) | set(b)
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

    candidate_rows = read(args.candidates)
    if not candidate_rows:
        raise ValueError("Candidate file is empty.")
    route_field = next(
        (field for field in ("stratum", "route") if field in candidate_rows[0]),
        None,
    )
    if route_field is None:
        raise ValueError("Candidate file must contain either 'stratum' or 'route'.")
    candidates = {row["audit_id"]: row for row in candidate_rows}
    a = {row["audit_id"]: row for row in read(args.reviewer_a)}
    b = {row["audit_id"]: row for row in read(args.reviewer_b)}
    if set(candidates) != set(a) or set(candidates) != set(b):
        raise ValueError("Candidate and reviewer full-text IDs differ.")
    ids = list(candidates)
    da = [a[x]["decision"] for x in ids]
    db = [b[x]["decision"] for x in ids]

    resolved: list[dict[str, str]] = []
    adjudication: list[dict[str, str]] = []
    for audit_id in ids:
        candidate, left, right = candidates[audit_id], a[audit_id], b[audit_id]
        consensus = (
            left["decision"] == right["decision"]
            and left["decision"] in {"include", "exclude"}
            and left["corpus_type"] == right["corpus_type"]
        )
        common = {
            "audit_id": audit_id,
            route_field: candidate[route_field],
            "title": candidate["title"],
            "reviewer_a_decision": left["decision"],
            "reviewer_a_corpus_type": left["corpus_type"],
            "reviewer_a_reason_code": left["reason_code"],
            "reviewer_a_rationale": left["rationale"],
            "reviewer_b_decision": right["decision"],
            "reviewer_b_corpus_type": right["corpus_type"],
            "reviewer_b_reason_code": right["reason_code"],
            "reviewer_b_rationale": right["rationale"],
        }
        if consensus:
            resolved.append(
                {
                    **common,
                    "final_decision": left["decision"],
                    "final_corpus_type": left["corpus_type"],
                    "final_reason_code": left["reason_code"],
                    "resolution_route": "reviewer_consensus",
                    "adjudication_rationale": (
                        f"A: {left['rationale']} B: {right['rationale']}"
                    ),
                }
            )
        else:
            adjudication.append(
                {
                    **common,
                    "final_decision": "",
                    "final_corpus_type": "",
                    "final_reason_code": "",
                    "adjudication_rationale": "",
                }
            )

    summary = {
        "records": len(ids),
        "agreement_count": sum(x == y for x, y in zip(da, db)),
        "raw_agreement": sum(x == y for x, y in zip(da, db)) / len(ids),
        "cohen_kappa": kappa(da, db),
        "reviewer_a_distribution": dict(sorted(Counter(da).items())),
        "reviewer_b_distribution": dict(sorted(Counter(db).items())),
        "consensus_resolved": len(resolved),
        "requires_adjudication": len(adjudication),
    }
    fields = [
        "audit_id",
        route_field,
        "title",
        "reviewer_a_decision",
        "reviewer_a_corpus_type",
        "reviewer_a_reason_code",
        "reviewer_a_rationale",
        "reviewer_b_decision",
        "reviewer_b_corpus_type",
        "reviewer_b_reason_code",
        "reviewer_b_rationale",
        "final_decision",
        "final_corpus_type",
        "final_reason_code",
        "resolution_route",
        "adjudication_rationale",
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "agreement-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    write(args.output_dir / "consensus-resolved.csv", resolved, fields)
    adjudication_fields = [field for field in fields if field != "resolution_route"]
    write(
        args.output_dir / "adjudication-required.csv",
        adjudication,
        adjudication_fields,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
