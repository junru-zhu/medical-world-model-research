#!/usr/bin/env python3
"""Validate provisional extraction and MedWM-Eval coding artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXTRACTION_FIELDS = [
    "candidate_id",
    "title",
    "primary_source_url",
    "publication_status",
    "domain",
    "dataset_or_cohort",
    "sample_scale",
    "institution_count",
    "split_strategy",
    "observation_process",
    "missingness",
    "censoring_or_competing_events",
    "state",
    "observation_decoder",
    "action",
    "action_provenance",
    "transition_mechanism",
    "maximum_horizon",
    "rollout_regime",
    "capability_claim",
    "baselines",
    "state_fidelity_metrics",
    "transition_metrics",
    "rollout_stability",
    "action_sensitivity",
    "calibration_and_uncertainty",
    "external_validation",
    "decision_utility",
    "safety_evaluation",
    "statistical_analysis",
    "causal_language",
    "estimand",
    "confounding_strategy",
    "positivity_and_overlap",
    "counterfactual_validation",
    "code_access",
    "weights_access",
    "data_access",
    "preprocessing_reproducibility",
    "randomness",
    "evidence_anchors",
    "appraisal_strengths",
    "appraisal_limitations",
    "source_status",
    "reviewer_confidence",
]

MEDWM_FIELDS = [
    "candidate_id",
    "title",
    "highest_capability_claim",
    "state_evidence",
    "dynamics_evidence",
    "rollout_evidence",
    "action_evidence",
    "uncertainty_evidence",
    "causal_evidence",
    "external_evidence",
    "decision_evidence",
    "safety_evidence",
    "reproducibility_evidence",
    "free_running_rollout",
    "horizon_resolved_results",
    "formal_calibration",
    "frozen_external_validation",
    "action_agnostic_comparator",
    "action_perturbation",
    "explicit_causal_estimand",
    "closed_loop_evaluation",
    "safety_hazard_test",
    "public_code",
    "evidence_anchors",
    "reviewer_notes",
    "confidence",
]

MEDWM_ADJUDICATED_FIELDS = MEDWM_FIELDS[:23] + [
    "disagreement_fields",
    "reviewer_a_anchors",
    "reviewer_b_anchors",
    "adjudication_anchors",
    "adjudication_notes",
    "confidence",
]

ORDINAL_FIELDS = {
    "state_evidence",
    "dynamics_evidence",
    "rollout_evidence",
    "action_evidence",
    "uncertainty_evidence",
    "causal_evidence",
    "external_evidence",
    "decision_evidence",
    "safety_evidence",
    "reproducibility_evidence",
}

ALLOWED = {
    "highest_capability_claim": {
        "passive_forecasting",
        "action_conditioned",
        "counterfactual",
        "planning",
    },
    "free_running_rollout": {"yes", "no", "unclear"},
    "horizon_resolved_results": {"yes", "no", "unclear"},
    "formal_calibration": {"yes", "no", "unclear"},
    "frozen_external_validation": {"yes", "no", "unclear"},
    "action_agnostic_comparator": {"yes", "no", "NA", "unclear"},
    "action_perturbation": {"yes", "no", "NA", "unclear"},
    "explicit_causal_estimand": {"yes", "no", "NA", "unclear"},
    "closed_loop_evaluation": {"real", "simulation", "offline", "no", "unclear"},
    "safety_hazard_test": {"yes", "no", "unclear"},
    "public_code": {"yes", "no", "unclear"},
    "confidence": {"high", "medium", "low"},
}
for field in ORDINAL_FIELDS:
    ALLOWED[field] = {"0", "1", "2", "NA", "NI"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError(f"{path}: expected a list of objects")
    return data


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_pair(
    *,
    csv_path: Path,
    json_path: Path,
    expected_fields: list[str],
    expected_ids: set[str],
    errors: list[str],
) -> list[dict[str, str]]:
    fields, csv_rows = read_csv(csv_path)
    json_rows = read_json(json_path)

    require(fields == expected_fields, f"{csv_path}: unexpected field order", errors)
    require(len(csv_rows) == len(expected_ids), f"{csv_path}: unexpected row count", errors)
    require(len(json_rows) == len(expected_ids), f"{json_path}: unexpected row count", errors)

    csv_ids = [row.get("candidate_id", "") for row in csv_rows]
    json_ids = [str(row.get("candidate_id", "")) for row in json_rows]
    require(len(csv_ids) == len(set(csv_ids)), f"{csv_path}: duplicate candidate_id", errors)
    require(len(json_ids) == len(set(json_ids)), f"{json_path}: duplicate candidate_id", errors)
    require(set(csv_ids) == expected_ids, f"{csv_path}: candidate_id set mismatch", errors)
    require(set(json_ids) == expected_ids, f"{json_path}: candidate_id set mismatch", errors)

    normalized_json = [
        {field: str(row.get(field, "")) for field in expected_fields} for row in json_rows
    ]
    normalized_csv = [
        {field: row.get(field, "") for field in expected_fields} for row in csv_rows
    ]
    require(
        normalized_csv == normalized_json,
        f"{csv_path}: CSV content does not match JSON source",
        errors,
    )
    for index, row in enumerate(csv_rows, start=2):
        blanks = [field for field in expected_fields if not row.get(field, "").strip()]
        require(not blanks, f"{csv_path}:{index}: blank fields {blanks}", errors)
    return csv_rows


def validate_csv_only(
    *,
    path: Path,
    expected_fields: list[str],
    expected_ids: set[str],
    errors: list[str],
    allow_blank_fields: set[str] | None = None,
) -> list[dict[str, str]]:
    allow_blank_fields = allow_blank_fields or set()
    fields, rows = read_csv(path)
    require(fields == expected_fields, f"{path}: unexpected field order", errors)
    ids = [row.get("candidate_id", "") for row in rows]
    require(len(rows) == len(expected_ids), f"{path}: unexpected row count", errors)
    require(len(ids) == len(set(ids)), f"{path}: duplicate candidate_id", errors)
    require(set(ids) == expected_ids, f"{path}: candidate_id set mismatch", errors)
    for index, row in enumerate(rows, start=2):
        blanks = [
            field
            for field in expected_fields
            if field not in allow_blank_fields and not row.get(field, "").strip()
        ]
        require(not blanks, f"{path}:{index}: blank fields {blanks}", errors)
    return rows


def validate_medwm_codes(
    *, path: Path, rows: list[dict[str, str]], errors: list[str]
) -> None:
    for index, row in enumerate(rows, start=2):
        for field, allowed in ALLOWED.items():
            require(
                row[field] in allowed,
                f"{path}:{index}: invalid {field}={row[field]!r}",
                errors,
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/"
            "screening/provisional-new-records"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path; defaults to BASE/validation.json.",
    )
    args = parser.parse_args()
    base = args.base
    errors: list[str] = []

    novel_fields, novel_rows = read_csv(base / "novel-empirical.csv")
    require("candidate_id" in novel_fields, "novel-empirical.csv: candidate_id missing", errors)
    expected_ids = {row["candidate_id"] for row in novel_rows}
    require(len(expected_ids) == 5, "novel-empirical.csv: expected five unique records", errors)

    extraction_rows = validate_pair(
        csv_path=base / "study-extraction-reviewer-a.csv",
        json_path=base / "study-extraction-reviewer-a.json",
        expected_fields=EXTRACTION_FIELDS,
        expected_ids=expected_ids,
        errors=errors,
    )
    medwm_rows = validate_pair(
        csv_path=base / "medwm-eval-reviewer-a.csv",
        json_path=base / "medwm-eval-reviewer-a.json",
        expected_fields=MEDWM_FIELDS,
        expected_ids=expected_ids,
        errors=errors,
    )

    extraction_titles = {row["candidate_id"]: row["title"] for row in extraction_rows}
    for index, row in enumerate(medwm_rows, start=2):
        require(
            row["title"] == extraction_titles.get(row["candidate_id"]),
            f"medwm-eval-reviewer-a.csv:{index}: title mismatch",
            errors,
        )
    validate_medwm_codes(
        path=base / "medwm-eval-reviewer-a.csv",
        rows=medwm_rows,
        errors=errors,
    )

    artifacts: dict[str, str] = {
        "reviewer_a_extraction": "pass",
        "reviewer_a_medwm": "pass",
        "reviewer_b_extraction": "pending",
        "reviewer_b_medwm": "pending",
        "adjudicated_extraction": "pending",
        "adjudicated_medwm": "pending",
    }
    reviewer_b_extraction_path = base / "study-extraction-reviewer-b.csv"
    reviewer_b_medwm_path = base / "medwm-eval-reviewer-b.csv"
    if reviewer_b_extraction_path.exists():
        reviewer_b_extraction = validate_csv_only(
            path=reviewer_b_extraction_path,
            expected_fields=EXTRACTION_FIELDS,
            expected_ids=expected_ids,
            errors=errors,
        )
        artifacts["reviewer_b_extraction"] = "pass"
    else:
        reviewer_b_extraction = []
    if reviewer_b_medwm_path.exists():
        reviewer_b_medwm = validate_csv_only(
            path=reviewer_b_medwm_path,
            expected_fields=MEDWM_FIELDS,
            expected_ids=expected_ids,
            errors=errors,
        )
        validate_medwm_codes(
            path=reviewer_b_medwm_path,
            rows=reviewer_b_medwm,
            errors=errors,
        )
        artifacts["reviewer_b_medwm"] = "pass"
    else:
        reviewer_b_medwm = []
    if reviewer_b_extraction and reviewer_b_medwm:
        titles_b = {
            row["candidate_id"]: row["title"] for row in reviewer_b_extraction
        }
        for index, row in enumerate(reviewer_b_medwm, start=2):
            require(
                row["title"] == titles_b.get(row["candidate_id"]),
                f"{reviewer_b_medwm_path}:{index}: title mismatch",
                errors,
            )

    adjudicated_extraction_path = base / "study-extraction-adjudicated.csv"
    adjudicated_medwm_path = base / "medwm-eval-adjudicated.csv"
    if adjudicated_extraction_path.exists():
        adjudicated_extraction = validate_csv_only(
            path=adjudicated_extraction_path,
            expected_fields=EXTRACTION_FIELDS,
            expected_ids=expected_ids,
            errors=errors,
        )
        artifacts["adjudicated_extraction"] = "pass"
    else:
        adjudicated_extraction = []
    if adjudicated_medwm_path.exists():
        adjudicated_medwm = validate_csv_only(
            path=adjudicated_medwm_path,
            expected_fields=MEDWM_ADJUDICATED_FIELDS,
            expected_ids=expected_ids,
            errors=errors,
            allow_blank_fields={"disagreement_fields"},
        )
        validate_medwm_codes(
            path=adjudicated_medwm_path,
            rows=adjudicated_medwm,
            errors=errors,
        )
        artifacts["adjudicated_medwm"] = "pass"
    else:
        adjudicated_medwm = []
    if adjudicated_extraction and adjudicated_medwm:
        adjudicated_titles = {
            row["candidate_id"]: row["title"] for row in adjudicated_extraction
        }
        for index, row in enumerate(adjudicated_medwm, start=2):
            require(
                row["title"] == adjudicated_titles.get(row["candidate_id"]),
                f"{adjudicated_medwm_path}:{index}: title mismatch",
                errors,
            )

    result = {
        "status": "pass" if not errors else "fail",
        "records": len(expected_ids),
        "extraction_fields": len(EXTRACTION_FIELDS),
        "medwm_fields": len(MEDWM_FIELDS),
        "artifacts": artifacts,
        "errors": errors,
    }
    output = args.output or (base / "validation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
