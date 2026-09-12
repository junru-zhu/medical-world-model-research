#!/usr/bin/env python3
"""Run and summarize trajectory-count sensitivity on a fixed patient subset."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np


METRICS = (
    "patient_nmae",
    "patient_crps",
    "coverage_90",
    "mean_interval_width_scaled",
    "patient_nll",
    "mask_brier",
)


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--models", default="grud,transformer,rssm")
    parser.add_argument("--seed", type=int, default=20260912)
    parser.add_argument("--trajectory-samples", default="20,50,100")
    parser.add_argument("--patients", type=int, default=1000)
    parser.add_argument("--patient-sample-seed", type=int, default=20260912)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    models = [value.strip() for value in args.models.split(",") if value.strip()]
    sample_counts = sorted(
        {int(value) for value in args.trajectory_samples.split(",") if value}
    )
    evaluator = Path(__file__).resolve().parent / "evaluate_neural_forecaster.py"
    metric_rows: list[dict[str, Any]] = []
    constraint_rows: list[dict[str, Any]] = []
    subset_hashes: dict[str, str] = {}

    for model in models:
        checkpoint = (
            args.result_root / model / f"seed-{args.seed}" / "model.pt"
        )
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)
        for samples in sample_counts:
            output = args.output_dir / model / f"samples-{samples}"
            summary_path = output / "summary.json"
            if not summary_path.is_file():
                run(
                    [
                        args.python,
                        str(evaluator),
                        "--data-dir",
                        str(args.data_dir),
                        "--checkpoint",
                        str(checkpoint),
                        "--output-dir",
                        str(output),
                        "--splits",
                        "external_test",
                        "--horizons",
                        "1,3,6,12,24",
                        "--minimum-context",
                        "12",
                        "--maximum-context",
                        "72",
                        "--stride",
                        "6",
                        "--trajectory-samples",
                        str(samples),
                        "--batch-size",
                        "64",
                        "--seed",
                        str(args.seed),
                        "--device",
                        args.device,
                        "--sensitivity-patient-sample",
                        str(args.patients),
                        "--sensitivity-sample-seed",
                        str(args.patient_sample_seed),
                    ]
                )
            summary = read_json(summary_path)
            if summary.get("status") != "sensitivity_only":
                raise ValueError(f"Unexpected sensitivity status: {summary_path}")
            subset_hash = summary["sampled_patient_hashes"]["external_test"]
            if model in subset_hashes and subset_hashes[model] != subset_hash:
                raise ValueError(f"Patient subset changed within {model}.")
            subset_hashes[model] = subset_hash
            for horizon, metrics in summary["patient_macro"][
                "external_test"
            ].items():
                for metric in METRICS:
                    metric_rows.append(
                        {
                            "model": model,
                            "seed": args.seed,
                            "trajectory_samples": samples,
                            "patients_requested": args.patients,
                            "patient_subset_sha256": subset_hash,
                            "horizon_hours": int(horizon),
                            "metric": metric,
                            "value": metrics[metric],
                        }
                    )
            with (output / "constraints.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                for row in csv.DictReader(handle):
                    constraint_rows.append(
                        {
                            "model": model,
                            "seed": args.seed,
                            "trajectory_samples": samples,
                            "patients_requested": args.patients,
                            "patient_subset_sha256": subset_hash,
                            "horizon_hours": int(row["horizon_hours"]),
                            "constraint": row["constraint"],
                            "violations_per_1000_states": float(
                                row["violations_per_1000_states"]
                            ),
                        }
                    )

    if len(set(subset_hashes.values())) != 1:
        raise ValueError("Models did not use the same external patient subset.")
    stability_rows: list[dict[str, Any]] = []
    for rows, value_field, kind in (
        (metric_rows, "value", "metric"),
        (
            constraint_rows,
            "violations_per_1000_states",
            "constraint",
        ),
    ):
        groups: dict[tuple[Any, ...], list[float]] = {}
        for row in rows:
            label = row[kind]
            key = (row["model"], row["horizon_hours"], kind, label)
            groups.setdefault(key, []).append(float(row[value_field]))
        for (model, horizon, label_kind, label), values in sorted(
            groups.items()
        ):
            stability_rows.append(
                {
                    "model": model,
                    "horizon_hours": horizon,
                    "quantity_type": label_kind,
                    "quantity": label,
                    "minimum": min(values),
                    "maximum": max(values),
                    "absolute_range": max(values) - min(values),
                    "relative_range_percent": (
                        100.0
                        * (max(values) - min(values))
                        / max(abs(float(np.mean(values))), 1e-12)
                    ),
                    "sample_counts": ",".join(
                        str(value) for value in sample_counts
                    ),
                }
            )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "metric-sensitivity.csv", metric_rows)
    write_csv(args.output_dir / "constraint-sensitivity.csv", constraint_rows)
    write_csv(args.output_dir / "stability-ranges.csv", stability_rows)
    summary = {
        "status": "complete",
        "models": models,
        "seed": args.seed,
        "trajectory_samples": sample_counts,
        "patients_requested": args.patients,
        "patient_sample_seed": args.patient_sample_seed,
        "patient_subset_sha256": next(iter(subset_hashes.values())),
        "interpretation": (
            "Numerical Monte Carlo convergence sensitivity only; not used for "
            "model selection or clinical claims."
        ),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
