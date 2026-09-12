#!/usr/bin/env python3
"""Compare two independent title/abstract screening files.

Any record not excluded by both reviewers is conservatively retained for
full-text assessment.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
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
    if not a:
        return None
    observed = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = Counter(a), Counter(b)
    labels = set(a) | set(b)
    expected = sum((ca[x] / len(a)) * (cb[x] / len(b)) for x in labels)
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def reviewer_index(path: Path, expected_ids: list[str]) -> dict[str, dict[str, str]]:
    rows = read(path)
    by_id = {row["audit_id"]: row for row in rows}
    if len(rows) != len(by_id):
        raise ValueError(f"Duplicate audit IDs in {path}")
    if set(expected_ids) != set(by_id):
        missing = set(expected_ids) - set(by_id)
        extra = set(by_id) - set(expected_ids)
        raise ValueError(
            f"Candidate and reviewer IDs differ for {path}: "
            f"missing={len(missing)}, extra={len(extra)}"
        )
    return by_id


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--reviewer-left", type=Path, required=True)
    parser.add_argument("--reviewer-right", type=Path, required=True)
    parser.add_argument("--left-label", required=True)
    parser.add_argument("--right-label", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    for label in (args.left_label, args.right_label):
        if not re.fullmatch(r"[a-z][a-z0-9_]*", label):
            raise ValueError(
                "Reviewer labels must be lowercase identifiers, e.g. reviewer_c."
            )
    if args.left_label == args.right_label:
        raise ValueError("Reviewer labels must differ.")

    candidates = read(args.candidates)
    if not candidates:
        raise ValueError("Candidate file is empty.")
    ids = [row["audit_id"] for row in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("Candidate audit IDs are not unique.")
    left = reviewer_index(args.reviewer_left, ids)
    right = reviewer_index(args.reviewer_right, ids)
    left_decisions = [left[x]["decision"] for x in ids]
    right_decisions = [right[x]["decision"] for x in ids]

    disagreements: list[dict[str, str]] = []
    follow_up: list[dict[str, str]] = []
    route_counts: dict[str, Counter[str]] = {}
    route_field = "route" if "route" in candidates[0] else "stratum"

    for candidate in candidates:
        audit_id = candidate["audit_id"]
        lrow, rrow = left[audit_id], right[audit_id]
        route = candidate[route_field]
        route_counter = route_counts.setdefault(route, Counter())
        route_counter["records"] += 1
        if lrow["decision"] == rrow["decision"] == "exclude":
            route_counter["consensus_exclude"] += 1
        elif lrow["decision"] == rrow["decision"] == "include":
            route_counter["consensus_include"] += 1
        else:
            route_counter["other_follow_up"] += 1

        if lrow["decision"] != rrow["decision"]:
            disagreements.append(
                {
                    "audit_id": audit_id,
                    route_field: route,
                    "title": candidate["title"],
                    f"{args.left_label}_decision": lrow["decision"],
                    f"{args.left_label}_reason_code": lrow["reason_code"],
                    f"{args.left_label}_rationale": lrow["rationale"],
                    f"{args.right_label}_decision": rrow["decision"],
                    f"{args.right_label}_reason_code": rrow["reason_code"],
                    f"{args.right_label}_rationale": rrow["rationale"],
                }
            )

        if lrow["decision"] != "exclude" or rrow["decision"] != "exclude":
            output = dict(candidate)
            for label, row in (
                (args.left_label, lrow),
                (args.right_label, rrow),
            ):
                output[f"{label}_decision"] = row["decision"]
                output[f"{label}_corpus_type"] = row["corpus_type"]
                output[f"{label}_reason_code"] = row["reason_code"]
                output[f"{label}_rationale"] = row["rationale"]
            follow_up.append(output)

    agreement_count = sum(
        x == y for x, y in zip(left_decisions, right_decisions)
    )
    summary = {
        "records": len(ids),
        "reviewer_left": args.left_label,
        "reviewer_right": args.right_label,
        "agreement_count": agreement_count,
        "raw_agreement": agreement_count / len(ids),
        "cohen_kappa": kappa(left_decisions, right_decisions),
        f"{args.left_label}_distribution": dict(
            sorted(Counter(left_decisions).items())
        ),
        f"{args.right_label}_distribution": dict(
            sorted(Counter(right_decisions).items())
        ),
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

    disagreement_fields = [
        "audit_id",
        route_field,
        "title",
        f"{args.left_label}_decision",
        f"{args.left_label}_reason_code",
        f"{args.left_label}_rationale",
        f"{args.right_label}_decision",
        f"{args.right_label}_reason_code",
        f"{args.right_label}_rationale",
    ]
    write(args.output_dir / "disagreements.csv", disagreements, disagreement_fields)

    follow_fields = list(candidates[0]) + [
        f"{label}_{field}"
        for label in (args.left_label, args.right_label)
        for field in ("decision", "corpus_type", "reason_code", "rationale")
    ]
    write(args.output_dir / "full-text-candidates.csv", follow_up, follow_fields)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
