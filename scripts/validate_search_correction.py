#!/usr/bin/env python3
"""Validate the staged discovery-filter correction without freezing the corpus."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


TITLE_DECISIONS = {"include", "exclude", "uncertain"}
FULLTEXT_TYPES = {"empirical", "review", "not_applicable", "uncertain"}
FULLTEXT_REASONS = {
    "include_empirical",
    "include_review",
    "wrong_domain",
    "no_learned_dynamics",
    "no_future_or_action_evaluation",
    "no_primary_empirical_evaluation",
    "review_not_primary",
    "duplicate_publication",
    "inaccessible_full_text",
    "unstable_record",
    "uncertain",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_stage_summary(
    path: Path,
    *,
    expected_records: int,
    expected_initially_included: int | None = None,
) -> dict[str, Any]:
    if not path.exists():
        return {"status": "pending"}
    summary = read_json(path)
    errors: list[str] = []
    if summary.get("records") != expected_records:
        errors.append(
            f"records {summary.get('records')} != {expected_records}"
        )
    if expected_initially_included is not None:
        if summary.get("initially_included") != expected_initially_included:
            errors.append(
                "initially_included "
                f"{summary.get('initially_included')} != "
                f"{expected_initially_included}"
            )
        if (
            summary.get("qc_retained", 0) + summary.get("qc_removed", 0)
            != expected_initially_included
        ):
            errors.append("qc_retained + qc_removed mismatch")
        if (
            summary.get("included_empirical", 0)
            + summary.get("included_reviews", 0)
            != summary.get("qc_retained", 0)
        ):
            errors.append("QC included type counts do not equal qc_retained")
    elif "included_total" in summary:
        if (
            summary.get("included_total", 0) + summary.get("excluded_total", 0)
            != expected_records
        ):
            errors.append("included_total + excluded_total mismatch")
        if (
            summary.get("included_empirical", 0)
            + summary.get("included_reviews", 0)
            != summary.get("included_total", 0)
        ):
            errors.append("included type counts do not equal included_total")
    return {
        "status": "complete" if not errors else "fail",
        "summary": summary,
        "errors": errors,
    }


def validate_rows(
    *,
    path: Path,
    expected_ids: list[str],
    fulltext: bool,
) -> dict[str, Any]:
    if not path.exists():
        return {"status": "pending", "path": str(path)}
    rows = read_csv(path)
    ids = [row.get("audit_id", "") for row in rows]
    errors: list[str] = []
    if len(rows) != len(expected_ids):
        errors.append(f"expected {len(expected_ids)} rows, found {len(rows)}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate audit_id")
    if ids != expected_ids:
        errors.append("audit_id order or membership mismatch")
    for index, row in enumerate(rows, start=2):
        decision = row.get("decision", "")
        if decision not in TITLE_DECISIONS:
            errors.append(f"row {index}: invalid decision {decision!r}")
        if fulltext:
            corpus_type = row.get("corpus_type", "")
            reason = row.get("reason_code", "")
            confidence = row.get("confidence", "")
            if corpus_type not in FULLTEXT_TYPES:
                errors.append(f"row {index}: invalid corpus_type {corpus_type!r}")
            if reason not in FULLTEXT_REASONS:
                errors.append(f"row {index}: invalid reason_code {reason!r}")
            if confidence not in {"high", "medium", "low"}:
                errors.append(f"row {index}: invalid confidence {confidence!r}")
    return {
        "status": "pass" if not errors else "fail",
        "path": str(path),
        "records": len(rows),
        "decision_distribution": dict(sorted(Counter(row.get("decision", "") for row in rows).items())),
        "errors": errors,
    }


def validate_track(
    *,
    root: Path,
    directory: str,
    title_reviewers: list[str],
    fulltext_reviewers: list[str],
    expected_records: int,
    expected_follow_up: int,
) -> dict[str, Any]:
    base = root / "screening" / directory
    candidates = read_csv(base / "candidates.csv")
    candidate_ids = [row["audit_id"] for row in candidates]
    comparison_candidates = read_csv(base / "comparison" / "full-text-candidates.csv")
    comparison_ids = [row["audit_id"] for row in comparison_candidates]
    agreement = read_json(base / "comparison" / "agreement-summary.json")

    errors: list[str] = []
    if len(candidates) != expected_records:
        errors.append(f"candidate count {len(candidates)} != {expected_records}")
    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append("candidate audit_id values are not unique")
    if len(comparison_candidates) != expected_follow_up:
        errors.append(
            f"full-text follow-up count {len(comparison_candidates)} != {expected_follow_up}"
        )
    if agreement.get("conservative_full_text_follow_up") != expected_follow_up:
        errors.append("agreement summary follow-up count mismatch")

    title_results = {
        name: validate_rows(
            path=base / f"{name}.csv",
            expected_ids=candidate_ids,
            fulltext=False,
        )
        for name in title_reviewers
    }
    fulltext_results = {
        name: validate_rows(
            path=base / f"{name}.csv",
            expected_ids=comparison_ids,
            fulltext=True,
        )
        for name in fulltext_reviewers
    }
    fulltext_comparison_path = base / "fulltext-comparison" / "agreement-summary.json"
    if fulltext_comparison_path.exists():
        fulltext_comparison_summary = read_json(fulltext_comparison_path)
        required_adjudications = int(
            fulltext_comparison_summary.get("requires_adjudication", 0)
        )
        third_path = base / "fulltext-comparison" / "third-adjudications.csv"
        required_path = (
            base / "fulltext-comparison" / "adjudication-required.csv"
        )
        required_rows = read_csv(required_path)
        required_ids = [row["audit_id"] for row in required_rows]
        if third_path.exists():
            third_rows = read_csv(third_path)
            third_ids = [row.get("audit_id", "") for row in third_rows]
            third_errors: list[str] = []
            if len(third_rows) != required_adjudications:
                third_errors.append(
                    f"expected {required_adjudications} rows, "
                    f"found {len(third_rows)}"
                )
            if third_ids != required_ids:
                third_errors.append("audit_id order or membership mismatch")
            if len(third_ids) != len(set(third_ids)):
                third_errors.append("duplicate audit_id")
            for index, row in enumerate(third_rows, start=2):
                if row.get("final_decision") not in {"include", "exclude"}:
                    third_errors.append(
                        f"row {index}: invalid final_decision"
                    )
                if row.get("final_corpus_type") not in {
                    "empirical",
                    "review",
                    "not_applicable",
                }:
                    third_errors.append(
                        f"row {index}: invalid final_corpus_type"
                    )
                if row.get("final_reason_code") not in FULLTEXT_REASONS:
                    third_errors.append(
                        f"row {index}: invalid final_reason_code"
                    )
                if not row.get("adjudication_rationale", "").strip():
                    third_errors.append(
                        f"row {index}: blank adjudication_rationale"
                    )
            third_status = {
                "status": "complete" if not third_errors else "fail",
                "records": len(third_rows),
                "expected": required_adjudications,
                "path": str(third_path),
                "errors": third_errors,
            }
        else:
            third_status = {
                "status": "pending",
                "expected": required_adjudications,
                "path": str(third_path),
            }
        fulltext_comparison = {
            "status": "complete",
            "summary": fulltext_comparison_summary,
            "third_adjudication": third_status,
        }
    else:
        fulltext_comparison = {"status": "pending"}
    final_status = validate_stage_summary(
        base / "final" / "summary.json",
        expected_records=len(comparison_candidates),
    )
    raw_included = (
        final_status.get("summary", {}).get("included_total")
        if final_status["status"] == "complete"
        else None
    )
    qc_status = validate_stage_summary(
        base / "qc-final" / "summary.json",
        expected_records=len(comparison_candidates),
        expected_initially_included=raw_included,
    )
    resolved_status = validate_stage_summary(
        base / "resolved-final" / "summary.json",
        expected_records=len(comparison_candidates),
    )
    for stage in (final_status, qc_status, resolved_status):
        if stage["status"] == "fail":
            errors.extend(stage.get("errors", []))
    track_complete = resolved_status["status"] == "complete"
    return {
        "status": "fail" if errors else ("complete" if track_complete else "in_progress"),
        "candidate_records": len(candidates),
        "full_text_follow_up": len(comparison_candidates),
        "agreement": {
            "raw_agreement": agreement.get("raw_agreement"),
            "cohen_kappa": agreement.get("cohen_kappa"),
            "disagreements": agreement.get("disagreements"),
        },
        "title_abstract_reviewers": title_results,
        "fulltext_reviewers": fulltext_results,
        "fulltext_comparison": fulltext_comparison,
        "raw_final_adjudication": final_status,
        "independent_inclusion_qc": qc_status,
        "resolved_final": resolved_status,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("output/literature-search/medical-world-models"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/"
            "screening/search-correction-validation.json"
        ),
    )
    args = parser.parse_args()

    sampled_summary = read_json(
        args.root / "screening/discovery-filter-audit/resolved-final/summary.json"
    )
    result = {
        "status": "search_correction_in_progress",
        "sampled_audit": {
            "status": "complete",
            "included": sampled_summary.get("included_total"),
            "empirical": sampled_summary.get("included_empirical"),
            "reviews": sampled_summary.get("included_reviews"),
            "excluded": sampled_summary.get("excluded_total"),
        },
        "expanded_alternate_search": validate_track(
            root=args.root,
            directory="expanded-search-screening",
            title_reviewers=["reviewer-c", "reviewer-d"],
            fulltext_reviewers=["fulltext-reviewer-g", "fulltext-reviewer-h"],
            expected_records=1030,
            expected_follow_up=198,
        ),
        "exhaustive_filter_rescreen": validate_track(
            root=args.root,
            directory="exhaustive-exclusion-rescreen",
            title_reviewers=["reviewer-e", "reviewer-f"],
            fulltext_reviewers=["fulltext-reviewer-i", "fulltext-reviewer-j"],
            expected_records=5079,
            expected_follow_up=119,
        ),
        "corpus_freeze_allowed": False,
    }
    tracks = [result["expanded_alternate_search"], result["exhaustive_filter_rescreen"]]
    failures = [
        track
        for track in tracks
        if track["status"] == "fail"
        or any(
            reviewer["status"] == "fail"
            for section in ("title_abstract_reviewers", "fulltext_reviewers")
            for reviewer in track[section].values()
        )
        or track.get("fulltext_comparison", {})
        .get("third_adjudication", {})
        .get("status")
        == "fail"
    ]
    if failures:
        result["status"] = "fail"
    elif all(track["status"] == "complete" for track in tracks):
        result["status"] = "search_screening_complete_downstream_pending"
    result["search_screening_complete"] = all(
        track["status"] == "complete" for track in tracks
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
