#!/usr/bin/env python3
"""Build a consensus-filled extraction file and a disagreement queue."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


IDENTITY_FIELDS = {"candidate_id", "title"}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def write_rows(
    path: Path, fields: list[str], rows: list[dict[str, str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    fields_a, rows_a = read_rows(args.reviewer_a)
    fields_b, rows_b = read_rows(args.reviewer_b)
    if fields_a != fields_b or len(rows_a) != len(rows_b):
        raise ValueError("Reviewer extraction files are not aligned")

    output_rows: list[dict[str, str]] = []
    queue_rows: list[dict[str, str]] = []
    records_with_disagreement: set[str] = set()
    for line, (row_a, row_b) in enumerate(
        zip(rows_a, rows_b, strict=True), start=2
    ):
        if (
            row_a["candidate_id"] != row_b["candidate_id"]
            or row_a["title"] != row_b["title"]
        ):
            raise ValueError(f"Reviewer identity mismatch at line {line}")
        output = {field: "" for field in fields_a}
        output["candidate_id"] = row_a["candidate_id"]
        output["title"] = row_a["title"]
        for field in fields_a:
            if field in IDENTITY_FIELDS:
                continue
            if normalized(row_a[field]) == normalized(row_b[field]):
                output[field] = row_a[field]
            else:
                records_with_disagreement.add(row_a["candidate_id"])
                queue_rows.append(
                    {
                        "candidate_id": row_a["candidate_id"],
                        "title": row_a["title"],
                        "field": field,
                        "reviewer_a": row_a[field],
                        "reviewer_b": row_b[field],
                        "adjudicated_value": "",
                        "adjudication_anchor": "",
                        "adjudication_notes": "",
                    }
                )
        output_rows.append(output)

    queue_fields = [
        "candidate_id",
        "title",
        "field",
        "reviewer_a",
        "reviewer_b",
        "adjudicated_value",
        "adjudication_anchor",
        "adjudication_notes",
    ]
    write_rows(args.output, fields_a, output_rows)
    write_rows(args.queue, queue_fields, queue_rows)
    summary = {
        "records": len(output_rows),
        "fields_compared_per_record": len(fields_a) - len(IDENTITY_FIELDS),
        "disagreements": len(queue_rows),
        "records_with_disagreement": len(records_with_disagreement),
        "status": "adjudication_required" if queue_rows else "consensus_complete",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
