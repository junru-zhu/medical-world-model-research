#!/usr/bin/env python3
"""Generate publication tables and paired inference from frozen experiment files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from summarize_neural_matrix import validate_run_artifacts


MODEL_LABELS = {
    "locf": "Last observation carried forward",
    "global_median": "Global median",
    "hourly_median": "Hourly median",
    "ridge_var": "Ridge vector autoregression",
    "grud": "Probabilistic GRU-D-style model",
    "transformer": "Causally masked Transformer",
    "rssm": "Recurrent state-space model",
}
NEURAL_MODELS = ("grud", "transformer", "rssm")
HORIZONS = (1, 3, 6, 12, 24)
PATIENT_METRICS = (
    "patient_nmae",
    "patient_crps",
    "coverage_90",
    "mean_interval_width_scaled",
    "patient_nll",
    "mask_brier",
)
SUMMARY_METRICS = PATIENT_METRICS + ("coverage_error_90",)
PRIMARY_PAIRS = (
    ("grud", "transformer"),
    ("grud", "ridge_var"),
    ("transformer", "ridge_var"),
    ("rssm", "ridge_var"),
    ("ridge_var", "locf"),
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def neural_run_paths(
    result_root: Path, models: list[str], seeds: list[int]
) -> tuple[list[dict[str, Any]], list[str]]:
    runs: list[dict[str, Any]] = []
    missing: list[str] = []
    for model in models:
        for seed in seeds:
            run_dir = result_root / model / f"seed-{seed}"
            paths = {
                "training": run_dir / "summary.json",
                "zero_shot": run_dir / "evaluation/patient-metrics.csv",
                "raw_summary": run_dir / "evaluation/summary.json",
                "constraints": run_dir / "evaluation/constraints.csv",
                "recalibrated": (
                    run_dir
                    / "external-test-recalibrated/patient-metrics.csv"
                ),
                "recalibrated_summary": (
                    run_dir / "external-test-recalibrated/summary.json"
                ),
                "calibration": (
                    run_dir
                    / "external-calibration-fit/spread-calibration.json"
                ),
            }
            absent = [name for name, path in paths.items() if not path.is_file()]
            if absent:
                missing.extend(
                    f"{model}/seed-{seed}:{name}" for name in absent
                )
                continue
            invalid = validate_run_artifacts(
                model=model,
                seed=seed,
                run_dir=run_dir,
                required={
                    "training": paths["training"],
                    "raw": paths["raw_summary"],
                    "recalibrated": paths["recalibrated_summary"],
                    "calibration": paths["calibration"],
                    "constraints": paths["constraints"],
                },
            )
            if invalid:
                missing.extend(
                    f"{model}/seed-{seed}:invalid:{item}"
                    for item in invalid
                )
                continue
            runs.append({"model": model, "seed": seed, **paths})
    return runs, missing


def load_patient_metrics(
    *,
    baseline_dir: Path,
    ridge_dir: Path,
    runs: list[dict[str, Any]],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in (
        baseline_dir / "patient-metrics.csv",
        ridge_dir / "patient-metrics.csv",
    ):
        frame = pd.read_csv(path)
        frame["seed"] = -1
        frame["evaluation"] = "zero_shot"
        for metric in PATIENT_METRICS:
            if metric not in frame:
                frame[metric] = np.nan
        frames.append(frame)
    for run in runs:
        for evaluation, key in (
            ("zero_shot", "zero_shot"),
            ("recalibrated", "recalibrated"),
        ):
            frame = pd.read_csv(run[key])
            frame["seed"] = run["seed"]
            frame["evaluation"] = evaluation
            frames.append(frame)
    combined = pd.concat(frames, ignore_index=True, sort=False)
    required = {
        "patient_id",
        "split",
        "model",
        "seed",
        "evaluation",
        "horizon_hours",
        "patient_nmae",
    }
    missing = required - set(combined)
    if missing:
        raise ValueError(f"Patient metric columns missing: {sorted(missing)}")
    return combined


def load_constraints(
    *,
    baseline_dir: Path,
    ridge_dir: Path,
    runs: list[dict[str, Any]],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    baseline = read_json(baseline_dir / "summary.json")
    for row in baseline["pressure_constraint"]:
        rows.append(
            {
                "split": row["split"],
                "model": row["model"],
                "seed": -1,
                "horizon_hours": row["horizon_hours"],
                "constraint": "pressure_order",
                "violations_per_1000_states": row[
                    "violations_per_1000_states"
                ],
            }
        )
    ridge = read_json(ridge_dir / "summary.json")
    for row in ridge["pressure_constraint"]:
        rows.append(
            {
                "split": row["split"],
                "model": "ridge_var",
                "seed": -1,
                "horizon_hours": row["horizon_hours"],
                "constraint": "pressure_order",
                "violations_per_1000_states": row[
                    "violations_per_1000_states"
                ],
            }
        )
    for run in runs:
        frame = pd.read_csv(run["constraints"])
        frame["seed"] = run["seed"]
        rows.extend(
            frame[
                [
                    "split",
                    "model",
                    "seed",
                    "horizon_hours",
                    "constraint",
                    "violations_per_1000_states",
                ]
            ].to_dict("records")
        )
    return pd.DataFrame(rows)


def load_training_and_calibration(
    runs: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    training_rows: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    for run in runs:
        training = read_json(run["training"])
        training_rows.append(
            {
                "model": run["model"],
                "seed": run["seed"],
                "best_epoch": training["best_epoch"],
                "epochs_run": training["epochs_run"],
                "best_validation_loss": training["best_validation_loss"],
                "parameter_count": training["parameter_count"],
            }
        )
        calibration = read_json(run["calibration"])
        for horizon, scale in calibration["horizon_scales"].items():
            calibration_rows.append(
                {
                    "model": run["model"],
                    "seed": run["seed"],
                    "horizon_hours": int(horizon),
                    "spread_scale": scale,
                    "observed_targets": calibration["observed_targets"][
                        horizon
                    ],
                }
            )
    return pd.DataFrame(training_rows), pd.DataFrame(calibration_rows)


def seed_patient_macro(patient: pd.DataFrame) -> pd.DataFrame:
    columns = [
        metric for metric in PATIENT_METRICS if metric in patient.columns
    ]
    result = (
        patient.groupby(
            [
                "evaluation",
                "split",
                "model",
                "seed",
                "horizon_hours",
            ],
            dropna=False,
        )[columns]
        .mean()
        .reset_index()
    )
    result["coverage_error_90"] = np.abs(result["coverage_90"] - 0.9)
    return result


def verify_recalibration_invariants(patient: pd.DataFrame) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for model in NEURAL_MODELS:
        model_seeds = sorted(
            patient[(patient["model"] == model) & (patient["seed"] >= 0)][
                "seed"
            ].unique()
        )
        for seed in model_seeds:
            for horizon in HORIZONS:
                raw = patient[
                    (patient["model"] == model)
                    & (patient["seed"] == seed)
                    & (patient["evaluation"] == "zero_shot")
                    & (patient["split"] == "external_test")
                    & (patient["horizon_hours"] == horizon)
                ][["patient_id", "patient_nmae", "mask_brier"]]
                recalibrated = patient[
                    (patient["model"] == model)
                    & (patient["seed"] == seed)
                    & (patient["evaluation"] == "recalibrated")
                    & (patient["split"] == "external_test")
                    & (patient["horizon_hours"] == horizon)
                ][["patient_id", "patient_nmae", "mask_brier"]]
                merged = raw.merge(
                    recalibrated,
                    on="patient_id",
                    how="outer",
                    suffixes=("_raw", "_recalibrated"),
                    indicator=True,
                )
                if not (merged["_merge"] == "both").all():
                    raise ValueError(
                        "Raw and recalibrated patient sets differ for "
                        f"{model}, seed {seed}, horizon {horizon}."
                    )
                nmae_difference = np.abs(
                    merged["patient_nmae_raw"]
                    - merged["patient_nmae_recalibrated"]
                )
                mask_difference = np.abs(
                    merged["mask_brier_raw"]
                    - merged["mask_brier_recalibrated"]
                )
                maximum_nmae_difference = float(nmae_difference.max())
                maximum_mask_difference = float(mask_difference.max())
                if maximum_nmae_difference > 1e-6:
                    raise ValueError(
                        "Spread recalibration changed point predictions for "
                        f"{model}, seed {seed}, horizon {horizon}: "
                        f"max patient NMAE delta {maximum_nmae_difference}."
                    )
                if maximum_mask_difference > 1e-10:
                    raise ValueError(
                        "Spread recalibration changed mask predictions for "
                        f"{model}, seed {seed}, horizon {horizon}: "
                        f"max patient Brier delta {maximum_mask_difference}."
                    )
                checks.append(
                    {
                        "model": model,
                        "seed": int(seed),
                        "horizon_hours": horizon,
                        "patients": len(merged),
                        "maximum_patient_nmae_difference": (
                            maximum_nmae_difference
                        ),
                        "maximum_patient_mask_brier_difference": (
                            maximum_mask_difference
                        ),
                        "pass": True,
                    }
                )
    return checks


def aggregate_seeds(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    neural = seed_metrics[seed_metrics["seed"] >= 0]
    rows: list[dict[str, Any]] = []
    keys = ["evaluation", "split", "model", "horizon_hours"]
    for key, group in neural.groupby(keys, sort=True):
        base = dict(zip(keys, key, strict=True))
        for metric in SUMMARY_METRICS:
            values = group[metric].dropna().to_numpy(dtype=float)
            if not len(values):
                continue
            rows.append(
                {
                    **base,
                    "metric": metric,
                    "seeds": len(values),
                    "mean": float(values.mean()),
                    "standard_deviation": (
                        float(values.std(ddof=1)) if len(values) > 1 else 0.0
                    ),
                    "minimum": float(values.min()),
                    "maximum": float(values.max()),
                }
            )
    return pd.DataFrame(rows)


def aggregate_constraints(constraints: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    keys = ["split", "model", "horizon_hours", "constraint"]
    for key, group in constraints.groupby(keys, sort=True):
        values = group["violations_per_1000_states"].to_numpy(dtype=float)
        rows.append(
            {
                **dict(zip(keys, key, strict=True)),
                "seeds": int((group["seed"] >= 0).sum()) or 1,
                "mean": float(values.mean()),
                "standard_deviation": (
                    float(values.std(ddof=1)) if len(values) > 1 else 0.0
                ),
                "minimum": float(values.min()),
                "maximum": float(values.max()),
            }
        )
    return pd.DataFrame(rows)


def model_value(
    seed_metrics: pd.DataFrame,
    *,
    model: str,
    split: str,
    horizon: int,
    metric: str,
    evaluation: str = "zero_shot",
) -> tuple[float, float]:
    selected = seed_metrics[
        (seed_metrics["model"] == model)
        & (seed_metrics["split"] == split)
        & (seed_metrics["horizon_hours"] == horizon)
        & (seed_metrics["evaluation"] == evaluation)
    ][metric].dropna()
    if not len(selected):
        return float("nan"), float("nan")
    return float(selected.mean()), (
        float(selected.std(ddof=1)) if len(selected) > 1 else 0.0
    )


def constraint_value(
    aggregate: pd.DataFrame,
    *,
    model: str,
    split: str,
    horizon: int,
    constraint: str,
) -> tuple[float, float]:
    selected = aggregate[
        (aggregate["model"] == model)
        & (aggregate["split"] == split)
        & (aggregate["horizon_hours"] == horizon)
        & (aggregate["constraint"] == constraint)
    ]
    if selected.empty:
        return float("nan"), float("nan")
    row = selected.iloc[0]
    return float(row["mean"]), float(row["standard_deviation"])


def main_table(
    seed_metrics: pd.DataFrame, aggregate_constraints_frame: pd.DataFrame
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for model in MODEL_LABELS:
        row: dict[str, Any] = {
            "model": model,
            "model_label": MODEL_LABELS[model],
        }
        for horizon in (1, 12, 24):
            mean, standard_deviation = model_value(
                seed_metrics,
                model=model,
                split="external_test",
                horizon=horizon,
                metric="patient_nmae",
            )
            row[f"nmae_{horizon}h_mean"] = mean
            row[f"nmae_{horizon}h_seed_sd"] = standard_deviation
        for metric in (
            "patient_crps",
            "coverage_90",
            "coverage_error_90",
            "mask_brier",
        ):
            mean, standard_deviation = model_value(
                seed_metrics,
                model=model,
                split="external_test",
                horizon=12,
                metric=metric,
            )
            row[f"{metric}_12h_mean"] = mean
            row[f"{metric}_12h_seed_sd"] = standard_deviation
        mean, standard_deviation = constraint_value(
            aggregate_constraints_frame,
            model=model,
            split="external_test",
            horizon=12,
            constraint="pressure_order",
        )
        row["pressure_violations_12h_per_1000_mean"] = mean
        row["pressure_violations_12h_per_1000_seed_sd"] = standard_deviation
        rows.append(row)
    return pd.DataFrame(rows)


def calibration_table(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for model in NEURAL_MODELS:
        for horizon in HORIZONS:
            row: dict[str, Any] = {
                "model": model,
                "model_label": MODEL_LABELS[model],
                "horizon_hours": horizon,
            }
            for evaluation in ("zero_shot", "recalibrated"):
                for metric in (
                    "coverage_90",
                    "coverage_error_90",
                    "patient_crps",
                    "mean_interval_width_scaled",
                    "patient_nll",
                ):
                    mean, standard_deviation = model_value(
                        seed_metrics,
                        model=model,
                        split="external_test",
                        horizon=horizon,
                        metric=metric,
                        evaluation=evaluation,
                    )
                    row[f"{evaluation}_{metric}_mean"] = mean
                    row[f"{evaluation}_{metric}_seed_sd"] = standard_deviation
            rows.append(row)
    return pd.DataFrame(rows)


def cross_site_table(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for model in MODEL_LABELS:
        seeds = sorted(
            seed_metrics[
                (seed_metrics["model"] == model)
                & (seed_metrics["evaluation"] == "zero_shot")
            ]["seed"].unique()
        )
        for seed in seeds:
            item: dict[str, Any] = {
                "model": model,
                "model_label": MODEL_LABELS[model],
                "seed": int(seed),
            }
            complete = True
            for metric in ("patient_nmae", "coverage_90", "mask_brier"):
                for split in ("internal_test", "external_test"):
                    selected = seed_metrics[
                        (seed_metrics["model"] == model)
                        & (seed_metrics["seed"] == seed)
                        & (seed_metrics["evaluation"] == "zero_shot")
                        & (seed_metrics["split"] == split)
                        & (seed_metrics["horizon_hours"] == 12)
                    ][metric].dropna()
                    value = (
                        float(selected.iloc[0])
                        if len(selected)
                        else float("nan")
                    )
                    item[f"{split}_{metric}_12h"] = value
                    if metric == "patient_nmae" and not np.isfinite(value):
                        complete = False
            if complete:
                internal = item["internal_test_patient_nmae_12h"]
                external = item["external_test_patient_nmae_12h"]
                item["relative_nmae_degradation_percent"] = (
                    100.0 * (external - internal) / internal
                )
            rows.append(item)
    return pd.DataFrame(rows)


def average_ranks(values: np.ndarray) -> np.ndarray:
    return pd.Series(values).rank(method="average").to_numpy(dtype=float)


def spearman(values_a: np.ndarray, values_b: np.ndarray) -> float:
    ranks_a = average_ranks(values_a)
    ranks_b = average_ranks(values_b)
    if np.all(ranks_a == ranks_a[0]) or np.all(ranks_b == ranks_b[0]):
        return float("nan")
    return float(np.corrcoef(ranks_a, ranks_b)[0, 1])


def pairwise_reversal_fraction(
    values_a: np.ndarray, values_b: np.ndarray
) -> float:
    reversals = 0
    comparable = 0
    for first in range(len(values_a)):
        for second in range(first + 1, len(values_a)):
            difference_a = values_a[first] - values_a[second]
            difference_b = values_b[first] - values_b[second]
            if difference_a == 0 or difference_b == 0:
                continue
            comparable += 1
            reversals += int(difference_a * difference_b < 0)
    return float(reversals / comparable) if comparable else float("nan")


def rank_vector(
    seed_metrics: pd.DataFrame,
    *,
    models: list[str],
    seed: int,
    split: str,
    horizon: int,
) -> np.ndarray:
    values = []
    for model in models:
        model_seed = seed if model in NEURAL_MODELS else -1
        selected = seed_metrics[
            (seed_metrics["model"] == model)
            & (seed_metrics["seed"] == model_seed)
            & (seed_metrics["evaluation"] == "zero_shot")
            & (seed_metrics["split"] == split)
            & (seed_metrics["horizon_hours"] == horizon)
        ]["patient_nmae"]
        if len(selected) != 1:
            raise ValueError(
                f"Missing rank value: {model}, {seed}, {split}, {horizon}"
            )
        values.append(float(selected.iloc[0]))
    return np.asarray(values)


def rank_stability(seed_metrics: pd.DataFrame, seeds: list[int]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    models = list(MODEL_LABELS)
    for seed in seeds:
        for split in ("internal_test", "external_test"):
            one_hour = rank_vector(
                seed_metrics,
                models=models,
                seed=seed,
                split=split,
                horizon=1,
            )
            for comparison_horizon in (12, 24):
                comparison = rank_vector(
                    seed_metrics,
                    models=models,
                    seed=seed,
                    split=split,
                    horizon=comparison_horizon,
                )
                rows.append(
                    {
                        "seed": seed,
                        "comparison_type": "cross_horizon",
                        "context": split,
                        "from_condition": "1h",
                        "to_condition": f"{comparison_horizon}h",
                        "spearman_rank_correlation": spearman(
                            one_hour, comparison
                        ),
                        "pairwise_reversal_fraction": (
                            pairwise_reversal_fraction(
                                one_hour, comparison
                            )
                        ),
                        "models": len(models),
                    }
                )
        for horizon in (12, 24):
            internal = rank_vector(
                seed_metrics,
                models=models,
                seed=seed,
                split="internal_test",
                horizon=horizon,
            )
            external = rank_vector(
                seed_metrics,
                models=models,
                seed=seed,
                split="external_test",
                horizon=horizon,
            )
            rows.append(
                {
                    "seed": seed,
                    "comparison_type": "cross_site",
                    "context": f"{horizon}h",
                    "from_condition": "internal_test",
                    "to_condition": "external_test",
                    "spearman_rank_correlation": spearman(
                        internal, external
                    ),
                    "pairwise_reversal_fraction": (
                        pairwise_reversal_fraction(internal, external)
                    ),
                    "models": len(models),
                }
            )
    return pd.DataFrame(rows)


def patient_matrix(
    patient: pd.DataFrame,
    *,
    model: str,
    split: str,
    horizon: int,
    metric: str,
    seeds: list[int],
) -> tuple[list[str], np.ndarray]:
    model_seeds = seeds if model in NEURAL_MODELS else [-1]
    frames: list[pd.Series] = []
    for seed in model_seeds:
        selected = patient[
            (patient["model"] == model)
            & (patient["seed"] == seed)
            & (patient["evaluation"] == "zero_shot")
            & (patient["split"] == split)
            & (patient["horizon_hours"] == horizon)
        ][["patient_id", metric]].dropna()
        if selected["patient_id"].duplicated().any():
            raise ValueError(
                f"Duplicate patient rows for {model}, seed {seed}, "
                f"{split}, horizon {horizon}, metric {metric}."
            )
        series = selected.set_index("patient_id")[metric]
        frames.append(series)
    common = frames[0].index
    for frame in frames[1:]:
        common = common.intersection(frame.index)
    common = common.sort_values()
    matrix = np.stack(
        [frame.loc[common].to_numpy(dtype=float) for frame in frames],
        axis=0,
    )
    return common.astype(str).tolist(), matrix


def paired_bootstrap_contrast(
    patient: pd.DataFrame,
    *,
    model_a: str,
    model_b: str,
    split: str,
    horizon: int,
    metric: str,
    seeds: list[int],
    replicates: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    ids_a, values_a = patient_matrix(
        patient,
        model=model_a,
        split=split,
        horizon=horizon,
        metric=metric,
        seeds=seeds,
    )
    ids_b, values_b = patient_matrix(
        patient,
        model=model_b,
        split=split,
        horizon=horizon,
        metric=metric,
        seeds=seeds,
    )
    common = sorted(set(ids_a).intersection(ids_b))
    index_a = {patient_id: index for index, patient_id in enumerate(ids_a)}
    index_b = {patient_id: index for index, patient_id in enumerate(ids_b)}
    columns_a = [index_a[patient_id] for patient_id in common]
    columns_b = [index_b[patient_id] for patient_id in common]
    values_a = values_a[:, columns_a]
    values_b = values_b[:, columns_b]
    patient_values_a = values_a.mean(axis=0)
    patient_values_b = values_b.mean(axis=0)
    observed = float(patient_values_a.mean() - patient_values_b.mean())
    draws = np.empty(replicates, dtype=float)
    patient_count = len(common)
    for index in range(replicates):
        patient_indices = rng.integers(
            0, patient_count, size=patient_count
        )
        mean_a = patient_values_a[patient_indices].mean()
        mean_b = patient_values_b[patient_indices].mean()
        draws[index] = mean_a - mean_b
    return {
        "split": split,
        "horizon_hours": horizon,
        "metric": metric,
        "model_a": model_a,
        "model_a_label": MODEL_LABELS[model_a],
        "model_b": model_b,
        "model_b_label": MODEL_LABELS[model_b],
        "patients": patient_count,
        "fixed_neural_seeds": len(seeds),
        "difference_a_minus_b": observed,
        "ci_95_lower": float(np.quantile(draws, 0.025)),
        "ci_95_upper": float(np.quantile(draws, 0.975)),
        "interpretation": (
            "Negative values favor model A because lower NMAE is better."
        ),
    }


def rollout_area_table(seed_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in seed_metrics.groupby(
        ["evaluation", "split", "model", "seed"], sort=True
    ):
        evaluation, split, model, seed = key
        ordered = group.set_index("horizon_hours").reindex(HORIZONS)
        if ordered["patient_nmae"].isna().any():
            continue
        for metric in (
            "patient_nmae",
            "patient_crps",
            "coverage_error_90",
            "mask_brier",
        ):
            values = ordered[metric].to_numpy(dtype=float)
            if not np.isfinite(values).all():
                continue
            rows.append(
                {
                    "evaluation": evaluation,
                    "split": split,
                    "model": model,
                    "seed": int(seed),
                    "metric": metric,
                    "normalized_rollout_area": float(
                        np.trapezoid(values, np.asarray(HORIZONS)) / 23.0
                    ),
                }
            )
    return pd.DataFrame(rows)


def fixed_seed_patient_values(
    patient: pd.DataFrame,
    *,
    model: str,
    split: str,
    horizon: int,
    metric: str,
    seeds: list[int],
) -> tuple[list[str], np.ndarray]:
    patient_ids, matrix = patient_matrix(
        patient,
        model=model,
        split=split,
        horizon=horizon,
        metric=metric,
        seeds=seeds,
    )
    return patient_ids, matrix.mean(axis=0)


def independent_cross_site_bootstrap(
    patient: pd.DataFrame,
    *,
    model: str,
    horizon: int,
    seeds: list[int],
    replicates: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    internal_ids, internal = fixed_seed_patient_values(
        patient,
        model=model,
        split="internal_test",
        horizon=horizon,
        metric="patient_nmae",
        seeds=seeds,
    )
    external_ids, external = fixed_seed_patient_values(
        patient,
        model=model,
        split="external_test",
        horizon=horizon,
        metric="patient_nmae",
        seeds=seeds,
    )
    internal_mean = float(internal.mean())
    external_mean = float(external.mean())
    absolute = external_mean - internal_mean
    relative = 100.0 * absolute / internal_mean
    absolute_draws = np.empty(replicates, dtype=float)
    relative_draws = np.empty(replicates, dtype=float)
    for index in range(replicates):
        internal_draw = internal[
            rng.integers(0, len(internal), size=len(internal))
        ].mean()
        external_draw = external[
            rng.integers(0, len(external), size=len(external))
        ].mean()
        difference = external_draw - internal_draw
        absolute_draws[index] = difference
        relative_draws[index] = 100.0 * difference / internal_draw
    return {
        "model": model,
        "model_label": MODEL_LABELS[model],
        "horizon_hours": horizon,
        "internal_patients": len(internal_ids),
        "external_patients": len(external_ids),
        "internal_mean_nmae": internal_mean,
        "external_mean_nmae": external_mean,
        "absolute_degradation": absolute,
        "absolute_ci_95_lower": float(np.quantile(absolute_draws, 0.025)),
        "absolute_ci_95_upper": float(np.quantile(absolute_draws, 0.975)),
        "relative_degradation_percent": relative,
        "relative_ci_95_lower": float(np.quantile(relative_draws, 0.025)),
        "relative_ci_95_upper": float(np.quantile(relative_draws, 0.975)),
        "resampling": (
            "Independent patient bootstrap within internal and external "
            "cohorts after averaging the fixed neural seeds."
        ),
    }


def markdown_number(mean: float, standard_deviation: float) -> str:
    if not np.isfinite(mean):
        return "NA"
    if standard_deviation > 0:
        return f"{mean:.4f} ({standard_deviation:.4f})"
    return f"{mean:.4f}"


def build_report(
    *,
    main: pd.DataFrame,
    calibration: pd.DataFrame,
    contrasts: pd.DataFrame,
    cross_site_inference: pd.DataFrame,
    ranks: pd.DataFrame,
    recalibration_checks: list[dict[str, Any]],
    training: pd.DataFrame,
    seeds: list[int],
) -> str:
    lines = [
        "# Frozen Neural-Matrix Publication Summary",
        "",
        f"Models: {len(NEURAL_MODELS)} neural families; seeds: "
        + ", ".join(str(seed) for seed in seeds)
        + ".",
        "",
        "Values in parentheses are across-seed standard deviations. "
        "Deterministic baselines have no seed variation.",
        "",
        "## Descriptive Zero-Shot External-Test Results",
        "",
        "| Model | 1 h NMAE | 12 h NMAE | 24 h NMAE | 12 h CRPS | 12 h coverage error | 12 h mask Brier | 12 h rollout-state pressure violations/1,000 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in main.to_dict("records"):
        lines.append(
            "| {model_label} | {n1} | {n12} | {n24} | {crps} | "
            "{coverage} | {mask} | {pressure} |".format(
                model_label=row["model_label"],
                n1=markdown_number(
                    row["nmae_1h_mean"], row["nmae_1h_seed_sd"]
                ),
                n12=markdown_number(
                    row["nmae_12h_mean"], row["nmae_12h_seed_sd"]
                ),
                n24=markdown_number(
                    row["nmae_24h_mean"], row["nmae_24h_seed_sd"]
                ),
                crps=markdown_number(
                    row["patient_crps_12h_mean"],
                    row["patient_crps_12h_seed_sd"],
                ),
                coverage=markdown_number(
                    row["coverage_error_90_12h_mean"],
                    row["coverage_error_90_12h_seed_sd"],
                ),
                mask=markdown_number(
                    row["mask_brier_12h_mean"],
                    row["mask_brier_12h_seed_sd"],
                ),
                pressure=markdown_number(
                    row["pressure_violations_12h_per_1000_mean"],
                    row["pressure_violations_12h_per_1000_seed_sd"],
                ),
            )
        )
    lines.extend(
        [
            "",
            "## External Recalibration",
            "",
            "| Model | Horizon | Raw coverage | Recalibrated coverage | Raw width | Recalibrated width | Raw CRPS | Recalibrated CRPS | Raw Gaussian NLS | Recalibrated Gaussian NLS |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in calibration.to_dict("records"):
        lines.append(
            "| {model_label} | {horizon_hours} h | {raw_cov} | "
            "{recal_cov} | {raw_width} | {recal_width} | {raw_crps} | "
            "{recal_crps} | {raw_nll} | {recal_nll} |".format(
                model_label=row["model_label"],
                horizon_hours=row["horizon_hours"],
                raw_cov=markdown_number(
                    row["zero_shot_coverage_90_mean"],
                    row["zero_shot_coverage_90_seed_sd"],
                ),
                recal_cov=markdown_number(
                    row["recalibrated_coverage_90_mean"],
                    row["recalibrated_coverage_90_seed_sd"],
                ),
                raw_width=markdown_number(
                    row["zero_shot_mean_interval_width_scaled_mean"],
                    row["zero_shot_mean_interval_width_scaled_seed_sd"],
                ),
                recal_width=markdown_number(
                    row["recalibrated_mean_interval_width_scaled_mean"],
                    row["recalibrated_mean_interval_width_scaled_seed_sd"],
                ),
                raw_crps=markdown_number(
                    row["zero_shot_patient_crps_mean"],
                    row["zero_shot_patient_crps_seed_sd"],
                ),
                recal_crps=markdown_number(
                    row["recalibrated_patient_crps_mean"],
                    row["recalibrated_patient_crps_seed_sd"],
                ),
                raw_nll=markdown_number(
                    row["zero_shot_patient_nll_mean"],
                    row["zero_shot_patient_nll_seed_sd"],
                ),
                recal_nll=markdown_number(
                    row["recalibrated_patient_nll_mean"],
                    row["recalibrated_patient_nll_seed_sd"],
                ),
            )
        )
    maximum_nmae_invariance_error = max(
        row["maximum_patient_nmae_difference"]
        for row in recalibration_checks
    )
    maximum_mask_invariance_error = max(
        row["maximum_patient_mask_brier_difference"]
        for row in recalibration_checks
    )
    lines.extend(
        [
            "",
            "The raw and recalibrated runs used identical split-specific "
            "Monte Carlo streams. Maximum patient-level NMAE difference was "
            f"{maximum_nmae_invariance_error:.3e}; maximum mask-Brier "
            f"difference was {maximum_mask_invariance_error:.3e}.",
            "",
            "## Frozen 12-Hour Paired NMAE Contrasts",
            "",
            "| Split | Model A | Model B | A-B | 95% bootstrap interval | Patients |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in contrasts.to_dict("records"):
        lines.append(
            f"| {row['split']} | {row['model_a_label']} | "
            f"{row['model_b_label']} | "
            f"{row['difference_a_minus_b']:.4f} | "
            f"[{row['ci_95_lower']:.4f}, {row['ci_95_upper']:.4f}] | "
            f"{row['patients']} |"
        )
    lines.extend(
        [
            "",
            "Negative contrast values favor model A. Intervals use a "
            "patient bootstrap after averaging the five fixed neural seeds. "
            "Across-seed variation is reported separately.",
            "",
            "## Cross-Cohort 12-Hour NMAE Degradation",
            "",
            "| Model | Internal | Zero-shot external | Absolute change [95% CI] | Relative change [95% CI] |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in cross_site_inference.to_dict("records"):
        lines.append(
            f"| {row['model_label']} | {row['internal_mean_nmae']:.4f} | "
            f"{row['external_mean_nmae']:.4f} | "
            f"{row['absolute_degradation']:.4f} "
            f"[{row['absolute_ci_95_lower']:.4f}, "
            f"{row['absolute_ci_95_upper']:.4f}] | "
            f"{row['relative_degradation_percent']:.1f}% "
            f"[{row['relative_ci_95_lower']:.1f}%, "
            f"{row['relative_ci_95_upper']:.1f}%] |"
        )
    lines.extend(
        [
            "",
            "## Rank Stability",
            "",
            "| Type | Context | Comparison | Spearman mean [range] | Pairwise reversal mean [range] |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for key, group in ranks.groupby(
        [
            "comparison_type",
            "context",
            "from_condition",
            "to_condition",
        ],
        sort=True,
    ):
        comparison_type, context, from_condition, to_condition = key
        correlations = group["spearman_rank_correlation"].to_numpy(
            dtype=float
        )
        reversals = group["pairwise_reversal_fraction"].to_numpy(dtype=float)
        lines.append(
            f"| {comparison_type} | {context} | {from_condition} to "
            f"{to_condition} | {np.nanmean(correlations):.3f} "
            f"[{np.nanmin(correlations):.3f}, "
            f"{np.nanmax(correlations):.3f}] | "
            f"{np.nanmean(reversals):.3f} "
            f"[{np.nanmin(reversals):.3f}, "
            f"{np.nanmax(reversals):.3f}] |"
        )
    lines.extend(
        [
            "",
            "## Training",
            "",
            "| Model | Parameters | Best epoch, range | Validation loss, mean (SD) |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for model, group in training.groupby("model", sort=True):
        losses = group["best_validation_loss"].to_numpy(dtype=float)
        lines.append(
            f"| {MODEL_LABELS[model]} | "
            f"{int(group['parameter_count'].iloc[0]):,} | "
            f"{int(group['best_epoch'].min())}-{int(group['best_epoch'].max())} | "
            f"{losses.mean():.4f} "
            f"({losses.std(ddof=1) if len(losses) > 1 else 0.0:.4f}) |"
        )
    lines.extend(
        [
            "",
            "Interpretation boundary: passive free-running forecasting only. "
            "The tables do not establish treatment effects, counterfactual "
            "validity, policy quality, clinical benefit, or deployment safety.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--ridge-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--models", default="grud,transformer,rssm")
    parser.add_argument(
        "--seeds", default="20260912,20260913,20260914,20260915,20260916"
    )
    parser.add_argument("--bootstrap-replicates", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260912)
    args = parser.parse_args()

    models = [value.strip() for value in args.models.split(",") if value.strip()]
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    unknown = sorted(set(models) - set(NEURAL_MODELS))
    if unknown:
        raise ValueError(f"Unknown neural models: {unknown}")
    runs, missing = neural_run_paths(args.result_root, models, seeds)
    completeness = {
        "status": "complete" if not missing else "incomplete",
        "expected_runs": len(models) * len(seeds),
        "complete_runs": len(runs),
        "missing": missing,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis-completeness.json").write_text(
        json.dumps(completeness, indent=2) + "\n", encoding="utf-8"
    )
    if missing:
        print(json.dumps(completeness, indent=2))
        return 1

    patient = load_patient_metrics(
        baseline_dir=args.baseline_dir,
        ridge_dir=args.ridge_dir,
        runs=runs,
    )
    recalibration_checks = verify_recalibration_invariants(patient)
    constraints = load_constraints(
        baseline_dir=args.baseline_dir,
        ridge_dir=args.ridge_dir,
        runs=runs,
    )
    training, calibration_scales = load_training_and_calibration(runs)
    seed_metrics = seed_patient_macro(patient)
    aggregate_metrics = aggregate_seeds(seed_metrics)
    aggregate_constraint_frame = aggregate_constraints(constraints)
    main = main_table(seed_metrics, aggregate_constraint_frame)
    calibration = calibration_table(seed_metrics)
    cross_site = cross_site_table(seed_metrics)
    ranks = rank_stability(seed_metrics, seeds)
    rollout_areas = rollout_area_table(seed_metrics)
    support_counts = (
        patient.groupby(
            [
                "evaluation",
                "split",
                "model",
                "seed",
                "horizon_hours",
            ],
            sort=True,
        )
        .agg(
            patients=("patient_id", "nunique"),
            observed_targets=("observed_targets", "sum"),
        )
        .reset_index()
    )

    rng = np.random.default_rng(args.bootstrap_seed)
    contrast_rows = []
    for split in ("internal_test", "external_test"):
        for model_a, model_b in PRIMARY_PAIRS:
            contrast_rows.append(
                paired_bootstrap_contrast(
                    patient,
                    model_a=model_a,
                    model_b=model_b,
                    split=split,
                    horizon=12,
                    metric="patient_nmae",
                    seeds=seeds,
                    replicates=args.bootstrap_replicates,
                    rng=rng,
                )
            )
    contrasts = pd.DataFrame(contrast_rows)
    cross_site_inference = pd.DataFrame(
        [
            independent_cross_site_bootstrap(
                patient,
                model=model,
                horizon=12,
                seeds=seeds,
                replicates=args.bootstrap_replicates,
                rng=rng,
            )
            for model in MODEL_LABELS
        ]
    )
    pilot_seed = seeds[0]
    nonpilot_seed_metrics = seed_metrics[
        (seed_metrics["seed"] == -1)
        | (seed_metrics["seed"] != pilot_seed)
    ]
    nonpilot_constraints = constraints[
        (constraints["seed"] == -1)
        | (constraints["seed"] != pilot_seed)
    ]
    pilot_exclusion_main = main_table(
        nonpilot_seed_metrics,
        aggregate_constraints(nonpilot_constraints),
    )
    pilot_exclusion_calibration = calibration_table(nonpilot_seed_metrics)

    write_csv(args.output_dir / "seed-patient-macro.csv", seed_metrics)
    write_csv(
        args.output_dir / "recalibration-invariant-checks.csv",
        pd.DataFrame(recalibration_checks),
    )
    write_csv(args.output_dir / "aggregate-patient-macro.csv", aggregate_metrics)
    write_csv(args.output_dir / "seed-constraints.csv", constraints)
    write_csv(
        args.output_dir / "aggregate-constraints.csv",
        aggregate_constraint_frame,
    )
    write_csv(args.output_dir / "training-runs.csv", training)
    write_csv(args.output_dir / "calibration-scales.csv", calibration_scales)
    write_csv(args.output_dir / "main-external-table.csv", main)
    write_csv(args.output_dir / "external-calibration-table.csv", calibration)
    write_csv(args.output_dir / "cross-site-table.csv", cross_site)
    write_csv(
        args.output_dir / "cross-site-nmae-bootstrap.csv",
        cross_site_inference,
    )
    write_csv(args.output_dir / "rank-stability.csv", ranks)
    write_csv(args.output_dir / "rollout-area.csv", rollout_areas)
    write_csv(args.output_dir / "support-counts.csv", support_counts)
    write_csv(args.output_dir / "paired-12h-nmae-contrasts.csv", contrasts)
    write_csv(
        args.output_dir / "pilot-seed-exclusion-main-table.csv",
        pilot_exclusion_main,
    )
    write_csv(
        args.output_dir / "pilot-seed-exclusion-calibration-table.csv",
        pilot_exclusion_calibration,
    )
    (args.output_dir / "publication-summary.md").write_text(
        build_report(
            main=main,
            calibration=calibration,
            contrasts=contrasts,
            cross_site_inference=cross_site_inference,
            ranks=ranks,
            recalibration_checks=recalibration_checks,
            training=training,
            seeds=seeds,
        ),
        encoding="utf-8",
    )
    summary = {
        **completeness,
        "bootstrap_replicates": args.bootstrap_replicates,
        "bootstrap_seed": args.bootstrap_seed,
        "outputs": sorted(
            path.name for path in args.output_dir.iterdir() if path.is_file()
        ),
        "interpretation_boundary": (
            "Passive free-running forecasting only; no treatment-effect, "
            "counterfactual, policy, clinical-benefit, or deployment claim."
        ),
    }
    (args.output_dir / "analysis-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
