#!/usr/bin/env python3
"""Build an adjudication sheet from two MedWM-Eval pilot coding files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    fields_a, rows_a = read_rows(args.reviewer_a)
    fields_b, rows_b = read_rows(args.reviewer_b)
    if fields_a != fields_b or len(rows_a) != len(rows_b):
        raise ValueError("Reviewer files are not aligned.")
    code_fields = [field for field in fields_a if field not in NONCODE_FIELDS]
    output_fields = (
        ["candidate_id", "title"]
        + code_fields
        + [
            "disagreement_fields",
            "reviewer_a_anchors",
            "reviewer_b_anchors",
            "adjudication_anchors",
            "adjudication_notes",
            "confidence",
        ]
    )

    output_rows: list[dict[str, str]] = []
    for row_a, row_b in zip(rows_a, rows_b, strict=True):
        if (
            row_a["candidate_id"] != row_b["candidate_id"]
            or row_a["title"] != row_b["title"]
        ):
            raise ValueError("Reviewer rows are not aligned.")
        output = {field: "" for field in output_fields}
        output["candidate_id"] = row_a["candidate_id"]
        output["title"] = row_a["title"]
        disagreements: list[str] = []
        for field in code_fields:
            if row_a[field] == row_b[field]:
                output[field] = row_a[field]
            else:
                disagreements.append(field)
        output["disagreement_fields"] = ";".join(disagreements)
        output["reviewer_a_anchors"] = row_a["evidence_anchors"]
        output["reviewer_b_anchors"] = row_b["evidence_anchors"]
        if not disagreements:
            output["adjudication_anchors"] = row_a["evidence_anchors"]
            output["adjudication_notes"] = "Reviewer consensus."
            output["confidence"] = (
                row_a["confidence"]
                if row_a["confidence"] == row_b["confidence"]
                else "medium"
            )
        output_rows.append(output)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Wrote {len(output_rows)} adjudication rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
