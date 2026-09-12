#!/usr/bin/env python3
"""Identify final-search candidates absent from the initial screened snapshot."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-candidates", type=Path, required=True)
    parser.add_argument("--initial-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.initial_review.open(newline="", encoding="utf-8") as handle:
        initial_titles = {
            normalize_title(row["title"]) for row in csv.DictReader(handle)
        }
    with args.final_candidates.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        final_rows = list(reader)

    addendum = [
        row for row in final_rows if normalize_title(row["title"]) not in initial_titles
    ]
    if not addendum:
        raise ValueError("No addendum candidates found.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames + ["final_search_id"])
        writer.writeheader()
        for index, row in enumerate(addendum, start=1):
            final_search_id = row["candidate_id"]
            writer.writerow(
                {
                    **row,
                    "candidate_id": f"MWM-A{index:03d}",
                    "final_search_id": final_search_id,
                }
            )
    print(f"Wrote {len(addendum)} addendum records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
