#!/usr/bin/env python3
"""Fit and evaluate a ridge vector autoregression with free-running rollout."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from run_baselines import (
    DYNAMIC_COLUMNS,
    PRESSURE_INDICES,
    fit_statistics,
    locf_arrays,
    read_manifest,
    read_patient,
    update_accumulator,
    write_csv,
)


def design_matrix(scaled: np.ndarray, lag: int) -> tuple[np.ndarray, np.ndarray]:
    if len(scaled) <= lag:
        return (
            np.empty((0, lag * scaled.shape[1] + 1), dtype=np.float64),
            np.empty((0, scaled.shape[1]), dtype=np.float64),
        )
    parts = [
        scaled[offset : len(scaled) - lag + offset]
        for offset in range(lag)
    ]
    features = np.concatenate(parts, axis=1)
    features = np.column_stack(
        [features, np.ones(features.shape[0], dtype=np.float64)]
    )
    targets = scaled[lag:]
    return features, targets


def fit_sufficient_statistics(
    data_root: Path,
    manifest: list[dict[str, str]],
    statistics: dict[str, Any],
    lag: int,
) -> dict[str, Any]:
    selected_indices = np.flatnonzero(statistics["selected"])
    selected_medians = statistics["medians"][selected_indices]
    selected_iqr = statistics["iqr"][selected_indices]
    feature_count = lag * len(selected_indices) + 1
    xtx = np.zeros((feature_count, feature_count), dtype=np.float64)
    xty = np.zeros((feature_count, len(selected_indices)), dtype=np.float64)
    transition_rows = 0
    patient_count = 0

    for row in manifest:
        if row["split"] != "train":
            continue
        values, _ = read_patient(data_root / row["relative_path"])
        filled, _ = locf_arrays(values, statistics["medians"])
        scaled = (
            filled[:, selected_indices] - selected_medians
        ) / selected_iqr
        features, targets = design_matrix(scaled, lag)
        if not len(features):
            continue
        xtx += features.T @ features
        xty += features.T @ targets
        transition_rows += len(features)
        patient_count += 1

    if transition_rows == 0:
        raise ValueError("No training transitions were generated.")
    return {
        "xtx": xtx,
        "xty": xty,
        "transition_rows": transition_rows,
        "patient_count": patient_count,
        "selected_indices": selected_indices,
        "selected_medians": selected_medians,
        "selected_iqr": selected_iqr,
    }


def solve_ridge(
    sufficient: dict[str, Any],
    ridge_lambda: float,
) -> np.ndarray:
    rows = sufficient["transition_rows"]
    xtx = sufficient["xtx"] / rows
    xty = sufficient["xty"] / rows
    penalty = np.eye(xtx.shape[0], dtype=np.float64) * ridge_lambda
    penalty[-1, -1] = 0.0
    return np.linalg.solve(xtx + penalty, xty)


def rollout(
    scaled: np.ndarray,
    anchors: np.ndarray,
    coefficient: np.ndarray,
    lag: int,
    horizon: int,
) -> np.ndarray:
    states = np.stack(
        [scaled[anchors - lag + 1 + offset] for offset in range(lag)],
        axis=1,
    )
    for _ in range(horizon):
        features = states.reshape(len(anchors), -1)
        features = np.column_stack(
            [features, np.ones(len(anchors), dtype=np.float64)]
        )
        next_state = features @ coefficient
        states = np.concatenate(
            [states[:, 1:], next_state[:, np.newaxis, :]],
            axis=1,
        )
    return states[:, -1]


def new_accumulator() -> dict[str, float]:
    return {"count": 0.0, "sum_abs": 0.0, "sum_sq": 0.0}


def evaluate(
    data_root: Path,
    manifest: list[dict[str, str]],
    statistics: dict[str, Any],
    sufficient: dict[str, Any],
    coefficient: np.ndarray,
    *,
    splits: set[str],
    horizons: list[int],
    min_context: int,
    stride: int,
    common_anchor_maximum_horizon: int,
    include_detail: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    selected_indices = sufficient["selected_indices"]
    selected_names = [DYNAMIC_COLUMNS[index] for index in selected_indices]
    selected_medians = sufficient["selected_medians"]
    selected_iqr = sufficient["selected_iqr"]
    index_lookup = {
        dynamic_index: selected_position
        for selected_position, dynamic_index in enumerate(selected_indices)
    }
    pressure_positions = tuple(index_lookup[index] for index in PRESSURE_INDICES)

    aggregate: dict[tuple[str, int, int], dict[str, float]] = defaultdict(
        new_accumulator
    )
    patient_rows: list[dict[str, Any]] = []
    constraint_counts: dict[tuple[str, int], list[int]] = defaultdict(
        lambda: [0, 0]
    )
    evaluated_patients: dict[str, int] = defaultdict(int)
    nonfinite_predictions: dict[tuple[str, int], int] = defaultdict(int)

    for row in manifest:
        split = row["split"]
        if split not in splits:
            continue
        values, _ = read_patient(data_root / row["relative_path"])
        if len(values) < min_context + common_anchor_maximum_horizon:
            continue
        filled, _ = locf_arrays(values, statistics["medians"])
        scaled = (
            filled[:, selected_indices] - selected_medians
        ) / selected_iqr
        evaluated_patients[split] += 1
        last_anchor = len(values) - common_anchor_maximum_horizon - 1
        anchors = np.arange(
            min_context - 1,
            last_anchor + 1,
            stride,
            dtype=int,
        )

        for horizon in horizons:
            prediction_scaled = rollout(
                scaled,
                anchors,
                coefficient,
                lag=(coefficient.shape[0] - 1) // len(selected_indices),
                horizon=horizon,
            )
            finite_rows = np.all(np.isfinite(prediction_scaled), axis=1)
            nonfinite_predictions[(split, horizon)] += int(
                np.sum(~finite_rows)
            )
            if not np.all(finite_rows):
                anchors = anchors[finite_rows]
                prediction_scaled = prediction_scaled[finite_rows]
            if not len(anchors):
                continue
            prediction = prediction_scaled * selected_iqr + selected_medians
            targets = values[anchors + horizon][:, selected_indices]

            patient_abs_sum = 0.0
            patient_scaled_count = 0
            for selected_position, dynamic_index in enumerate(selected_indices):
                observed = ~np.isnan(targets[:, selected_position])
                if not np.any(observed):
                    continue
                pred = prediction[observed, selected_position]
                actual = targets[observed, selected_position]
                update_accumulator(
                    aggregate[(split, horizon, selected_position)],
                    pred,
                    actual,
                )
                patient_abs_sum += float(
                    np.sum(
                        np.abs(pred - actual)
                        / selected_iqr[selected_position]
                    )
                )
                patient_scaled_count += int(np.sum(observed))

            if patient_scaled_count and include_detail:
                patient_rows.append(
                    {
                        "patient_id": row["patient_id"],
                        "cohort": row["cohort"],
                        "split": split,
                        "model": "ridge_var",
                        "horizon_hours": horizon,
                        "observed_targets": patient_scaled_count,
                        "patient_nmae": patient_abs_sum / patient_scaled_count,
                    }
                )

            pressure = prediction[:, pressure_positions]
            violations = np.sum(
                (pressure[:, 0] < pressure[:, 1])
                | (pressure[:, 1] < pressure[:, 2])
            )
            counter = constraint_counts[(split, horizon)]
            counter[0] += int(violations)
            counter[1] += int(len(pressure))

    metric_rows: list[dict[str, Any]] = []
    if include_detail:
        for (split, horizon, selected_position), accumulator in sorted(
            aggregate.items()
        ):
            count = int(accumulator["count"])
            if not count:
                continue
            mae = accumulator["sum_abs"] / count
            metric_rows.append(
                {
                    "split": split,
                    "model": "ridge_var",
                    "horizon_hours": horizon,
                    "variable": selected_names[selected_position],
                    "observed_targets": count,
                    "mae": mae,
                    "rmse": np.sqrt(accumulator["sum_sq"] / count),
                    "nmae": mae / selected_iqr[selected_position],
                }
            )

    patient_macro: dict[str, float] = {}
    for split in sorted(splits):
        values = [
            row["patient_nmae"]
            for row in patient_rows
            if row["split"] == split
        ]
        if values:
            patient_macro[split] = float(np.mean(values))

    summary = {
        "model": "ridge_var",
        "selected_variables": selected_names,
        "evaluated_patients": dict(sorted(evaluated_patients.items())),
        "patient_macro_nmae_across_requested_horizons": patient_macro,
        "pressure_constraint": [
            {
                "split": split,
                "horizon_hours": horizon,
                "violations": values[0],
                "evaluated_states": values[1],
                "violations_per_1000_states": (
                    1000 * values[0] / values[1] if values[1] else None
                ),
            }
            for (split, horizon), values in sorted(constraint_counts.items())
        ],
        "nonfinite_prediction_rows": [
            {
                "split": split,
                "horizon_hours": horizon,
                "rows": count,
            }
            for (split, horizon), count in sorted(nonfinite_predictions.items())
        ],
    }
    return metric_rows, patient_rows, summary


def validation_score(
    data_root: Path,
    manifest: list[dict[str, str]],
    statistics: dict[str, Any],
    sufficient: dict[str, Any],
    coefficient: np.ndarray,
    *,
    horizon: int,
    min_context: int,
    stride: int,
) -> float:
    _, patient_rows, _ = evaluate(
        data_root,
        manifest,
        statistics,
        sufficient,
        coefficient,
        splits={"validation"},
        horizons=[horizon],
        min_context=min_context,
        stride=stride,
        common_anchor_maximum_horizon=horizon,
        include_detail=True,
    )
    if not patient_rows:
        raise ValueError("No validation patient metrics were produced.")
    return float(np.mean([row["patient_nmae"] for row in patient_rows]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--model-input",
        type=Path,
        help=(
            "Optional frozen ridge-var-model.npz. When provided, skip fitting "
            "and hyperparameter selection and evaluate this model only."
        ),
    )
    parser.add_argument("--coverage-threshold", type=float, default=0.05)
    parser.add_argument("--hour-cap", type=int, default=72)
    parser.add_argument("--lag", type=int, default=3)
    parser.add_argument("--min-context", type=int, default=12)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument(
        "--common-anchor-maximum-horizon",
        type=int,
        default=0,
        help=(
            "Require every evaluation anchor to support this horizon for all "
            "reported metrics. Zero uses the maximum requested horizon."
        ),
    )
    parser.add_argument("--tuning-stride", type=int, default=2)
    parser.add_argument("--tuning-horizon", type=int, default=12)
    parser.add_argument("--horizons", default="1,3,6,12,24")
    parser.add_argument("--splits", default="internal_test,external_test")
    parser.add_argument(
        "--ridge-lambdas",
        default="0.000001,0.0001,0.01,0.1,1.0",
    )
    args = parser.parse_args()

    if args.lag < 1:
        raise ValueError("--lag must be positive.")
    horizons = [int(value) for value in args.horizons.split(",") if value]
    common_anchor_maximum_horizon = (
        args.common_anchor_maximum_horizon or max(horizons)
    )
    if common_anchor_maximum_horizon < max(horizons):
        raise ValueError(
            "--common-anchor-maximum-horizon must be at least the maximum "
            "requested horizon."
        )
    splits = {value for value in args.splits.split(",") if value}
    ridge_lambdas = [
        float(value) for value in args.ridge_lambdas.split(",") if value
    ]
    manifest = read_manifest(args.split_manifest)
    data_root = args.data_root.resolve()
    statistics = fit_statistics(
        data_root,
        manifest,
        args.coverage_threshold,
        args.hour_cap,
    )
    if args.model_input:
        frozen = np.load(args.model_input, allow_pickle=False)
        frozen_lag = int(frozen["lag"][0])
        if args.lag != frozen_lag:
            raise ValueError(
                f"--lag {args.lag} does not match frozen model lag "
                f"{frozen_lag}."
            )
        selected_indices = frozen["selected_indices"]
        expected_indices = np.flatnonzero(statistics["selected"])
        if not np.array_equal(selected_indices, expected_indices):
            raise ValueError(
                "Frozen model variables do not match current training "
                "coverage selection."
            )
        sufficient = {
            "selected_indices": selected_indices,
            "selected_medians": frozen["selected_medians"],
            "selected_iqr": frozen["selected_iqr"],
            "transition_rows": 0,
            "patient_count": sum(
                row["split"] == "train" for row in manifest
            ),
        }
        coefficient = frozen["coefficient"]
        selected_lambda = float(frozen["ridge_lambda"][0])
        source_summary_path = args.model_input.parent / "summary.json"
        source_summary = (
            json.loads(source_summary_path.read_text(encoding="utf-8"))
            if source_summary_path.is_file()
            else {}
        )
        sufficient["transition_rows"] = int(
            source_summary.get("training_transitions", 0)
        )
        selection_path = args.model_input.parent / "model-selection.csv"
        if selection_path.is_file():
            with selection_path.open(newline="", encoding="utf-8") as handle:
                selection_rows = list(csv.DictReader(handle))
        else:
            selection_rows = [
                {
                    "ridge_lambda": selected_lambda,
                    "validation_horizon_hours": source_summary.get(
                        "selection_horizon_hours", args.tuning_horizon
                    ),
                    "validation_stride": source_summary.get(
                        "selection_stride", args.tuning_stride
                    ),
                    "mean_patient_nmae": "loaded_frozen_model",
                }
            ]
        selection_horizon = int(
            source_summary.get(
                "selection_horizon_hours", args.tuning_horizon
            )
        )
        selection_stride = int(
            source_summary.get("selection_stride", args.tuning_stride)
        )
    else:
        sufficient = fit_sufficient_statistics(
            data_root,
            manifest,
            statistics,
            args.lag,
        )
        selection_rows: list[dict[str, Any]] = []
        candidates: dict[float, np.ndarray] = {}
        for ridge_lambda in ridge_lambdas:
            candidate = solve_ridge(sufficient, ridge_lambda)
            candidates[ridge_lambda] = candidate
            score = validation_score(
                data_root,
                manifest,
                statistics,
                sufficient,
                candidate,
                horizon=args.tuning_horizon,
                min_context=args.min_context,
                stride=args.tuning_stride,
            )
            selection_rows.append(
                {
                    "ridge_lambda": ridge_lambda,
                    "validation_horizon_hours": args.tuning_horizon,
                    "validation_stride": args.tuning_stride,
                    "mean_patient_nmae": score,
                }
            )
            print(
                f"lambda={ridge_lambda:g} "
                f"validation_nmae={score:.8f}",
                flush=True,
            )

        selected_row = min(
            selection_rows,
            key=lambda row: (
                float(row["mean_patient_nmae"]),
                float(row["ridge_lambda"]),
            ),
        )
        selected_lambda = float(selected_row["ridge_lambda"])
        coefficient = candidates[selected_lambda]
        selection_horizon = args.tuning_horizon
        selection_stride = args.tuning_stride
    metrics, patient_metrics, summary = evaluate(
        data_root,
        manifest,
        statistics,
        sufficient,
        coefficient,
        splits=splits,
        horizons=horizons,
        min_context=args.min_context,
        stride=args.stride,
        common_anchor_maximum_horizon=common_anchor_maximum_horizon,
        include_detail=True,
    )
    summary.update(
        {
            "lag": args.lag,
            "selected_ridge_lambda": selected_lambda,
            "selection_metric": "validation mean patient NMAE",
            "selection_horizon_hours": selection_horizon,
            "selection_stride": selection_stride,
            "training_transitions": sufficient["transition_rows"],
            "training_patients": sufficient["patient_count"],
            "horizons": horizons,
            "evaluation_stride": args.stride,
            "common_anchor_maximum_horizon": (
                common_anchor_maximum_horizon
            ),
            "requested_splits": sorted(splits),
            "model_input": str(args.model_input) if args.model_input else None,
        }
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "metrics-by-variable.csv", metrics)
    write_csv(args.output_dir / "patient-metrics.csv", patient_metrics)
    write_csv(args.output_dir / "model-selection.csv", selection_rows)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    np.savez_compressed(
        args.output_dir / "ridge-var-model.npz",
        coefficient=coefficient,
        selected_indices=sufficient["selected_indices"],
        selected_medians=sufficient["selected_medians"],
        selected_iqr=sufficient["selected_iqr"],
        lag=np.asarray([args.lag], dtype=np.int64),
        ridge_lambda=np.asarray([selected_lambda], dtype=np.float64),
    )
    print(
        json.dumps(
            {
                "selected_ridge_lambda": selected_lambda,
                "metric_rows": len(metrics),
                "patient_metric_rows": len(patient_metrics),
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
