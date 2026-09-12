#!/usr/bin/env python3
"""Build the residual exhaustive rescreen of primary-search filter exclusions.

The sampled discovery-filter audit found eligible records in both random
exclusion strata. Consequently, every remaining automated exclusion must
receive independent title/abstract screening. Records already covered by the
completed discovery audit or by the active primary-search alternate-term route
are removed to avoid duplicate screening.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


FIELDS = [
    "audit_id",
    "route",
    "title",
    "abstract",
    "authors",
    "year",
    "publication_date",
    "venue",
    "doi",
    "arxiv_id",
    "url",
    "record_type",
    "sources",
    "query_labels",
    "source_status",
    "original_exclusion_reason",
]


def record_uid(row: dict[str, object]) -> str:
    identity = str(
        row.get("doi")
        or row.get("arxiv_id")
        or row.get("title")
        or row.get("url")
        or ""
    ).strip().lower()
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"AUD-{digest}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excluded", type=Path, required=True)
    parser.add_argument("--completed-audit", type=Path, required=True)
    parser.add_argument("--expanded-candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    excluded = read_jsonl(args.excluded)
    completed_ids = {row["audit_id"] for row in read_csv(args.completed_audit)}
    expanded_rows = read_csv(args.expanded_candidates)
    active_primary_ids = {
        row["audit_id"]
        for row in expanded_rows
        if row.get("route") == "primary_search_alternate_filter"
    }

    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    removed_completed = 0
    removed_active = 0
    for record in excluded:
        uid = record_uid(record)
        if uid in completed_ids:
            removed_completed += 1
            continue
        if uid in active_primary_ids:
            removed_active += 1
            continue
        if uid in seen:
            raise ValueError(f"Duplicate residual audit ID: {uid}")
        seen.add(uid)
        reason = str(record.get("exclusion_reason", ""))
        if reason == "world-model phrase absent from title and abstract":
            route = "primary_phrase_filter_residual"
        elif reason == "medical-domain term absent from title and abstract":
            route = "primary_medical_filter_residual"
        else:
            raise ValueError(f"Unexpected exclusion reason: {reason}")
        row = {field: str(record.get(field, "")) for field in FIELDS}
        row["audit_id"] = uid
        row["route"] = route
        row["original_exclusion_reason"] = reason
        rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    route_counts = Counter(row["route"] for row in rows)
    summary = {
        "source_exclusions": len(excluded),
        "completed_audit_ids": len(completed_ids),
        "active_primary_alternate_ids": len(active_primary_ids),
        "removed_as_completed_audit": removed_completed,
        "removed_as_active_primary_alternate": removed_active,
        "residual_records": len(rows),
        "residual_routes": dict(sorted(route_counts.items())),
        "coverage_check": (
            len(rows) + removed_completed + removed_active == len(excluded)
        ),
    }
    summary_path = args.output.parent / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
