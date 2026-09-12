#!/usr/bin/env python3
"""Build a study-level audit linking stated capability to reported evidence."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


CAPABILITY_REQUIREMENTS = {
    "passive_forecasting": [
        ("rollout_evidence", "rollout"),
        ("uncertainty_evidence", "uncertainty"),
    ],
    "action_conditioned": [
        ("rollout_evidence", "rollout"),
        ("action_evidence", "action"),
        ("uncertainty_evidence", "uncertainty"),
    ],
    "counterfactual": [
        ("rollout_evidence", "rollout"),
        ("action_evidence", "action"),
        ("uncertainty_evidence", "uncertainty"),
        ("causal_evidence", "causal"),
    ],
    "planning": [
        ("rollout_evidence", "rollout"),
        ("action_evidence", "action"),
        ("uncertainty_evidence", "uncertainty"),
        ("decision_evidence", "decision"),
        ("safety_evidence", "safety"),
    ],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def priority(absent: int, partial: int) -> str:
    if absent >= 2 or absent + partial >= 4:
        return "high"
    if absent or partial >= 2:
        return "medium"
    return "routine"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--included", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    pilot_rows = read_csv(args.pilot)
    extraction = {
        row["candidate_id"]: row for row in read_csv(args.extraction)
    }
    included = {
        row["candidate_id"]: row
        for row in read_csv(args.included)
        if row["final_corpus_type"] == "empirical"
    }
    pilot_ids = {row["candidate_id"] for row in pilot_rows}
    if pilot_ids != set(extraction) or pilot_ids != set(included):
        raise ValueError("Pilot, extraction, and included empirical IDs differ.")

    output: list[dict[str, str]] = []
    for row in pilot_rows:
        candidate_id = row["candidate_id"]
        capability = row["highest_capability_claim"]
        requirements = CAPABILITY_REQUIREMENTS[capability]
        absent_domains = [
            label for field, label in requirements if row[field] == "0"
        ]
        partial_domains = [
            label for field, label in requirements if row[field] == "1"
        ]
        strong_domains = [
            label for field, label in requirements if row[field] == "2"
        ]

        feature_limits: list[str] = []
        if row["formal_calibration"] != "yes":
            feature_limits.append(
                f"formal_calibration={row['formal_calibration']}"
            )
        if row["frozen_external_validation"] != "yes":
            feature_limits.append(
                "frozen_external_validation="
                f"{row['frozen_external_validation']}"
            )
        if capability in {"counterfactual", "planning"}:
            if row["explicit_causal_estimand"] != "yes":
                feature_limits.append(
                    "explicit_causal_estimand="
                    f"{row['explicit_causal_estimand']}"
                )
        if capability == "planning":
            if row["closed_loop_evaluation"] in {"no", "offline"}:
                feature_limits.append(
                    f"closed_loop_evaluation={row['closed_loop_evaluation']}"
                )
            if row["safety_hazard_test"] != "yes":
                feature_limits.append(
                    f"safety_hazard_test={row['safety_hazard_test']}"
                )

        extracted = extraction[candidate_id]
        output.append(
            {
                "candidate_id": candidate_id,
                "title": included[candidate_id]["title"],
                "highest_capability_claim": capability,
                "required_domains_strong": ";".join(strong_domains) or "none",
                "required_domains_partial": ";".join(partial_domains) or "none",
                "required_domains_absent": ";".join(absent_domains) or "none",
                "descriptive_feature_limits": ";".join(feature_limits) or "none",
                "priority_for_human_claim_review": priority(
                    len(absent_domains), len(partial_domains)
                ),
                "extracted_claim_boundary": extracted["capability_claim"],
                "causal_language": extracted["causal_language"],
                "decision_utility": extracted["decision_utility"],
                "safety_evaluation": extracted["safety_evaluation"],
                "evidence_anchors": extracted["evidence_anchors"],
                "reviewer_confidence": extracted["reviewer_confidence"],
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "claim-provenance-audit.csv", output)

    capability_counts = Counter(
        row["highest_capability_claim"] for row in output
    )
    priority_counts = Counter(
        row["priority_for_human_claim_review"] for row in output
    )
    summary = {
        "records": len(output),
        "capability_claims": dict(sorted(capability_counts.items())),
        "human_claim_review_priority": dict(sorted(priority_counts.items())),
        "interpretation": (
            "The priority flag routes human verification; it is not a study "
            "quality score or a verdict that the claimed capability is invalid."
        ),
    }
    (args.output_dir / "claim-provenance-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Claim-Provenance Audit",
        "",
        (
            f"Records: {len(output)}. This audit cross-references each study's "
            "highest stated capability with the capability-specific evidence "
            "domains reported in its inspected primary text."
        ),
        "",
        (
            "The priority flag is only a routing aid for human verification. "
            "It is not a study-quality score and does not determine eligibility."
        ),
        "",
        "| Human review priority | Studies |",
        "| --- | ---: |",
    ]
    for label in ("high", "medium", "routine"):
        lines.append(f"| {label} | {priority_counts.get(label, 0)} |")
    lines.extend(
        [
            "",
            "The CSV companion preserves the extracted claim boundary, causal "
            "language, decision utility, safety evidence, source anchors, and "
            "the exact absent or partial capability-specific evidence domains "
            "for every empirical study.",
        ]
    )
    (args.output_dir / "claim-provenance-audit.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
