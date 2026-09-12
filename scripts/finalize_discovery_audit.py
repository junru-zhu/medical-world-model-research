#!/usr/bin/env python3
"""Merge consensus and third-review decisions for the discovery-filter audit."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--consensus", type=Path, required=True)
    parser.add_argument("--adjudications", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    candidates = read(args.candidates)
    by_id = {row["audit_id"]: row for row in candidates}
    consensus = {row["audit_id"]: row for row in read(args.consensus)}
    adjudications = {row["audit_id"]: row for row in read(args.adjudications)}
    if set(consensus) & set(adjudications):
        raise ValueError("Consensus and adjudication IDs overlap.")
    if set(consensus) | set(adjudications) != set(by_id):
        missing = set(by_id) - (set(consensus) | set(adjudications))
        extra = (set(consensus) | set(adjudications)) - set(by_id)
        raise ValueError(f"Decision coverage mismatch: missing={missing}, extra={extra}")

    rows: list[dict[str, str]] = []
    for candidate in candidates:
        audit_id = candidate["audit_id"]
        if audit_id in consensus:
            decision = consensus[audit_id]
            resolution_route = "reviewer_consensus"
            rationale = decision["adjudication_rationale"]
        else:
            decision = adjudications[audit_id]
            resolution_route = "third_full_text_adjudication"
            rationale = decision["adjudication_rationale"]
        rows.append(
            {
                **candidate,
                "final_decision": decision["final_decision"],
                "final_corpus_type": decision["final_corpus_type"],
                "final_reason_code": decision["final_reason_code"],
                "resolution_route": resolution_route,
                "adjudication_rationale": rationale,
            }
        )
    fields = list(candidates[0]) + [
        "final_decision",
        "final_corpus_type",
        "final_reason_code",
        "resolution_route",
        "adjudication_rationale",
    ]
    included = [row for row in rows if row["final_decision"] == "include"]
    excluded = [row for row in rows if row["final_decision"] == "exclude"]
    if len(included) + len(excluded) != len(rows):
        raise ValueError("Every final decision must be include or exclude.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / "adjudicated.csv", rows, fields)
    write(args.output_dir / "included.csv", included, fields)
    write(args.output_dir / "excluded.csv", excluded, fields)
    summary = {
        "records": len(rows),
        "included_total": len(included),
        "included_empirical": sum(
            row["final_corpus_type"] == "empirical" for row in included
        ),
        "included_reviews": sum(
            row["final_corpus_type"] == "review" for row in included
        ),
        "excluded_total": len(excluded),
        "third_adjudications": len(adjudications),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
