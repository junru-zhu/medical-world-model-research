#!/usr/bin/env python3
"""Apply a transparent post-extraction eligibility re-audit."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header")
        return list(reader.fieldnames), list(reader)


def write_csv(
    path: Path, fieldnames: list[str], rows: list[dict[str, str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-included", type=Path, required=True)
    parser.add_argument("--source-excluded", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--source-extraction", type=Path, required=True)
    parser.add_argument("--source-pilot", type=Path, required=True)
    parser.add_argument("--pilot-reviewer-a", type=Path, required=True)
    parser.add_argument("--pilot-reviewer-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    included_fields, included = read_csv(args.source_included)
    excluded_fields, excluded = read_csv(args.source_excluded)
    if included_fields != excluded_fields:
        raise ValueError("Included and excluded screening schemas differ.")
    decision_fields, decisions = read_csv(args.decisions)
    required_decisions = {
        "candidate_id",
        "final_decision",
        "final_corpus_type",
        "primary_reason_code",
        "audit_rationale",
        "confidence",
        "source_quality_note",
    }
    if not required_decisions.issubset(decision_fields):
        raise ValueError("Eligibility decision schema is incomplete.")

    by_id = {row["candidate_id"]: row for row in included}
    decision_by_id = {row["candidate_id"]: row for row in decisions}
    if len(decision_by_id) != len(decisions):
        raise ValueError("Duplicate candidate IDs in re-audit decisions.")
    missing = sorted(set(decision_by_id) - set(by_id))
    if missing:
        raise ValueError(f"Re-audit candidates absent from included set: {missing}")
    if any(row["final_decision"] != "exclude" for row in decisions):
        raise ValueError("This script expects correction rows to be exclusions.")

    final_included = [
        row for row in included if row["candidate_id"] not in decision_by_id
    ]
    reaudited_excluded: list[dict[str, str]] = []
    for candidate_id, decision in decision_by_id.items():
        row = dict(by_id[candidate_id])
        row["final_decision"] = "exclude"
        row["final_corpus_type"] = decision["final_corpus_type"]
        row["final_reason_code"] = decision["primary_reason_code"]
        row["resolution_route"] = "post_extraction_eligibility_reaudit"
        row["adjudication_rationale"] = decision["audit_rationale"]
        reaudited_excluded.append(row)
    final_excluded = excluded + sorted(
        reaudited_excluded, key=lambda row: row["candidate_id"]
    )

    extraction_fields, extraction = read_csv(args.source_extraction)
    pilot_fields, pilot = read_csv(args.source_pilot)
    reviewer_a_fields, reviewer_a = read_csv(args.pilot_reviewer_a)
    reviewer_b_fields, reviewer_b = read_csv(args.pilot_reviewer_b)
    empirical_ids = {
        row["candidate_id"]
        for row in final_included
        if row["final_corpus_type"] == "empirical"
    }
    final_extraction = [
        row for row in extraction if row["candidate_id"] in empirical_ids
    ]
    final_pilot = [row for row in pilot if row["candidate_id"] in empirical_ids]
    final_reviewer_a = [
        row for row in reviewer_a if row["candidate_id"] in empirical_ids
    ]
    final_reviewer_b = [
        row for row in reviewer_b if row["candidate_id"] in empirical_ids
    ]

    if len(final_extraction) != len(empirical_ids):
        raise ValueError("Final extraction does not match empirical IDs.")
    if len(final_pilot) != len(empirical_ids):
        raise ValueError("Final pilot does not match empirical IDs.")
    if len(final_reviewer_a) != len(empirical_ids):
        raise ValueError("Reviewer A pilot does not match empirical IDs.")
    if len(final_reviewer_b) != len(empirical_ids):
        raise ValueError("Reviewer B pilot does not match empirical IDs.")

    write_csv(args.output_dir / "included.csv", included_fields, final_included)
    write_csv(args.output_dir / "excluded.csv", excluded_fields, final_excluded)
    write_csv(
        args.output_dir / "study-extraction.csv",
        extraction_fields,
        final_extraction,
    )
    write_csv(
        args.output_dir / "medwm-eval-final.csv", pilot_fields, final_pilot
    )
    write_csv(
        args.output_dir / "medwm-pilot-reviewer-a.csv",
        reviewer_a_fields,
        final_reviewer_a,
    )
    write_csv(
        args.output_dir / "medwm-pilot-reviewer-b.csv",
        reviewer_b_fields,
        final_reviewer_b,
    )

    summary = {
        "full_text_assessed": len(final_included) + len(final_excluded),
        "included_total": len(final_included),
        "included_empirical": len(empirical_ids),
        "included_reviews": sum(
            row["final_corpus_type"] == "review" for row in final_included
        ),
        "excluded_total": len(final_excluded),
        "reaudit_exclusions": sorted(decision_by_id),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
