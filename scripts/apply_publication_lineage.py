#!/usr/bin/env python3
"""Apply publication-lineage decisions to a provisionally merged corpus."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


LINEAGE_FIELDS = [
    "candidate_id",
    "title",
    "lineage_action",
    "canonical_candidate_id",
    "relation_type",
    "lineage_rationale",
    "source_anchor",
    "confidence",
]
ALLOWED_ACTIONS = {
    "retain",
    "merge_into_existing",
    "merge_into_novel",
    "exclude_unstable",
}


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


def merge_tokens(left: str, right: str) -> str:
    values = {
        item.strip()
        for value in (left, right)
        for item in value.split(";")
        if item.strip()
    }
    return ";".join(sorted(values))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merged", type=Path, required=True)
    parser.add_argument("--existing-included", type=Path, required=True)
    parser.add_argument("--lineage", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    merged_fields, merged_rows = read(args.merged)
    _, existing_rows = read(args.existing_included)
    lineage_fields, lineage_rows = read(args.lineage)
    if lineage_fields != LINEAGE_FIELDS:
        raise ValueError(
            f"Lineage schema mismatch: expected {LINEAGE_FIELDS}, "
            f"found {lineage_fields}"
        )

    merged_by_id = {row["candidate_id"]: dict(row) for row in merged_rows}
    if len(merged_by_id) != len(merged_rows):
        raise ValueError("Duplicate candidate_id in merged corpus.")
    existing_ids = {row["candidate_id"] for row in existing_rows}
    novel_order = [
        row["candidate_id"]
        for row in merged_rows
        if row["candidate_id"] not in existing_ids
    ]
    lineage_order = [row["candidate_id"] for row in lineage_rows]
    if lineage_order != novel_order:
        raise ValueError("Lineage rows do not match novel merged-corpus order.")
    decisions = {row["candidate_id"]: row for row in lineage_rows}
    if len(decisions) != len(lineage_rows):
        raise ValueError("Duplicate candidate_id in lineage decisions.")

    for index, row in enumerate(lineage_rows, start=2):
        blank = [field for field in LINEAGE_FIELDS if not row[field].strip()]
        if blank:
            raise ValueError(f"{args.lineage}:{index}: blank fields {blank}")
        if row["title"] != merged_by_id[row["candidate_id"]]["title"]:
            raise ValueError(
                f"{args.lineage}:{index}: title mismatch for "
                f"{row['candidate_id']}"
            )
        if row["lineage_action"] not in ALLOWED_ACTIONS:
            raise ValueError(
                f"{args.lineage}:{index}: invalid lineage_action"
            )
        if row["confidence"] not in {"high", "medium", "low"}:
            raise ValueError(f"{args.lineage}:{index}: invalid confidence")
        canonical_id = row["canonical_candidate_id"]
        if canonical_id not in merged_by_id:
            raise ValueError(
                f"{args.lineage}:{index}: unknown canonical_candidate_id"
            )
        if row["lineage_action"] == "retain":
            if canonical_id != row["candidate_id"]:
                raise ValueError(
                    f"{args.lineage}:{index}: retain must be self-canonical"
                )
        elif row["lineage_action"] == "merge_into_existing":
            if canonical_id not in existing_ids:
                raise ValueError(
                    f"{args.lineage}:{index}: target is not existing"
                )
        elif row["lineage_action"] == "merge_into_novel":
            target = decisions.get(canonical_id)
            if target is None or target["lineage_action"] != "retain":
                raise ValueError(
                    f"{args.lineage}:{index}: novel target must be retained"
                )
        elif canonical_id != row["candidate_id"]:
            raise ValueError(
                f"{args.lineage}:{index}: excluded record must self-reference"
            )

    removed_ids = {
        row["candidate_id"]
        for row in lineage_rows
        if row["lineage_action"] != "retain"
    }
    for decision in lineage_rows:
        if decision["lineage_action"] not in {
            "merge_into_existing",
            "merge_into_novel",
        }:
            continue
        source = merged_by_id[decision["candidate_id"]]
        target = merged_by_id[decision["canonical_candidate_id"]]
        target["source_routes"] = merge_tokens(
            target.get("source_routes", ""), source.get("source_routes", "")
        )
        target["source_record_ids"] = merge_tokens(
            target.get("source_record_ids", ""),
            source.get("source_record_ids", ""),
        )
        target["exact_match_group_size"] = str(
            int(target.get("exact_match_group_size", "1"))
            + int(source.get("exact_match_group_size", "1"))
        )

    lineage_output_fields = [
        "lineage_action",
        "lineage_canonical_candidate_id",
        "lineage_relation_type",
        "lineage_rationale",
        "lineage_source_anchor",
        "lineage_confidence",
    ]
    included: list[dict[str, str]] = []
    removed: list[dict[str, str]] = []
    for row in merged_rows:
        candidate_id = row["candidate_id"]
        output = dict(merged_by_id[candidate_id])
        if candidate_id in decisions:
            decision = decisions[candidate_id]
            output.update(
                {
                    "lineage_action": decision["lineage_action"],
                    "lineage_canonical_candidate_id": decision[
                        "canonical_candidate_id"
                    ],
                    "lineage_relation_type": decision["relation_type"],
                    "lineage_rationale": decision["lineage_rationale"],
                    "lineage_source_anchor": decision["source_anchor"],
                    "lineage_confidence": decision["confidence"],
                }
            )
        else:
            output.update(
                {
                    "lineage_action": "existing_corpus",
                    "lineage_canonical_candidate_id": candidate_id,
                    "lineage_relation_type": "existing_corpus",
                    "lineage_rationale": (
                        "Retained from the pre-correction development corpus."
                    ),
                    "lineage_source_anchor": "existing final-corpus ledger",
                    "lineage_confidence": "high",
                }
            )
        if candidate_id in removed_ids:
            removed.append(output)
        else:
            included.append(output)

    output_fields = [*merged_fields, *lineage_output_fields]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / "included.csv", included, output_fields)
    write(args.output_dir / "removed-or-merged.csv", removed, output_fields)
    write(args.output_dir / "lineage-ledger.csv", lineage_rows, LINEAGE_FIELDS)
    summary = {
        "merged_input_records": len(merged_rows),
        "existing_records": len(existing_ids),
        "novel_records_reviewed": len(lineage_rows),
        "retained_total": len(included),
        "retained_empirical": sum(
            row["final_corpus_type"] == "empirical" for row in included
        ),
        "retained_reviews": sum(
            row["final_corpus_type"] == "review" for row in included
        ),
        "lineage_actions": {
            action: sum(row["lineage_action"] == action for row in lineage_rows)
            for action in sorted(ALLOWED_ACTIONS)
        },
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
