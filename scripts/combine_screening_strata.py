#!/usr/bin/env python3
"""Combine adjudicated screening strata without altering their provenance."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    fieldnames: list[str] | None = None
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in args.input:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if fieldnames is None:
                fieldnames = list(reader.fieldnames or [])
            elif list(reader.fieldnames or []) != fieldnames:
                raise ValueError(f"Column mismatch in {path}")
            for row in reader:
                candidate_id = row["candidate_id"]
                if candidate_id in seen:
                    raise ValueError(f"Duplicate candidate ID: {candidate_id}")
                seen.add(candidate_id)
                rows.append(row)

    if not fieldnames:
        raise ValueError("No input rows.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
