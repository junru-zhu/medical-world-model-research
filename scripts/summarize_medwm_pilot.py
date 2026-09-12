#!/usr/bin/env python3
"""Summarize an adjudicated MedWM-Eval pilot coding table."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ORDINAL_FIELDS = [
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
]
FEATURE_FIELDS = [
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
]


def count_yes(rows: list[dict[str, str]], field: str) -> dict[str, Any]:
    values = [row[field] for row in rows]
    applicable = [value for value in values if value != "NA"]
    known = [
        value for value in applicable if value not in {"NI", "unclear"}
    ]
    yes = sum(value == "yes" for value in values)
    return {
        "yes": yes,
        "total_denominator": len(values),
        "applicable_denominator": len(applicable),
        "known_denominator": len(known),
        "percent_of_applicable": (
            100 * yes / len(applicable) if applicable else None
        ),
        "percent_of_known": 100 * yes / len(known) if known else None,
        "distribution": dict(sorted(Counter(values).items())),
    }


def count_joint_yes(
    rows: list[dict[str, str]], fields: list[str]
) -> dict[str, Any]:
    matching = [
        row["candidate_id"]
        for row in rows
        if all(row[field] == "yes" for field in fields)
    ]
    return {
        "fields": fields,
        "yes": len(matching),
        "total_denominator": len(rows),
        "candidate_ids": matching,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudicated", type=Path, required=True)
    parser.add_argument(
        "--annotations",
        type=Path,
        help=(
            "Optional analysis annotation table containing candidate_id and "
            "corpus_boundary."
        ),
    )
    parser.add_argument(
        "--corpus-boundary",
        choices=["strict_core", "extended_peripheral"],
        help="If set, retain only records with this corpus boundary.",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    with args.adjudicated.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Missing adjudicated CSV header.")
        rows = list(reader)
    if not rows:
        raise ValueError("No adjudicated rows.")
    if args.corpus_boundary and not args.annotations:
        raise ValueError("--corpus-boundary requires --annotations.")
    if args.annotations:
        with args.annotations.open(newline="", encoding="utf-8") as handle:
            annotations = {
                row["candidate_id"]: row for row in csv.DictReader(handle)
            }
        row_ids = {row["candidate_id"] for row in rows}
        if row_ids != set(annotations):
            raise ValueError(
                "Adjudicated and annotation candidate IDs do not match."
            )
        if args.corpus_boundary:
            rows = [
                row
                for row in rows
                if annotations[row["candidate_id"]]["corpus_boundary"]
                == args.corpus_boundary
            ]
            if not rows:
                raise ValueError(
                    f"No rows retained for {args.corpus_boundary}."
                )

    required = {"candidate_id", "title", "highest_capability_claim"}
    required.update(ORDINAL_FIELDS)
    required.update(FEATURE_FIELDS)
    missing = required - set(reader.fieldnames)
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    for row in rows:
        blank = [field for field in required if not row[field].strip()]
        if blank:
            raise ValueError(
                f"{row['candidate_id']} has blank adjudicated fields: {blank}"
            )

    capabilities = dict(
        sorted(Counter(row["highest_capability_claim"] for row in rows).items())
    )
    ordinal = {
        field: dict(sorted(Counter(row[field] for row in rows).items()))
        for field in ORDINAL_FIELDS
    }
    features: dict[str, Any] = {}
    for field in FEATURE_FIELDS:
        if field == "closed_loop_evaluation":
            features[field] = {
                "distribution": dict(
                    sorted(Counter(row[field] for row in rows).items())
                )
            }
        else:
            features[field] = count_yes(rows, field)
    uncertainty_reporting_rows = [
        row for row in rows if row["uncertainty_evidence"] in {"1", "2"}
    ]
    uncertainty_reporting_subset = {
        "definition": (
            "Studies with partial or directly auditable uncertainty evidence "
            "under the MedWM-Eval coding."
        ),
        "records": len(uncertainty_reporting_rows),
        "formal_calibration_yes": sum(
            row["formal_calibration"] == "yes"
            for row in uncertainty_reporting_rows
        ),
        "all_four_yes": sum(
            all(
                row[field] == "yes"
                for field in (
                    "free_running_rollout",
                    "horizon_resolved_results",
                    "formal_calibration",
                    "frozen_external_validation",
                )
            )
            for row in uncertainty_reporting_rows
        ),
        "candidate_ids": [
            row["candidate_id"] for row in uncertainty_reporting_rows
        ],
    }
    applicability_tracks = {
        "all_empirical_dynamics": {
            "records": len(rows),
            "candidate_ids": [row["candidate_id"] for row in rows],
        },
        "operational_action_input": {
            "definition": (
                "Action comparator field is applicable rather than NA."
            ),
            "records": sum(
                row["action_agnostic_comparator"] != "NA" for row in rows
            ),
            "candidate_ids": [
                row["candidate_id"]
                for row in rows
                if row["action_agnostic_comparator"] != "NA"
            ],
        },
        "causal_or_policy_applicable": {
            "definition": (
                "Explicit causal-estimand field is applicable rather than NA. "
                "This includes patient or biomedical intervention contrasts "
                "and policy-value claims, while procedural control without a "
                "causal outcome interpretation is coded NA."
            ),
            "records": sum(
                row["explicit_causal_estimand"] != "NA" for row in rows
            ),
            "candidate_ids": [
                row["candidate_id"]
                for row in rows
                if row["explicit_causal_estimand"] != "NA"
            ],
        },
        "planning_highest_claim": {
            "records": sum(
                row["highest_capability_claim"] == "planning" for row in rows
            ),
            "candidate_ids": [
                row["candidate_id"]
                for row in rows
                if row["highest_capability_claim"] == "planning"
            ],
        },
    }

    payload = {
        "records": len(rows),
        "corpus_boundary": args.corpus_boundary or "extended_all",
        "capability_claims": capabilities,
        "ordinal_evidence_domains": ordinal,
        "descriptive_features": features,
        "uncertainty_reporting_subset": uncertainty_reporting_subset,
        "applicability_tracks": applicability_tracks,
        "joint_evidence_intersections": {
            "rollout_horizon_calibration": count_joint_yes(
                rows,
                [
                    "free_running_rollout",
                    "horizon_resolved_results",
                    "formal_calibration",
                ],
            ),
            "rollout_horizon_external": count_joint_yes(
                rows,
                [
                    "free_running_rollout",
                    "horizon_resolved_results",
                    "frozen_external_validation",
                ],
            ),
            "calibration_external": count_joint_yes(
                rows,
                [
                    "formal_calibration",
                    "frozen_external_validation",
                ],
            ),
            "rollout_horizon_calibration_external": count_joint_yes(
                rows,
                [
                    "free_running_rollout",
                    "horizon_resolved_results",
                    "formal_calibration",
                    "frozen_external_validation",
                ],
            ),
        },
        "denominator_note": (
            "Total is the full empirical corpus. Applicable excludes only NA. "
            "Known additionally excludes NI and unclear. Confirmed-yes counts "
            "are reported against the applicable denominator unless a display "
            "explicitly uses the total corpus."
        ),
        "interpretation_note": (
            "Counts describe reported evidence in the inspected primary text. "
            "They do not prove that unreported work was not performed."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# MedWM-Eval Pilot Synthesis",
        "",
        f"Empirical studies: {len(rows)}",
        "",
        "## Highest Capability Claim",
        "",
        "| Capability | Studies |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {capability.replace('_', ' ')} | {count} |"
        for capability, count in capabilities.items()
    )
    lines.extend(
        [
            "",
            "## Descriptive Evidence Features",
            "",
            "| Feature | Confirmed yes | Total | Applicable | Known | Yes / applicable |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for field in FEATURE_FIELDS:
        if field == "closed_loop_evaluation":
            continue
        item = features[field]
        percent = (
            f"{item['percent_of_applicable']:.1f}%"
            if item["percent_of_applicable"] is not None
            else "NA"
        )
        lines.append(
            f"| {field.replace('_', ' ')} | {item['yes']} | "
            f"{item['total_denominator']} | "
            f"{item['applicable_denominator']} | "
            f"{item['known_denominator']} | {percent} |"
        )
    lines.extend(
        [
            "",
            "## Applicability and Calibration Sensitivity",
            "",
            (
                "The uncertainty-reporting subset contains "
                f"{uncertainty_reporting_subset['records']} studies; "
                f"{uncertainty_reporting_subset['formal_calibration_yes']} "
                "reported formal calibration and "
                f"{uncertainty_reporting_subset['all_four_yes']} combined all "
                "four benchmark criteria."
            ),
            "",
            (
                "Operational action-input track: "
                f"{applicability_tracks['operational_action_input']['records']} "
                "studies."
            ),
            (
                "Causal or policy-applicable track: "
                f"{applicability_tracks['causal_or_policy_applicable']['records']} "
                "studies."
            ),
            "",
            "## Joint Evidence Intersections",
            "",
            "| Joint criterion | Studies | Total corpus |",
            "| --- | ---: | ---: |",
            (
                "| Free-running rollout + horizon-resolved results + "
                "formal calibration | "
                f"{payload['joint_evidence_intersections']['rollout_horizon_calibration']['yes']} "
                f"| {len(rows)} |"
            ),
            (
                "| Free-running rollout + horizon-resolved results + "
                "frozen external validation | "
                f"{payload['joint_evidence_intersections']['rollout_horizon_external']['yes']} "
                f"| {len(rows)} |"
            ),
            (
                "| Formal calibration + frozen external validation | "
                f"{payload['joint_evidence_intersections']['calibration_external']['yes']} "
                f"| {len(rows)} |"
            ),
            (
                "| All four criteria | "
                f"{payload['joint_evidence_intersections']['rollout_horizon_calibration_external']['yes']} "
                f"| {len(rows)} |"
            ),
            "",
            "Closed-loop setting distribution: "
            + "; ".join(
                f"{key}={value}"
                for key, value in features[
                    "closed_loop_evaluation"
                ]["distribution"].items()
            ),
            "",
            payload["denominator_note"],
            "",
            "Counts describe reported evidence in the inspected primary text; "
            "absence of reporting is not proof that work was not performed.",
        ]
    )
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(rows), "output": str(args.output_json)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
