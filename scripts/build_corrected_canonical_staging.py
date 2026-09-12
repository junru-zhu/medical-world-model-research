#!/usr/bin/env python3
"""Build a validated corrected corpus in staging before canonical promotion."""

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


def unique_map(
    rows: list[dict[str, str]], *, label: str
) -> dict[str, dict[str, str]]:
    result = {row["candidate_id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"{label}: duplicate candidate_id")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corrected-included", type=Path, required=True)
    parser.add_argument("--existing-included", type=Path, required=True)
    parser.add_argument("--existing-extraction", type=Path, required=True)
    parser.add_argument("--existing-medwm-final", type=Path, required=True)
    parser.add_argument("--existing-reviewer-a", type=Path, required=True)
    parser.add_argument("--existing-reviewer-b", type=Path, required=True)
    parser.add_argument("--novel-extraction", type=Path, required=True)
    parser.add_argument("--novel-medwm-final", type=Path, required=True)
    parser.add_argument("--sampled-reviewer-a", type=Path, required=True)
    parser.add_argument("--sampled-reviewer-b", type=Path, required=True)
    parser.add_argument("--dual-review-base", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    included_fields, corrected_included = read_rows(args.corrected_included)
    _, existing_included = read_rows(args.existing_included)
    extraction_fields, existing_extraction = read_rows(args.existing_extraction)
    medwm_final_fields, existing_medwm_final = read_rows(
        args.existing_medwm_final
    )
    reviewer_fields_a, existing_reviewer_a = read_rows(args.existing_reviewer_a)
    reviewer_fields_b, existing_reviewer_b = read_rows(args.existing_reviewer_b)
    if reviewer_fields_a != reviewer_fields_b:
        raise ValueError("Existing independent reviewer schemas differ")
    novel_extraction_fields, novel_extraction = read_rows(args.novel_extraction)
    novel_medwm_fields, novel_medwm_final = read_rows(args.novel_medwm_final)
    if novel_extraction_fields != extraction_fields:
        raise ValueError("Novel and existing extraction schemas differ")
    if novel_medwm_fields != medwm_final_fields:
        raise ValueError("Novel and existing final MedWM schemas differ")

    empirical_ids = [
        row["candidate_id"]
        for row in corrected_included
        if row["final_corpus_type"] == "empirical"
    ]
    review_ids = [
        row["candidate_id"]
        for row in corrected_included
        if row["final_corpus_type"] == "review"
    ]
    if len(empirical_ids) != len(set(empirical_ids)):
        raise ValueError("Corrected empirical corpus contains duplicate IDs")
    if len(review_ids) != len(set(review_ids)):
        raise ValueError("Corrected review corpus contains duplicate IDs")
    existing_ids = {row["candidate_id"] for row in existing_included}
    novel_empirical_ids = [
        candidate_id
        for candidate_id in empirical_ids
        if candidate_id not in existing_ids
    ]

    extraction_by_id = unique_map(
        existing_extraction + novel_extraction,
        label="combined extraction",
    )
    medwm_final_by_id = unique_map(
        existing_medwm_final + novel_medwm_final,
        label="combined final MedWM",
    )
    if set(extraction_by_id) != set(empirical_ids):
        raise ValueError("Corrected empirical and extraction IDs differ")
    if set(medwm_final_by_id) != set(empirical_ids):
        raise ValueError("Corrected empirical and final MedWM IDs differ")

    _, sampled_reviewer_a = read_rows(args.sampled_reviewer_a)
    _, sampled_reviewer_b = read_rows(args.sampled_reviewer_b)
    novel_reviewer_a = list(sampled_reviewer_a)
    novel_reviewer_b = list(sampled_reviewer_b)
    manifest = json.loads(
        (args.dual_review_base / "manifest.json").read_text(encoding="utf-8")
    )
    for batch in manifest["batches"]:
        batch_dir = args.dual_review_base / batch["batch"]
        fields_a, rows_a = read_rows(
            batch_dir / "reviewer-a/medwm-eval.csv"
        )
        fields_b, rows_b = read_rows(
            batch_dir / "reviewer-b/medwm-eval.csv"
        )
        if fields_a != reviewer_fields_a or fields_b != reviewer_fields_a:
            raise ValueError(f"{batch['batch']}: reviewer schema mismatch")
        expected_ids = list(batch["candidate_ids"])
        if [row["candidate_id"] for row in rows_a] != expected_ids:
            raise ValueError(f"{batch['batch']}: Reviewer A order mismatch")
        if [row["candidate_id"] for row in rows_b] != expected_ids:
            raise ValueError(f"{batch['batch']}: Reviewer B order mismatch")
        novel_reviewer_a.extend(rows_a)
        novel_reviewer_b.extend(rows_b)

    reviewer_a_by_id = unique_map(
        existing_reviewer_a + novel_reviewer_a,
        label="combined Reviewer A",
    )
    reviewer_b_by_id = unique_map(
        existing_reviewer_b + novel_reviewer_b,
        label="combined Reviewer B",
    )
    if set(reviewer_a_by_id) != set(empirical_ids):
        raise ValueError("Corrected empirical and Reviewer A IDs differ")
    if set(reviewer_b_by_id) != set(empirical_ids):
        raise ValueError("Corrected empirical and Reviewer B IDs differ")

    for candidate_id in empirical_ids:
        title = extraction_by_id[candidate_id]["title"]
        if medwm_final_by_id[candidate_id]["title"] != title:
            raise ValueError(f"{candidate_id}: final MedWM title mismatch")
        if reviewer_a_by_id[candidate_id]["title"] != title:
            raise ValueError(f"{candidate_id}: Reviewer A title mismatch")
        if reviewer_b_by_id[candidate_id]["title"] != title:
            raise ValueError(f"{candidate_id}: Reviewer B title mismatch")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_rows(
        args.output_dir / "included.csv",
        included_fields,
        corrected_included,
    )
    write_rows(
        args.output_dir / "study-extraction.csv",
        extraction_fields,
        [extraction_by_id[candidate_id] for candidate_id in empirical_ids],
    )
    write_rows(
        args.output_dir / "medwm-eval-final.csv",
        medwm_final_fields,
        [medwm_final_by_id[candidate_id] for candidate_id in empirical_ids],
    )
    write_rows(
        args.output_dir / "medwm-pilot-reviewer-a.csv",
        reviewer_fields_a,
        [reviewer_a_by_id[candidate_id] for candidate_id in empirical_ids],
    )
    write_rows(
        args.output_dir / "medwm-pilot-reviewer-b.csv",
        reviewer_fields_a,
        [reviewer_b_by_id[candidate_id] for candidate_id in empirical_ids],
    )
    summary = {
        "status": "staging_validated",
        "included_total": len(corrected_included),
        "included_empirical": len(empirical_ids),
        "included_reviews": len(review_ids),
        "existing_publications": len(existing_included),
        "novel_publications": len(corrected_included) - len(existing_included),
        "novel_empirical": len(novel_empirical_ids),
        "extraction_records": len(extraction_by_id),
        "medwm_final_records": len(medwm_final_by_id),
        "reviewer_a_records": len(reviewer_a_by_id),
        "reviewer_b_records": len(reviewer_b_by_id),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
