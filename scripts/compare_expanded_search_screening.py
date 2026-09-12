#!/usr/bin/env python3
"""Compare dual expanded-search screening and select full-text follow-up."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
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


def kappa(a: list[str], b: list[str]) -> float | None:
    observed = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = Counter(a), Counter(b)
    labels = set(a) | set(b)
    expected = sum((ca[x] / len(a)) * (cb[x] / len(b)) for x in labels)
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--reviewer-c", type=Path, required=True)
    parser.add_argument("--reviewer-d", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    candidates = read(args.candidates)
    c = {row["audit_id"]: row for row in read(args.reviewer_c)}
    d = {row["audit_id"]: row for row in read(args.reviewer_d)}
    ids = [row["audit_id"] for row in candidates]
    if set(ids) != set(c) or set(ids) != set(d):
        raise ValueError("Candidate and reviewer IDs differ.")
    dc = [c[x]["decision"] for x in ids]
    dd = [d[x]["decision"] for x in ids]

    disagreements: list[dict[str, str]] = []
    follow_up: list[dict[str, str]] = []
    route_counts: dict[str, Counter[str]] = {}
    for candidate in candidates:
        audit_id = candidate["audit_id"]
        left, right = c[audit_id], d[audit_id]
        route = candidate["route"]
        route_counter = route_counts.setdefault(route, Counter())
        route_counter["records"] += 1
        if left["decision"] == right["decision"] == "exclude":
            route_counter["consensus_exclude"] += 1
        elif left["decision"] == right["decision"] == "include":
            route_counter["consensus_include"] += 1
        else:
            route_counter["other_follow_up"] += 1
        if left["decision"] != right["decision"]:
            disagreements.append(
                {
                    "audit_id": audit_id,
                    "route": route,
                    "title": candidate["title"],
                    "reviewer_c_decision": left["decision"],
                    "reviewer_c_reason_code": left["reason_code"],
                    "reviewer_c_rationale": left["rationale"],
                    "reviewer_d_decision": right["decision"],
                    "reviewer_d_reason_code": right["reason_code"],
                    "reviewer_d_rationale": right["rationale"],
                }
            )
        if left["decision"] != "exclude" or right["decision"] != "exclude":
            row = dict(candidate)
            for prefix, decision in [("reviewer_c", left), ("reviewer_d", right)]:
                row[f"{prefix}_decision"] = decision["decision"]
                row[f"{prefix}_corpus_type"] = decision["corpus_type"]
                row[f"{prefix}_reason_code"] = decision["reason_code"]
                row[f"{prefix}_rationale"] = decision["rationale"]
            follow_up.append(row)

    summary = {
        "records": len(ids),
        "agreement_count": sum(x == y for x, y in zip(dc, dd)),
        "raw_agreement": sum(x == y for x, y in zip(dc, dd)) / len(ids),
        "cohen_kappa": kappa(dc, dd),
        "reviewer_c_distribution": dict(sorted(Counter(dc).items())),
        "reviewer_d_distribution": dict(sorted(Counter(dd).items())),
        "disagreements": len(disagreements),
        "conservative_full_text_follow_up": len(follow_up),
        "routes": {
            route: dict(sorted(counts.items()))
            for route, counts in route_counts.items()
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "agreement-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    write(
        args.output_dir / "disagreements.csv",
        disagreements,
        [
            "audit_id",
            "route",
            "title",
            "reviewer_c_decision",
            "reviewer_c_reason_code",
            "reviewer_c_rationale",
            "reviewer_d_decision",
            "reviewer_d_reason_code",
            "reviewer_d_rationale",
        ],
    )
    follow_fields = list(candidates[0]) + [
        "reviewer_c_decision",
        "reviewer_c_corpus_type",
        "reviewer_c_reason_code",
        "reviewer_c_rationale",
        "reviewer_d_decision",
        "reviewer_d_corpus_type",
        "reviewer_d_reason_code",
        "reviewer_d_rationale",
    ]
    write(args.output_dir / "full-text-candidates.csv", follow_up, follow_fields)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
