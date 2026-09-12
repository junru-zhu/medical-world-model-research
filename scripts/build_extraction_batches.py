#!/usr/bin/env python3
"""Build disjoint empirical-study extraction batches from the adjudicated corpus."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


OUTPUT_FIELDS = [
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--included",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/"
            "screening/fulltext-adjudicated/included.csv"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "output/literature-search/medical-world-models/screening/extraction"
        ),
    )
    parser.add_argument("--batches", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.batches < 1:
        raise ValueError("--batches must be at least 1")

    with args.included.open(newline="", encoding="utf-8") as handle:
        empirical = [
            row
            for row in csv.DictReader(handle)
            if row["final_corpus_type"] == "empirical"
        ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    batch_rows: list[list[dict[str, str]]] = [[] for _ in range(args.batches)]
    for index, row in enumerate(empirical):
        batch_rows[index % args.batches].append(row)

    for batch_number, rows in enumerate(batch_rows, start=1):
        path = args.output_dir / f"extraction-batch-{batch_number}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            for row in rows:
                output = {field: "" for field in OUTPUT_FIELDS}
                output.update(
                    {
                        "candidate_id": row["candidate_id"],
                        "title": row["title"],
                        "primary_source_url": (
                            row["reviewer_a_full_text_url"]
                            or row["reviewer_b_full_text_url"]
                            or row["url"]
                        ),
                        "publication_status": row["record_type"],
                        "source_status": row["source_status"],
                    }
                )
                writer.writerow(output)

    print(
        f"Wrote {len(empirical)} empirical records across "
        f"{args.batches} batches to {args.output_dir}"
    )


if __name__ == "__main__":
    main()
