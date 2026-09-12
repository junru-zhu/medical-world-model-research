#!/usr/bin/env python3
"""Create independent MedWM-Eval pilot coding templates."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = [
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--extraction",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/study-extraction.csv"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/screening/pilot-coding"
        ),
    )
    args = parser.parse_args()

    with args.extraction.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for reviewer in ("a", "b"):
        path = args.output_dir / f"medwm-pilot-reviewer-{reviewer}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            for row in rows:
                output = {field: "" for field in FIELDS}
                output["candidate_id"] = row["candidate_id"]
                output["title"] = row["title"]
                writer.writerow(output)
        print(f"Wrote {len(rows)} rows to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
