#!/usr/bin/env python3
"""Run deterministic clinical-rollout baselines on PhysioNet 2019."""

from __future__ import annotations

import argparse
import csv
import json
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DYNAMIC_COLUMNS = [
    "HR",
    "O2Sat",
    "Temp",
    "SBP",
    "MAP",
    "DBP",
    "Resp",
    "EtCO2",
    "BaseExcess",
    "HCO3",
    "FiO2",
    "pH",
    "PaCO2",
    "SaO2",
    "AST",
    "BUN",
    "Alkalinephos",
    "Calcium",
    "Chloride",
    "Creatinine",
    "Bilirubin_direct",
    "Glucose",
    "Lactate",
    "Magnesium",
    "Phosphate",
    "Potassium",
    "Bilirubin_total",
    "TroponinI",
    "Hct",
    "Hgb",
    "PTT",
    "WBC",
    "Fibrinogen",
    "Platelets",
]
MODELS = ("locf", "global_median", "hourly_median")
PRESSURE_INDICES = tuple(DYNAMIC_COLUMNS.index(name) for name in ("SBP", "MAP", "DBP"))


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_patient(path: Path) -> tuple[np.ndarray, np.ndarray]:
    frame = pd.read_csv(path, sep="|", usecols=DYNAMIC_COLUMNS + ["ICULOS"])
    return (
        frame[DYNAMIC_COLUMNS].to_numpy(dtype=np.float64, copy=True),
        frame["ICULOS"].to_numpy(dtype=np.int32, copy=True),
    )


def fit_statistics(
    data_root: Path,
    manifest: list[dict[str, str]],
    coverage_threshold: float,
    hour_cap: int,
) -> dict[str, Any]:
    chunks: list[np.ndarray] = []
    for row in manifest:
        if row["split"] != "train":
            continue
        values, iculos = read_patient(data_root / row["relative_path"])
        combined = np.column_stack([values, iculos])
        chunks.append(combined)
    if not chunks:
        raise ValueError("No training patients found in split manifest.")
    matrix = np.concatenate(chunks, axis=0)
    values = matrix[:, : len(DYNAMIC_COLUMNS)]
    iculos = matrix[:, -1].astype(np.int32)
    coverage = np.mean(~np.isnan(values), axis=0)
    selected = coverage >= coverage_threshold
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        medians = np.nanmedian(values, axis=0)
        q25 = np.nanquantile(values, 0.25, axis=0)
        q75 = np.nanquantile(values, 0.75, axis=0)
        low = np.nanquantile(values, 0.001, axis=0)
        high = np.nanquantile(values, 0.999, axis=0)
    medians[~np.isfinite(medians)] = 0.0
    q25[~np.isfinite(q25)] = medians[~np.isfinite(q25)]
    q75[~np.isfinite(q75)] = medians[~np.isfinite(q75)]
    low[~np.isfinite(low)] = medians[~np.isfinite(low)]
    high[~np.isfinite(high)] = medians[~np.isfinite(high)]
    iqr = q75 - q25
    iqr[~np.isfinite(iqr) | (iqr <= 0)] = 1.0

    hourly = np.tile(medians, (hour_cap + 1, 1))
    capped_hours = np.clip(iculos, 0, hour_cap)
    for hour in range(hour_cap + 1):
        hour_values = values[capped_hours == hour]
        if hour_values.size:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                hour_medians = np.nanmedian(hour_values, axis=0)
            valid = np.isfinite(hour_medians)
            hourly[hour, valid] = hour_medians[valid]

    return {
        "coverage": coverage,
        "selected": selected,
        "medians": medians,
        "iqr": iqr,
        "low": low,
        "high": high,
        "hourly_medians": hourly,
        "hour_cap": hour_cap,
        "coverage_threshold": coverage_threshold,
        "training_rows": int(values.shape[0]),
        "training_patients": sum(row["split"] == "train" for row in manifest),
    }


