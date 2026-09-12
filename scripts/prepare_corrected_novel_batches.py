#!/usr/bin/env python3
"""Prepare disjoint dual-review batches for corrected novel empirical records."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--novel-dir", type=Path, required=True)
    parser.add_argument("--completed-extraction", type=Path, required=True)
    parser.add_argument("--reviewer-medwm-schema", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--batches", type=int, default=3)
    args = parser.parse_args()
    if args.batches < 1:
        raise ValueError("--batches must be at least 1")

    record_fields, records = read_rows(args.novel_dir / "novel-empirical.csv")
    extraction_fields, extraction_template = read_rows(
        args.novel_dir / "study-extraction-template.csv"
    )
    medwm_fields, _ = read_rows(args.reviewer_medwm_schema)
    _, completed = read_rows(args.completed_extraction)
    completed_ids = {row["candidate_id"] for row in completed}
    record_ids = [row["candidate_id"] for row in records]
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("novel-empirical.csv contains duplicate candidate IDs")
    if not completed_ids.issubset(set(record_ids)):
        missing = sorted(completed_ids - set(record_ids))
        raise ValueError(f"Completed IDs are absent from corrected records: {missing}")

    extraction_by_id = {row["candidate_id"]: row for row in extraction_template}
    if set(extraction_by_id) != set(record_ids):
        raise ValueError("Novel record and extraction-template candidate-ID sets differ")

    pending = [row for row in records if row["candidate_id"] not in completed_ids]
    batches: list[list[dict[str, str]]] = [[] for _ in range(args.batches)]
    for index, row in enumerate(pending):
        batches[index % args.batches].append(row)

    manifest_batches: list[dict[str, object]] = []
    for batch_number, batch_records in enumerate(batches, start=1):
        batch_name = f"batch-{batch_number:02d}"
        batch_dir = args.output_dir / batch_name
        ids = [row["candidate_id"] for row in batch_records]
        write_rows(batch_dir / "records.csv", record_fields, batch_records)
        for reviewer in ("reviewer-a", "reviewer-b"):
            reviewer_dir = batch_dir / reviewer
            write_rows(
                reviewer_dir / "study-extraction.csv",
                extraction_fields,
                [extraction_by_id[candidate_id] for candidate_id in ids],
            )
            write_rows(
                reviewer_dir / "medwm-eval.csv",
                medwm_fields,
                [
                    {
                        **{field: "" for field in medwm_fields},
                        "candidate_id": candidate_id,
                        "title": next(
                            row["title"]
                            for row in batch_records
                            if row["candidate_id"] == candidate_id
                        ),
                    }
                    for candidate_id in ids
                ],
            )
        manifest_batches.append(
            {
                "batch": batch_name,
                "records": len(ids),
                "candidate_ids": ids,
            }
        )

    manifest = {
        "novel_empirical": len(records),
        "already_completed": len(completed_ids),
        "pending_dual_review": len(pending),
        "batches": manifest_batches,
        "independence_rule": (
            "Reviewer B must not inspect reviewer A files or decisions before "
            "submitting an independent extraction and coding pass."
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
