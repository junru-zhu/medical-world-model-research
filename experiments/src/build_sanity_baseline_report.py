#!/usr/bin/env python3
"""Combine deterministic and ridge baseline results into an evidence report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def read_constraints(path: Path, model_from_row: bool) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for row in payload["pressure_constraint"]:
        output = dict(row)
        if not model_from_row:
            output["model"] = payload["model"]
        rows.append(output)
    return pd.DataFrame(rows)


def format_ci(row: pd.Series) -> str:
    return (
        f"{row['mean_patient_nmae']:.4f} "
        f"[{row['bootstrap_95_ci_lower']:.4f}, "
        f"{row['bootstrap_95_ci_upper']:.4f}]"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--ridge-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    patient = pd.concat(
        [
            pd.read_csv(args.baseline_dir / "patient-nmae-summary.csv"),
            pd.read_csv(args.ridge_dir / "patient-nmae-summary.csv"),
        ],
        ignore_index=True,
    ).sort_values(["split", "horizon_hours", "mean_patient_nmae", "model"])
    constraints = pd.concat(
        [
            read_constraints(args.baseline_dir / "summary.json", True),
            read_constraints(args.ridge_dir / "summary.json", False),
        ],
        ignore_index=True,
    ).sort_values(["split", "horizon_hours", "model"])

    rankings = []
    for (split, horizon), group in patient.groupby(
        ["split", "horizon_hours"], sort=True
    ):
        ordered = group.sort_values(["mean_patient_nmae", "model"])
        rankings.append(
            {
                "split": split,
                "horizon_hours": horizon,
                "ranking_best_to_worst": " > ".join(ordered["model"]),
            }
        )
    ranking_frame = pd.DataFrame(rankings)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    patient.to_csv(args.output_dir / "combined-patient-nmae.csv", index=False)
    constraints.to_csv(args.output_dir / "combined-constraints.csv", index=False)
    ranking_frame.to_csv(args.output_dir / "model-rankings.csv", index=False)

    selected_horizons = {1, 12, 24}
    display = patient[patient["horizon_hours"].isin(selected_horizons)].copy()
    display["estimate"] = display.apply(format_ci, axis=1)
    pivot = display.pivot(
        index=["split", "model"],
        columns="horizon_hours",
        values="estimate",
    ).reset_index()

    constraint_display = constraints[
        constraints["horizon_hours"].isin(selected_horizons)
    ].copy()
    constraint_pivot = constraint_display.pivot(
        index=["split", "model"],
        columns="horizon_hours",
        values="violations_per_1000_states",
    ).reset_index()

    locf = patient[patient["model"] == "locf"][
        ["split", "horizon_hours", "mean_patient_nmae"]
    ].rename(columns={"mean_patient_nmae": "locf_nmae"})
    ridge = patient[patient["model"] == "ridge_var"][
        ["split", "horizon_hours", "mean_patient_nmae"]
    ].rename(columns={"mean_patient_nmae": "ridge_nmae"})
    comparison = locf.merge(ridge, on=["split", "horizon_hours"])
    comparison["ridge_relative_improvement_vs_locf"] = (
        comparison["locf_nmae"] - comparison["ridge_nmae"]
    ) / comparison["locf_nmae"]
    comparison.to_csv(
        args.output_dir / "ridge-vs-locf.csv",
        index=False,
    )

    lines = [
        "# Sanity-Baseline Evidence Report",
        "",
        "Status: completed real-data sanity-baseline component; probabilistic "
        "neural results are stored and summarized separately",
        "",
        "Dataset: PhysioNet/Computing in Cardiology Challenge 2019 v1.0.0",
        "",
        "All models use cohort-A training statistics and the same deterministic "
        "patient split. Ridge hyperparameters were selected on the validation "
        "split. Cohort-B external test data were not used for selection.",
        "",
        "## Patient-Macro NMAE",
        "",
        "Values are mean patient NMAE with percentile 95% patient-level "
        "bootstrap intervals.",
        "",
        "| Split | Model | 1 h | 12 h | 24 h |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for _, row in pivot.iterrows():
        lines.append(
            f"| {row['split']} | {row['model']} | {row[1]} | "
            f"{row[12]} | {row[24]} |"
        )

    lines.extend(
        [
            "",
            "## Arterial-Pressure Ordering Violations",
            "",
            "Violations per 1,000 generated states for systolic >= mean >= "
            "diastolic pressure.",
            "",
            "| Split | Model | 1 h | 12 h | 24 h |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for _, row in constraint_pivot.iterrows():
        lines.append(
            f"| {row['split']} | {row['model']} | {row[1]:.3f} | "
            f"{row[12]:.3f} | {row[24]:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Bounded Interpretation",
            "",
            "- Ridge VAR has lower NMAE than LOCF and both population baselines "
            "at every tested horizon and in both test cohorts.",
            "- NMAE increases with horizon for the learned and persistence "
            "baselines, demonstrating rollout degradation even in this "
            "point-forecast setting.",
            "- All models degrade on the external cohort in NMAE, but the "
            "magnitude is model- and horizon-dependent.",
            "- Population medians have zero pressure-ordering violations by "
            "construction while having worse forecast error. A zero constraint "
            "count is therefore not evidence of useful dynamics.",
            "- Ridge constraint violations decline with horizon as its "
            "forecasts revert toward common population states; this may reflect "
            "mean collapse rather than physiological preservation.",
            "- The model ranking is stable across these four sanity baselines. "
            "This statement is restricted to the deterministic and ridge "
            "comparison; the publication analysis adds probabilistic neural "
            "models on the same support.",
            "- These point models do not evaluate calibration, stochastic "
            "trajectory diversity, observation-mask fidelity, causal effects, "
            "or clinical benefit.",
        ]
    )
    (args.output_dir / "report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "patient_rows": len(patient),
                "constraint_rows": len(constraints),
                "ranking_rows": len(ranking_frame),
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