def locf_arrays(values: np.ndarray, fallback: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    time_steps, variables = values.shape
    output = np.empty_like(values)
    seen = np.zeros_like(values, dtype=bool)
    last = fallback.copy()
    has_seen = np.zeros(variables, dtype=bool)
    for index in range(time_steps):
        observed = ~np.isnan(values[index])
        last[observed] = values[index, observed]
        has_seen |= observed
        output[index] = last
        seen[index] = has_seen
    return output, seen


def new_accumulator() -> dict[str, float]:
    return {"count": 0.0, "sum_abs": 0.0, "sum_sq": 0.0}


def update_accumulator(
    accumulator: dict[str, float],
    prediction: np.ndarray,
    target: np.ndarray,
) -> None:
    error = prediction - target
    accumulator["count"] += float(error.size)
    accumulator["sum_abs"] += float(np.sum(np.abs(error)))
    accumulator["sum_sq"] += float(np.sum(error**2))


def evaluate(
    data_root: Path,
    manifest: list[dict[str, str]],
    statistics: dict[str, Any],
    splits: set[str],
    horizons: list[int],
    min_context: int,
    stride: int,
    common_anchor_maximum_horizon: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    selected_indices = np.flatnonzero(statistics["selected"])
    selected_names = [DYNAMIC_COLUMNS[index] for index in selected_indices]
    aggregate: dict[tuple[str, str, int, int], dict[str, float]] = defaultdict(
        new_accumulator
    )
    patient_rows: list[dict[str, Any]] = []
    constraint_counts: dict[tuple[str, str, int], list[int]] = defaultdict(
        lambda: [0, 0]
    )
    evaluated_patients: dict[str, int] = defaultdict(int)

    for row in manifest:
        split = row["split"]
        if split not in splits:
            continue
        values, iculos = read_patient(data_root / row["relative_path"])
        if len(values) < min_context + common_anchor_maximum_horizon:
            continue
        locf, _ = locf_arrays(values, statistics["medians"])
        evaluated_patients[split] += 1
        last_anchor = len(values) - common_anchor_maximum_horizon - 1
        anchors = np.arange(
            min_context - 1,
            last_anchor + 1,
            stride,
            dtype=int,
        )

        for horizon in horizons:
            target_indices = anchors + horizon
            targets = values[target_indices]
            target_hours = np.clip(
                iculos[target_indices], 0, statistics["hour_cap"]
            )
            predictions = {
                "locf": locf[anchors],
                "global_median": np.broadcast_to(
                    statistics["medians"], targets.shape
                ),
                "hourly_median": statistics["hourly_medians"][target_hours],
            }

            for model, prediction in predictions.items():
                patient_abs_sum = 0.0
                patient_scaled_count = 0
                for variable_index in selected_indices:
                    observed = ~np.isnan(targets[:, variable_index])
                    if not np.any(observed):
                        continue
                    pred = prediction[observed, variable_index]
                    actual = targets[observed, variable_index]
                    update_accumulator(
                        aggregate[(split, model, horizon, variable_index)],
                        pred,
                        actual,
                    )
                    patient_abs_sum += float(
                        np.sum(
                            np.abs(pred - actual) / statistics["iqr"][variable_index]
                        )
                    )
                    patient_scaled_count += int(np.sum(observed))

                if patient_scaled_count:
                    patient_rows.append(
                        {
                            "patient_id": row["patient_id"],
                            "cohort": row["cohort"],
                            "split": split,
                            "model": model,
                            "horizon_hours": horizon,
                            "observed_targets": patient_scaled_count,
                            "patient_nmae": patient_abs_sum / patient_scaled_count,
                        }
                    )

                sbp, map_index, dbp = PRESSURE_INDICES
                pressure = prediction[:, [sbp, map_index, dbp]]
                violations = np.sum(
                    (pressure[:, 0] < pressure[:, 1])
                    | (pressure[:, 1] < pressure[:, 2])
                )
                counter = constraint_counts[(split, model, horizon)]
                counter[0] += int(violations)
                counter[1] += int(pressure.shape[0])

    metric_rows: list[dict[str, Any]] = []
    for (split, model, horizon, variable_index), accumulator in sorted(
        aggregate.items()
    ):
        count = int(accumulator["count"])
        if not count:
            continue
        mae = accumulator["sum_abs"] / count
        rmse = np.sqrt(accumulator["sum_sq"] / count)
        metric_rows.append(
            {
                "split": split,
                "model": model,
                "horizon_hours": horizon,
                "variable": DYNAMIC_COLUMNS[variable_index],
                "observed_targets": count,
                "mae": mae,
                "rmse": rmse,
                "nmae": mae / statistics["iqr"][variable_index],
            }
        )

    summary = {
        "selected_variables": selected_names,
        "coverage_threshold": statistics["coverage_threshold"],
        "training_rows": statistics["training_rows"],
        "training_patients": statistics["training_patients"],
        "evaluated_patients": dict(sorted(evaluated_patients.items())),
        "pressure_constraint": [
            {
                "split": split,
                "model": model,
                "horizon_hours": horizon,
                "violations": values[0],
                "evaluated_states": values[1],
                "violations_per_1000_states": (
                    1000 * values[0] / values[1] if values[1] else None
                ),
            }
            for (split, model, horizon), values in sorted(constraint_counts.items())
        ],
    }
    return metric_rows, patient_rows, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows produced for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--coverage-threshold", type=float, default=0.05)
    parser.add_argument("--hour-cap", type=int, default=72)
    parser.add_argument("--min-context", type=int, default=12)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument(
        "--common-anchor-maximum-horizon",
        type=int,
        default=0,
        help=(
            "Require every anchor to support this horizon for all reported "
            "metrics. Zero uses the maximum requested horizon."
        ),
    )
    parser.add_argument("--horizons", default="1,3,6,12,24")
    parser.add_argument(
        "--splits", default="internal_test,external_test"
    )
    args = parser.parse_args()

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
    manifest = read_manifest(args.split_manifest)
    data_root = args.data_root.resolve()
    statistics = fit_statistics(
        data_root,
        manifest,
        args.coverage_threshold,
        args.hour_cap,
    )
    metrics, patient_metrics, summary = evaluate(
        data_root,
        manifest,
        statistics,
        splits,
        horizons,
        args.min_context,
        args.stride,
        common_anchor_maximum_horizon,
    )
    write_csv(args.output_dir / "metrics-by-variable.csv", metrics)
    write_csv(args.output_dir / "patient-metrics.csv", patient_metrics)
    summary.update(
        {
            "models": list(MODELS),
            "horizons": horizons,
            "min_context": args.min_context,
            "stride": args.stride,
            "common_anchor_maximum_horizon": (
                common_anchor_maximum_horizon
            ),
            "requested_splits": sorted(splits),
            "variable_coverage": {
                name: float(coverage)
                for name, coverage in zip(
                    DYNAMIC_COLUMNS, statistics["coverage"], strict=True
                )
            },
            "training_median": {
                name: float(value)
                for name, value in zip(
                    DYNAMIC_COLUMNS, statistics["medians"], strict=True
                )
            },
            "training_iqr": {
                name: float(value)
                for name, value in zip(
                    DYNAMIC_COLUMNS, statistics["iqr"], strict=True
                )
            },
        }
    )
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "metric_rows": len(metrics),
                "patient_metric_rows": len(patient_metrics),
                "selected_variables": len(summary["selected_variables"]),
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
