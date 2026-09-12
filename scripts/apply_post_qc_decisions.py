#!/usr/bin/env python3
"""Apply documented lead decisions after an independent inclusion-QC pass."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


LEAD_FIELDS = [
    "lead_final_decision",
    "lead_final_corpus_type",
    "lead_final_reason_code",
    "lead_rationale",
    "lead_full_text_anchor",
    "lead_confidence",
]
LEAD_INPUT_FIELDS = [
    "audit_id",
    "final_decision",
    "final_corpus_type",
    "final_reason_code",
    "lead_rationale",
    "full_text_anchor",
    "confidence",
]


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudicated", type=Path, required=True)
    parser.add_argument("--lead-decisions", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    _, rows = read(args.adjudicated)
    by_id = {row["audit_id"]: row for row in rows}
    decision_fields, decisions_list = read(args.lead_decisions)
    if decision_fields != LEAD_INPUT_FIELDS:
        raise ValueError(
            "Lead-decision schema mismatch: "
            f"expected {LEAD_INPUT_FIELDS}, found {decision_fields}"
        )
    decisions = {row["audit_id"]: row for row in decisions_list}
    if len(decisions) != len(decisions_list):
        raise ValueError("Duplicate IDs in lead decisions.")
    if not set(decisions).issubset(by_id):
        raise ValueError(f"Unknown lead-decision IDs: {set(decisions) - set(by_id)}")
    for index, decision in enumerate(decisions_list, start=2):
        blank = [
            field for field in LEAD_INPUT_FIELDS if not decision[field].strip()
        ]
        if blank:
            raise ValueError(
                f"{args.lead_decisions}:{index}: blank fields {blank}"
            )
        if decision["final_decision"] not in {"include", "exclude"}:
            raise ValueError(
                f"{args.lead_decisions}:{index}: invalid final_decision"
            )
        if decision["final_corpus_type"] not in {
            "empirical",
            "review",
            "not_applicable",
        }:
            raise ValueError(
                f"{args.lead_decisions}:{index}: invalid final_corpus_type"
            )
        if decision["confidence"] not in {"high", "medium", "low"}:
            raise ValueError(
                f"{args.lead_decisions}:{index}: invalid confidence"
            )
        if (
            decision["final_decision"] == "include"
            and decision["final_corpus_type"] not in {"empirical", "review"}
        ):
            raise ValueError(
                f"{args.lead_decisions}:{index}: included row has invalid type"
            )
        if (
            decision["final_decision"] == "exclude"
            and decision["final_corpus_type"] != "not_applicable"
        ):
            raise ValueError(
                f"{args.lead_decisions}:{index}: excluded row must be not_applicable"
            )

    output: list[dict[str, str]] = []
    for row in rows:
        merged = dict(row)
        for field in LEAD_FIELDS:
            merged[field] = ""
        decision = decisions.get(row["audit_id"])
        if decision:
            merged["lead_final_decision"] = decision["final_decision"]
            merged["lead_final_corpus_type"] = decision["final_corpus_type"]
            merged["lead_final_reason_code"] = decision["final_reason_code"]
            merged["lead_rationale"] = decision["lead_rationale"]
            merged["lead_full_text_anchor"] = decision["full_text_anchor"]
            merged["lead_confidence"] = decision["confidence"]
            merged["final_decision"] = decision["final_decision"]
            merged["final_corpus_type"] = decision["final_corpus_type"]
            merged["final_reason_code"] = decision["final_reason_code"]
            merged["resolution_route"] = "post_qc_lead_source_sufficiency"
            merged["adjudication_rationale"] = decision["lead_rationale"]
        output.append(merged)

    fields = list(rows[0]) + LEAD_FIELDS
    included = [row for row in output if row["final_decision"] == "include"]
    excluded = [row for row in output if row["final_decision"] == "exclude"]
    if len(included) + len(excluded) != len(output):
        raise ValueError("All final decisions must be include or exclude.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / "adjudicated.csv", output, fields)
    write(args.output_dir / "included.csv", included, fields)
    write(args.output_dir / "excluded.csv", excluded, fields)
    summary = {
        "records": len(output),
        "post_qc_lead_decisions": len(decisions),
        "included_total": len(included),
        "included_empirical": sum(
            row["final_corpus_type"] == "empirical" for row in included
        ),
        "included_reviews": sum(
            row["final_corpus_type"] == "review" for row in included
        ),
        "excluded_total": len(excluded),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
