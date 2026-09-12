#!/usr/bin/env python3
"""Create capability, domain, boundary, and source-status sensitivity analyses."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


BOUNDARY_IDS = {"MWM-0012", "MWM-0135", "MWM-0261"}
PEER_REVIEWED_IDS = {
    "MWM-0114",
    "MWM-0215",
    "MWM-0263",
    "MWM-0290",
    "MWM-0294",
    "MWM-0315",
    "MWM-0369",
    "MWM-S003",
    "MWM-S005",
    "MWM-S006",
}
DOMAIN_IDS = {
    "longitudinal_physiology_decision": {
        "MWM-0013",
        "MWM-0040",
        "MWM-0046",
        "MWM-0073",
        "MWM-0074",
        "MWM-0094",
        "MWM-0095",
        "MWM-0103",
        "MWM-0114",
        "MWM-0149",
        "MWM-0164",
        "MWM-0200",
        "MWM-0215",
        "MWM-0369",
    },
    "imaging_biological": {
        "MWM-0008",
        "MWM-0018",
        "MWM-0032",
        "MWM-0034",
        "MWM-0077",
        "MWM-0125",
        "MWM-0132",
        "MWM-0166",
        "MWM-0239",
        "MWM-0263",
        "MWM-0290",
        "MWM-S002",
        "MWM-S003",
    },
    "procedural_embodied": {
        "MWM-0011",
        "MWM-0054",
        "MWM-0068",
        "MWM-0078",
        "MWM-0136",
        "MWM-0138",
        "MWM-0151",
        "MWM-0157",
        "MWM-0170",
        "MWM-0173",
        "MWM-0174",
        "MWM-0175",
        "MWM-0177",
        "MWM-0199",
        "MWM-0242",
        "MWM-0294",
        "MWM-0315",
        "MWM-S004",
        "MWM-S005",
        "MWM-S006",
    },
    "peripheral_health_adjacent": BOUNDARY_IDS,
}
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
    "safety_hazard_test",
    "public_code",
]
DISPLAY_FEATURES = [
    "free_running_rollout",
    "horizon_resolved_results",
    "formal_calibration",
    "frozen_external_validation",
    "explicit_causal_estimand",
    "safety_hazard_test",
]
WORLD_RE = re.compile(r"\bworld[\s-]+models?\b", re.IGNORECASE)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def domain_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for domain, ids in DOMAIN_IDS.items():
        for candidate_id in ids:
            if candidate_id in mapping:
                raise ValueError(f"Duplicate domain coding for {candidate_id}")
            mapping[candidate_id] = domain
    return mapping


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    summary: dict[str, object] = {
        "records": len(rows),
        "capability_claims": dict(
            sorted(Counter(row["highest_capability_claim"] for row in rows).items())
        ),
        "features": {},
    }
    for field in FEATURE_FIELDS:
        distribution = Counter(row[field] for row in rows)
        eligible = sum(value != "NA" for value in (row[field] for row in rows))
        summary["features"][field] = {
            "yes": distribution.get("yes", 0),
            "eligible": eligible,
            "unclear": distribution.get("unclear", 0),
            "distribution": dict(sorted(distribution.items())),
        }
    return summary


def cross_tab(
    rows: list[dict[str, str]], group_field: str
) -> dict[str, dict[str, object]]:
    groups = sorted({row[group_field] for row in rows})
    result: dict[str, dict[str, object]] = {}
    for group in groups:
        subset = [row for row in rows if row[group_field] == group]
        item: dict[str, object] = {"records": len(subset), "ordinal": {}, "features": {}}
        for field in ORDINAL_FIELDS:
            distribution = Counter(row[field] for row in subset)
            applicable = sum(row[field] != "NA" for row in subset)
            item["ordinal"][field] = {
                "strong": distribution.get("2", 0),
                "partial": distribution.get("1", 0),
                "absent": distribution.get("0", 0),
                "not_applicable": distribution.get("NA", 0),
                "applicable": applicable,
            }
        for field in DISPLAY_FEATURES:
            distribution = Counter(row[field] for row in subset)
            item["features"][field] = {
                "yes": distribution.get("yes", 0),
                "no": distribution.get("no", 0),
                "unclear": distribution.get("unclear", 0),
                "not_applicable": distribution.get("NA", 0),
            }
        result[group] = item
    return result


def applicability_joint_gap(
    rows: list[dict[str, str]],
) -> tuple[dict[str, object], list[dict[str, str]]]:
    """Post hoc sensitivity for probabilistic multistep rollout studies.

    This is deliberately labeled as an operational sensitivity subset rather
    than a universal applicability rule. It restricts the descriptive
    four-feature intersection to studies that already report at least partial
    uncertainty evidence, free-running rollout, and horizon-resolved results.
    """

    subset = [
        row
        for row in rows
        if row["uncertainty_evidence"] in {"1", "2"}
        and row["free_running_rollout"] == "yes"
        and row["horizon_resolved_results"] == "yes"
    ]
    detail_fields = [
        "candidate_id",
        "title",
        "highest_capability_claim",
        "uncertainty_evidence",
        "free_running_rollout",
        "horizon_resolved_results",
        "formal_calibration",
        "frozen_external_validation",
    ]
    details = [
        {field: row[field] for field in detail_fields}
        for row in subset
    ]
    external_distribution = Counter(
        row["frozen_external_validation"] for row in subset
    )
    calibration_yes = sum(
        row["formal_calibration"] == "yes" for row in subset
    )
    external_yes = external_distribution.get("yes", 0)
    joint_yes = sum(
        row["formal_calibration"] == "yes"
        and row["frozen_external_validation"] == "yes"
        for row in subset
    )
    return (
        {
            "status": "post_hoc_operational_sensitivity",
            "definition": (
                "Strict-core studies with partial or directly auditable "
                "uncertainty evidence, free-running rollout, and "
                "horizon-resolved results. This subset is not a validated "
                "universal applicability rule."
            ),
            "records": len(subset),
            "formal_calibration_yes": calibration_yes,
            "frozen_external_validation_yes": external_yes,
            "frozen_external_validation_unclear": external_distribution.get(
                "unclear", 0
            ),
            "frozen_external_validation_known": (
                len(subset) - external_distribution.get("unclear", 0)
            ),
            "formal_calibration_and_frozen_external_validation_yes": joint_yes,
            "candidate_ids": [row["candidate_id"] for row in subset],
        },
        details,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--included", type=Path, required=True)
    parser.add_argument(
        "--annotations",
        type=Path,
        help=(
            "Optional explicit candidate_id, domain_group, corpus_boundary, "
            "and source_tier ledger. Required for a changed corpus."
        ),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    pilot = read_csv(args.pilot)
    extraction = {
        row["candidate_id"]: row for row in read_csv(args.extraction)
    }
    included = {
        row["candidate_id"]: row
        for row in read_csv(args.included)
        if row["final_corpus_type"] == "empirical"
    }
    ids = {row["candidate_id"] for row in pilot}
    if ids != set(extraction) or ids != set(included):
        raise ValueError("Pilot, extraction, and included empirical IDs differ.")
    if args.annotations:
        annotation_rows = read_csv(args.annotations)
        annotations = {
            row["candidate_id"]: row for row in annotation_rows
        }
        if len(annotations) != len(annotation_rows):
            raise ValueError("Duplicate candidate_id in analysis annotations.")
        if ids != set(annotations):
            missing = sorted(ids - set(annotations))
            extra = sorted(set(annotations) - ids)
            raise ValueError(
                f"Analysis annotation mismatch; missing={missing}, extra={extra}"
            )
        for candidate_id, annotation in annotations.items():
            blank = [
                field
                for field in (
                    "domain_group",
                    "corpus_boundary",
                    "source_tier",
                )
                if not annotation.get(field, "").strip()
            ]
            if blank:
                raise ValueError(
                    f"Incomplete analysis annotation for {candidate_id}: {blank}"
                )
            if annotation["corpus_boundary"] not in {
                "strict_core",
                "extended_peripheral",
            }:
                raise ValueError(
                    f"Invalid corpus_boundary for {candidate_id}"
                )
            if annotation["source_tier"] not in {
                "peer_reviewed",
                "preprint_or_unreviewed",
            }:
                raise ValueError(f"Invalid source_tier for {candidate_id}")
        mapping = {
            candidate_id: annotation["domain_group"]
            for candidate_id, annotation in annotations.items()
        }
        boundary_ids = {
            candidate_id
            for candidate_id, annotation in annotations.items()
            if annotation["corpus_boundary"] == "extended_peripheral"
        }
        peer_reviewed_ids = {
            candidate_id
            for candidate_id, annotation in annotations.items()
            if annotation["source_tier"] == "peer_reviewed"
        }
    else:
        mapping = domain_map()
        boundary_ids = BOUNDARY_IDS
        peer_reviewed_ids = PEER_REVIEWED_IDS
        if ids != set(mapping):
            missing = sorted(ids - set(mapping))
            extra = sorted(set(mapping) - ids)
            raise ValueError(
                f"Domain coding mismatch; missing={missing}, extra={extra}"
            )

    enriched: list[dict[str, str]] = []
    characteristics: list[dict[str, str]] = []
    for row in pilot:
        candidate_id = row["candidate_id"]
        augmented = dict(row)
        augmented["domain_group"] = mapping[candidate_id]
        augmented["corpus_boundary"] = (
            "extended_peripheral"
            if candidate_id in boundary_ids
            else "strict_core"
        )
        augmented["source_tier"] = (
            "peer_reviewed"
            if candidate_id in peer_reviewed_ids
            else "preprint_or_unreviewed"
        )
        title_abstract = (
            f"{included[candidate_id]['title']} "
            f"{included[candidate_id]['abstract']}"
        )
        augmented["world_model_self_identification"] = (
            "explicit_title_or_abstract"
            if WORLD_RE.search(title_abstract)
            else "reviewer_inferred_lineage"
        )
        enriched.append(augmented)
        characteristics.append(
            {
                "candidate_id": candidate_id,
                "title": row["title"],
                "domain_group": augmented["domain_group"],
                "corpus_boundary": augmented["corpus_boundary"],
                "source_tier": augmented["source_tier"],
                "world_model_self_identification": augmented[
                    "world_model_self_identification"
                ],
                "publication_status": extraction[candidate_id][
                    "publication_status"
                ],
                "reviewer_confidence": extraction[candidate_id][
                    "reviewer_confidence"
                ],
                "closed_loop_evaluation": row["closed_loop_evaluation"],
                "frozen_external_validation": row[
                    "frozen_external_validation"
                ],
                "formal_calibration": row["formal_calibration"],
                "safety_hazard_test": row["safety_hazard_test"],
                "public_code": row["public_code"],
            }
        )

    subsets = {
        "extended_all": enriched,
        "strict_core": [
            row for row in enriched if row["corpus_boundary"] == "strict_core"
        ],
        "peer_reviewed": [
            row for row in enriched if row["source_tier"] == "peer_reviewed"
        ],
        "explicit_world_model": [
            row
            for row in enriched
            if row["world_model_self_identification"]
            == "explicit_title_or_abstract"
        ],
        "high_confidence": [
            row for row in enriched if row["confidence"] == "high"
        ],
    }
    applicability_summary, applicability_details = applicability_joint_gap(
        subsets["strict_core"]
    )
    payload = {
        "coding_notes": {
            "strict_core_exclusions": sorted(boundary_ids),
            "strict_core_definition": (
                "Directly clinical, biomedical, physiological, or medical-"
                "procedural state dynamics. Wellness-only, nonclinical "
                "affective, and mixed synthetic benchmark records are retained "
                "only in the extended sensitivity corpus."
            ),
            "peer_reviewed_ids": sorted(peer_reviewed_ids),
            "source_quality_note": (
                "Publication status is a sensitivity stratum, not a risk-of-"
                "bias score."
            ),
        },
        "subsets": {name: summarize(rows) for name, rows in subsets.items()},
        "capability_by_evidence": cross_tab(
            subsets["strict_core"], "highest_capability_claim"
        ),
        "domain_by_evidence": cross_tab(
            subsets["strict_core"], "domain_group"
        ),
        "extended_capability_by_evidence": cross_tab(
            enriched, "highest_capability_claim"
        ),
        "extended_domain_by_evidence": cross_tab(
            enriched, "domain_group"
        ),
        "applicability_matched_joint_gap": applicability_summary,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "review-sensitivity-analysis.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    with (args.output_dir / "study-characteristics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(characteristics[0]))
        writer.writeheader()
        writer.writerows(characteristics)
    with (args.output_dir / "applicability-joint-gap.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(applicability_details[0]),
        )
        writer.writeheader()
        writer.writerows(applicability_details)

    lines = [
        "# Review Sensitivity Analysis",
        "",
        "## Corpus Boundaries and Source Status",
        "",
        "| Analysis set | Studies | Planning | Action-conditioned | Counterfactual | Passive | Calibration | External validation | Safety test |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, summary in payload["subsets"].items():
        capabilities = summary["capability_claims"]
        features = summary["features"]
        lines.append(
            f"| {name.replace('_', ' ')} | {summary['records']} | "
            f"{capabilities.get('planning', 0)} | "
            f"{capabilities.get('action_conditioned', 0)} | "
            f"{capabilities.get('counterfactual', 0)} | "
            f"{capabilities.get('passive_forecasting', 0)} | "
            f"{features['formal_calibration']['yes']} | "
            f"{features['frozen_external_validation']['yes']} | "
            f"{features['safety_hazard_test']['yes']} |"
        )
    lines.extend(
        [
            "",
            "## Capability by Strongest MedWM-Eval Evidence Level",
            "",
            "| Capability | Studies | Rollout | Action | Uncertainty | Causal | External | Decision | Safety |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for capability, item in payload["capability_by_evidence"].items():
        values = [
            item["ordinal"][field]["strong"]
            for field in [
                "rollout_evidence",
                "action_evidence",
                "uncertainty_evidence",
                "causal_evidence",
                "external_evidence",
                "decision_evidence",
                "safety_evidence",
            ]
        ]
        lines.append(
            f"| {capability.replace('_', ' ')} | {item['records']} | "
            + " | ".join(str(value) for value in values)
            + " |"
        )
    lines.extend(
        [
            "",
            "## Domain by Selected Reported Evidence",
            "",
            "| Domain | Studies | Free rollout | Horizon resolved | Calibration | External validation | Causal estimand | Safety test |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for domain, item in payload["domain_by_evidence"].items():
        values = [
            item["features"][field]["yes"]
            for field in DISPLAY_FEATURES
        ]
        lines.append(
            f"| {domain.replace('_', ' ')} | {item['records']} | "
            + " | ".join(str(value) for value in values)
            + " |"
        )
    applicability = payload["applicability_matched_joint_gap"]
    lines.extend(
        [
            "",
            "## Post Hoc Applicability Sensitivity",
            "",
            (
                "This operational sensitivity is restricted to strict-core "
                "studies with partial or directly auditable uncertainty "
                "evidence, free-running rollout, and horizon-resolved "
                "results. It is not a validated universal applicability rule."
            ),
            "",
            "| Studies | Formal calibration | Frozen external validation | Both | External status unclear |",
            "| ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {applicability['records']} | "
                f"{applicability['formal_calibration_yes']} | "
                f"{applicability['frozen_external_validation_yes']} | "
                f"{applicability['formal_calibration_and_frozen_external_validation_yes']} | "
                f"{applicability['frozen_external_validation_unclear']} |"
            ),
            "",
            "Publication status and corpus-boundary analyses are sensitivity "
            "checks. They do not substitute for study-type-specific risk-of-"
            "bias assessment or human verification.",
        ]
    )
    (args.output_dir / "review-sensitivity-analysis.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                name: summary["records"]
                for name, summary in payload["subsets"].items()
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
