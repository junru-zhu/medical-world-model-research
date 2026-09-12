#!/usr/bin/env python3
"""Apply claim-level third-reviewer decisions to the pilot coding sheet."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {path}")
        return reader.fieldnames, list(reader)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--disagreements", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    template_fields, template_rows = read_rows(args.template)
    _, disagreement_rows = read_rows(args.disagreements)
    _, decision_rows = read_rows(args.decisions)
    _, extraction_rows = read_rows(args.extraction)

    disagreement_keys = {
        (row["candidate_id"], row["field"]) for row in disagreement_rows
    }
    decisions: dict[tuple[str, str], dict[str, str]] = {}
    for row in decision_rows:
        key = (row["candidate_id"], row["field"])
        if key in decisions:
            raise ValueError(f"Duplicate adjudication decision: {key}")
        decisions[key] = row
    if set(decisions) != disagreement_keys:
        missing = sorted(disagreement_keys - set(decisions))
        extra = sorted(set(decisions) - disagreement_keys)
        raise ValueError(
            f"Decision coverage mismatch. Missing={missing}; extra={extra}"
        )

    extraction = {row["candidate_id"]: row for row in extraction_rows}
    output_rows: list[dict[str, str]] = []
    for row in template_rows:
        output = dict(row)
        fields = [value for value in row["disagreement_fields"].split(";") if value]
        rationales: list[str] = []
        for field in fields:
            decision = decisions[(row["candidate_id"], field)]
            output[field] = decision["final_value"]
            rationales.append(f"{field}: {decision['rationale']}")
        if fields:
            output["adjudication_anchors"] = extraction[
                row["candidate_id"]
            ]["evidence_anchors"]
            output["adjudication_notes"] = " | ".join(rationales)
            output["confidence"] = (
                "low"
                if any(output[field] == "NI" for field in fields)
                else "medium"
            )
        output_rows.append(output)

    required_code_fields = [
        field
        for field in template_fields
        if field
        not in {
            "candidate_id",
            "title",
            "disagreement_fields",
            "reviewer_a_anchors",
            "reviewer_b_anchors",
            "adjudication_anchors",
            "adjudication_notes",
            "confidence",
        }
    ]
    incomplete = defaultdict(list)
    for row in output_rows:
        for field in required_code_fields:
            if not row[field].strip():
                incomplete[row["candidate_id"]].append(field)
    if incomplete:
        raise ValueError(f"Incomplete adjudicated rows: {dict(incomplete)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=template_fields)
        writer.writeheader()
        writer.writerows(output_rows)
    print(
        f"Wrote {len(output_rows)} fully adjudicated records to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
