#!/usr/bin/env python3
"""Summarize the frozen multi-seed neural evaluation matrix."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


PATIENT_METRICS = (
    "patient_nmae",
    "patient_crps",
    "coverage_90",
    "coverage_error_90",
    "mean_interval_width_scaled",
    "patient_nll",
    "mask_brier",
)
RANDOM_STREAM_POLICY = "split-specific-v1"
CONSTRAINT_POLICY = "rollout-state-and-emitted-v1"
EXPECTED_HORIZONS = [1, 3, 6, 12, 24]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_run_artifacts(
    *,
    model: str,
    seed: int,
    run_dir: Path,
    required: dict[str, Path],
) -> list[str]:
    errors: list[str] = []
    try:
        training = read_json(required["training"])
        raw = read_json(required["raw"])
        recalibrated = read_json(required["recalibrated"])
        calibration = read_json(required["calibration"])
    except (json.JSONDecodeError, OSError, KeyError) as error:
        return [f"metadata:{error}"]
    checkpoint = (run_dir / "model.pt").resolve()
    for name, payload in (
        ("training", training),
        ("raw", raw),
        ("recalibrated", recalibrated),
        ("calibration", calibration),
    ):
        if payload.get("status") != "complete":
            errors.append(f"{name}:status={payload.get('status')}")
        if payload.get("model") != model:
            errors.append(f"{name}:model={payload.get('model')}")
        if int(payload.get("seed", -1)) != seed:
            errors.append(f"{name}:seed={payload.get('seed')}")
    for name, payload in (
        ("raw", raw),
        ("recalibrated", recalibrated),
        ("calibration", calibration),
    ):
        if Path(payload.get("checkpoint", "")).resolve() != checkpoint:
            errors.append(f"{name}:checkpoint")
        if payload.get("random_stream_policy") != RANDOM_STREAM_POLICY:
            errors.append(f"{name}:random_stream_policy")
    for name, payload in (("raw", raw), ("recalibrated", recalibrated)):
        if payload.get("constraint_policy") != CONSTRAINT_POLICY:
            errors.append(f"{name}:constraint_policy")
        if payload.get("horizons") != EXPECTED_HORIZONS:
            errors.append(f"{name}:horizons")
        if payload.get("common_anchor_maximum_horizon") != 24:
            errors.append(f"{name}:common_anchor_maximum_horizon")
        if payload.get("anchor_stride") != 6:
            errors.append(f"{name}:anchor_stride")
        if payload.get("trajectory_samples") != 20:
            errors.append(f"{name}:trajectory_samples")
        if payload.get("evaluation_batch_size") != 128:
            errors.append(f"{name}:evaluation_batch_size")
    if set(raw.get("splits", [])) != {"internal_test", "external_test"}:
        errors.append("raw:splits")
    if recalibrated.get("splits") != ["external_test"]:
        errors.append("recalibrated:splits")
    if calibration.get("fit_split") != "external_calibration":
        errors.append("calibration:fit_split")
    if calibration.get("trajectory_samples") != 20:
        errors.append("calibration:trajectory_samples")
    if calibration.get("evaluation_batch_size") != 128:
        errors.append("calibration:evaluation_batch_size")
    return errors


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def aggregate(
    rows: list[dict[str, Any]],
    *,
    keys: tuple[str, ...],
    value: str,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[float]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[key] for key in keys)].append(float(row[value]))
    output = []
    for key, values in sorted(grouped.items()):
        item = dict(zip(keys, key, strict=True))
        item.update(
            {
                "seeds": len(values),
                "mean": statistics.fmean(values),
                "standard_deviation": (
                    statistics.stdev(values) if len(values) > 1 else 0.0
                ),
                "minimum": min(values),
                "maximum": max(values),
            }
        )
        output.append(item)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--models", default="grud,transformer,rssm"
    )
    parser.add_argument(
        "--seeds", default="20260912,20260913,20260914,20260915,20260916"
    )
    args = parser.parse_args()

    models = [value.strip() for value in args.models.split(",") if value.strip()]
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    seed_metrics: list[dict[str, Any]] = []
    seed_constraints: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    training_rows: list[dict[str, Any]] = []
    missing: list[str] = []

    for model in models:
        for seed in seeds:
            run_dir = args.result_root / model / f"seed-{seed}"
            required = {
                "training": run_dir / "summary.json",
                "raw": run_dir / "evaluation/summary.json",
                "recalibrated": (
                    run_dir / "external-test-recalibrated/summary.json"
                ),
                "calibration": (
                    run_dir / "external-calibration-fit/spread-calibration.json"
                ),
                "constraints": run_dir / "evaluation/constraints.csv",
            }
            absent = [name for name, path in required.items() if not path.is_file()]
            if absent:
                missing.extend(
                    f"{model}/seed-{seed}:{name}" for name in absent
                )
                continue
            invalid = validate_run_artifacts(
                model=model,
                seed=seed,
                run_dir=run_dir,
                required=required,
            )
            if invalid:
                missing.extend(
                    f"{model}/seed-{seed}:invalid:{item}"
                    for item in invalid
                )
                continue

            training = read_json(required["training"])
            training_rows.append(
                {
                    "model": model,
                    "seed": seed,
                    "best_epoch": training["best_epoch"],
                    "best_validation_loss": training[
                        "best_validation_loss"
                    ],
                    "epochs_run": training["epochs_run"],
                    "parameter_count": training["parameter_count"],
                }
            )

            for evaluation, path in (
                ("zero_shot", required["raw"]),
                ("recalibrated", required["recalibrated"]),
            ):
                summary = read_json(path)
                for split, horizons in summary["patient_macro"].items():
                    for horizon, metrics in horizons.items():
                        expanded = dict(metrics)
                        expanded["coverage_error_90"] = abs(
                            expanded["coverage_90"] - 0.9
                        )
                        for metric in PATIENT_METRICS:
                            seed_metrics.append(
                                {
                                    "evaluation": evaluation,
                                    "split": split,
                                    "model": model,
                                    "seed": seed,
                                    "horizon_hours": int(horizon),
                                    "metric": metric,
                                    "value": expanded[metric],
                                }
                            )

            calibration = read_json(required["calibration"])
            for horizon, scale in calibration["horizon_scales"].items():
                calibration_rows.append(
                    {
                        "model": model,
                        "seed": seed,
                        "horizon_hours": int(horizon),
                        "spread_scale": scale,
                        "observed_targets": calibration[
                            "observed_targets"
                        ][horizon],
                    }
                )

            with required["constraints"].open(
                newline="", encoding="utf-8"
            ) as handle:
                for row in csv.DictReader(handle):
                    seed_constraints.append(
                        {
                            "split": row["split"],
                            "model": model,
                            "seed": seed,
                            "horizon_hours": int(row["horizon_hours"]),
                            "constraint": row["constraint"],
                            "violations_per_1000_states": float(
                                row["violations_per_1000_states"]
                            ),
                        }
                    )

    if not seed_metrics:
        raise ValueError("No complete neural runs were found.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "training-runs.csv", training_rows)
    write_csv(args.output_dir / "seed-metrics.csv", seed_metrics)
    write_csv(
        args.output_dir / "aggregate-metrics.csv",
        aggregate(
            seed_metrics,
            keys=(
                "evaluation",
                "split",
                "model",
                "horizon_hours",
                "metric",
            ),
            value="value",
        ),
    )
    write_csv(args.output_dir / "calibration-scales.csv", calibration_rows)
    write_csv(args.output_dir / "seed-constraints.csv", seed_constraints)
    write_csv(
        args.output_dir / "aggregate-constraints.csv",
        aggregate(
            seed_constraints,
            keys=("split", "model", "horizon_hours", "constraint"),
            value="violations_per_1000_states",
        ),
    )
    completeness = {
        "status": "complete" if not missing else "incomplete",
        "models": models,
        "seeds": seeds,
        "complete_runs": len(training_rows),
        "expected_runs": len(models) * len(seeds),
        "missing": missing,
        "interpretation_boundary": (
            "Seed-level descriptive aggregation only. Patient-clustered "
            "bootstrap contrasts and multiplicity-controlled hypothesis tests "
            "must be generated separately for final inference."
        ),
    }
    (args.output_dir / "completeness.json").write_text(
        json.dumps(completeness, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(completeness, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
