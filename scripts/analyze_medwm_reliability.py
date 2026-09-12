#!/usr/bin/env python3
"""Estimate field-level MedWM-Eval agreement with study bootstrap intervals."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Callable


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


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    if not a:
        return None
    labels = sorted(set(a) | set(b))
    observed = sum(x == y for x, y in zip(a, b)) / len(a)
    count_a, count_b = Counter(a), Counter(b)
    expected = sum(
        (count_a[label] / len(a)) * (count_b[label] / len(b))
        for label in labels
    )
    if math.isclose(expected, 1.0):
        return 1.0 if math.isclose(observed, 1.0) else None
    return (observed - expected) / (1 - expected)


def weighted_kappa(
    a: list[str], b: list[str], *, quadratic: bool
) -> float | None:
    pairs = [
        (int(x), int(y))
        for x, y in zip(a, b)
        if x != "NA" and y != "NA"
    ]
    if not pairs:
        return None
    labels = [0, 1, 2]
    count_a = Counter(x for x, _ in pairs)
    count_b = Counter(y for _, y in pairs)
    n = len(pairs)

    def distance(x: int, y: int) -> float:
        scaled = abs(x - y) / (len(labels) - 1)
        return scaled**2 if quadratic else scaled

    observed = sum(distance(x, y) for x, y in pairs) / n
    expected = sum(
        distance(x, y) * (count_a[x] / n) * (count_b[y] / n)
        for x in labels
        for y in labels
    )
    if math.isclose(expected, 0.0):
        return 1.0 if math.isclose(observed, 0.0) else None
    return 1 - observed / expected


def percentile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def bootstrap_ci(
    rows_a: list[dict[str, str]],
    rows_b: list[dict[str, str]],
    statistic: Callable[[list[str], list[str]], float | None],
    field: str,
    *,
    replicates: int,
    seed: int,
) -> list[float | None]:
    rng = random.Random(seed)
    estimates: list[float] = []
    for _ in range(replicates):
        indices = [rng.randrange(len(rows_a)) for _ in rows_a]
        a = [rows_a[index][field] for index in indices]
        b = [rows_b[index][field] for index in indices]
        estimate = statistic(a, b)
        if estimate is not None and math.isfinite(estimate):
            estimates.append(estimate)
    return [percentile(estimates, 0.025), percentile(estimates, 0.975)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--replicates", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args()

    rows_a = read_rows(args.reviewer_a)
    rows_b = read_rows(args.reviewer_b)
    if len(rows_a) != len(rows_b):
        raise ValueError("Reviewer files have different record counts.")
    ids_a = [row["candidate_id"] for row in rows_a]
    ids_b = [row["candidate_id"] for row in rows_b]
    if ids_a != ids_b:
        raise ValueError("Reviewer files are not aligned by candidate_id.")

    ignored = {
        "candidate_id",
        "title",
        "evidence_anchors",
        "reviewer_notes",
        "confidence",
    }
    fields = [field for field in rows_a[0] if field not in ignored]
    result: dict[str, object] = {
        "records": len(rows_a),
        "bootstrap_replicates": args.replicates,
        "bootstrap_seed": args.seed,
        "bootstrap_unit": "study",
        "fields": {},
    }
    for field_index, field in enumerate(fields):
        a = [row[field] for row in rows_a]
        b = [row[field] for row in rows_b]
        raw = sum(x == y for x, y in zip(a, b)) / len(a)
        field_result: dict[str, object] = {
            "raw_agreement": raw,
            "cohen_kappa": cohen_kappa(a, b),
            "cohen_kappa_95_ci": bootstrap_ci(
                rows_a,
                rows_b,
                cohen_kappa,
                field,
                replicates=args.replicates,
                seed=args.seed + field_index,
            ),
            "reviewer_a_distribution": dict(sorted(Counter(a).items())),
            "reviewer_b_distribution": dict(sorted(Counter(b).items())),
        }
        if field in ORDINAL_FIELDS:
            linear = lambda x, y: weighted_kappa(  # noqa: E731
                x, y, quadratic=False
            )
            quadratic = lambda x, y: weighted_kappa(  # noqa: E731
                x, y, quadratic=True
            )
            field_result.update(
                {
                    "ordinal_pairs_excluding_na": sum(
                        x != "NA" and y != "NA"
                        for x, y in zip(a, b)
                    ),
                    "linear_weighted_kappa": linear(a, b),
                    "linear_weighted_kappa_95_ci": bootstrap_ci(
                        rows_a,
                        rows_b,
                        linear,
                        field,
                        replicates=args.replicates,
                        seed=args.seed + 100 + field_index,
                    ),
                    "quadratic_weighted_kappa": quadratic(a, b),
                    "quadratic_weighted_kappa_95_ci": bootstrap_ci(
                        rows_a,
                        rows_b,
                        quadratic,
                        field,
                        replicates=args.replicates,
                        seed=args.seed + 200 + field_index,
                    ),
                }
            )
        result["fields"][field] = field_result

    total = len(rows_a) * len(fields)
    agreements = sum(
        rows_a[index][field] == rows_b[index][field]
        for index in range(len(rows_a))
        for field in fields
    )
    result["overall"] = {
        "study_field_decisions": total,
        "agreements": agreements,
        "raw_agreement": agreements / total,
        "interpretation": (
            "AI-pass process reproducibility only; not evidence of human "
            "inter-rater reliability or construct validity."
        ),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# MedWM-Eval Coding Reliability",
        "",
        (
            f"Records: {len(rows_a)}; study-field decisions: {total}; "
            f"overall raw agreement: {agreements / total:.1%}."
        ),
        "",
        "Intervals are percentile 95% confidence intervals from a study-level "
        f"bootstrap with {args.replicates:,} replicates and seed {args.seed}.",
        "",
        "| Field | Raw agreement | Cohen kappa (95% CI) | Linear weighted kappa (95% CI) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for field in fields:
        item = result["fields"][field]
        kappa = item["cohen_kappa"]
        kappa_ci = item["cohen_kappa_95_ci"]
        kappa_text = (
            "NE"
            if kappa is None
            else f"{kappa:.3f} ({kappa_ci[0]:.3f} to {kappa_ci[1]:.3f})"
        )
        if field in ORDINAL_FIELDS:
            weighted = item["linear_weighted_kappa"]
            weighted_ci = item["linear_weighted_kappa_95_ci"]
            weighted_text = (
                "NE"
                if weighted is None
                else (
                    f"{weighted:.3f} "
                    f"({weighted_ci[0]:.3f} to {weighted_ci[1]:.3f})"
                )
            )
        else:
            weighted_text = "NA"
        lines.append(
            f"| {field.replace('_', ' ')} | "
            f"{item['raw_agreement']:.1%} | {kappa_text} | {weighted_text} |"
        )
    lines.extend(
        [
            "",
            "These statistics characterize reproducibility between the two "
            "developmental AI-assisted coding passes. They do not validate "
            "MedWM-Eval and do not replace human dual coding.",
        ]
    )
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result["overall"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
