#!/usr/bin/env python3
"""Summarize patient-level baseline metrics with deterministic bootstrap intervals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def bootstrap_mean_interval(
    values: np.ndarray,
    *,
    replicates: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    if values.size == 0:
        raise ValueError("Cannot bootstrap an empty sample.")
    if values.size == 1:
        return float(values[0]), float(values[0])

    means = np.empty(replicates, dtype=np.float64)
    chunk_size = max(1, min(replicates, 256))
    for start in range(0, replicates, chunk_size):
        stop = min(start + chunk_size, replicates)
        indices = rng.integers(
            0,
            values.size,
            size=(stop - start, values.size),
            endpoint=False,
        )
        means[start:stop] = values[indices].mean(axis=1)
    lower, upper = np.quantile(means, [0.025, 0.975])
    return float(lower), float(upper)


def summarize(
    frame: pd.DataFrame,
    *,
    replicates: int,
    seed: int,
) -> pd.DataFrame:
    required = {
        "patient_id",
        "cohort",
        "split",
        "model",
        "horizon_hours",
        "patient_nmae",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    rows: list[dict[str, float | int | str]] = []
    groups = frame.groupby(
        ["split", "model", "horizon_hours"], sort=True, observed=True
    )
    for group_index, ((split, model, horizon), group) in enumerate(groups):
        if group.duplicated(["cohort", "patient_id"]).any():
            raise ValueError(
                f"Duplicate patient rows for {split}/{model}/{horizon}."
            )
        values = group["patient_nmae"].to_numpy(dtype=np.float64)
        rng = np.random.default_rng(seed + group_index)
        lower, upper = bootstrap_mean_interval(
            values,
            replicates=replicates,
            rng=rng,
        )
        rows.append(
            {
                "split": str(split),
                "model": str(model),
                "horizon_hours": int(horizon),
                "patients": int(values.size),
                "mean_patient_nmae": float(values.mean()),
                "median_patient_nmae": float(np.median(values)),
                "bootstrap_95_ci_lower": lower,
                "bootstrap_95_ci_upper": upper,
            }
        )
    return pd.DataFrame(rows)


def cross_site(summary: pd.DataFrame) -> pd.DataFrame:
    pivot = summary.pivot(
        index=["model", "horizon_hours"],
        columns="split",
        values="mean_patient_nmae",
    ).reset_index()
    required = {"internal_test", "external_test"}
    if not required.issubset(pivot.columns):
        return pd.DataFrame(
            columns=[
                "model",
                "horizon_hours",
                "internal_test_mean_patient_nmae",
                "external_test_mean_patient_nmae",
                "relative_degradation",
            ]
        )
    output = pivot[
        ["model", "horizon_hours", "internal_test", "external_test"]
    ].copy()
    output["relative_degradation"] = (
        output["external_test"] - output["internal_test"]
    ) / output["internal_test"]
    return output.rename(
        columns={
            "internal_test": "internal_test_mean_patient_nmae",
            "external_test": "external_test_mean_patient_nmae",
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patient-metrics", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-replicates", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args()

    if args.bootstrap_replicates < 1:
        raise ValueError("--bootstrap-replicates must be positive.")

    frame = pd.read_csv(args.patient_metrics)
    summary = summarize(
        frame,
        replicates=args.bootstrap_replicates,
        seed=args.seed,
    )
    cross_site_summary = cross_site(summary)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "patient-nmae-summary.csv"
    cross_site_path = args.output_dir / "cross-site-summary.csv"
    metadata_path = args.output_dir / "summary-metadata.json"
    summary.to_csv(summary_path, index=False)
    cross_site_summary.to_csv(cross_site_path, index=False)
    metadata_path.write_text(
        json.dumps(
            {
                "bootstrap_replicates": args.bootstrap_replicates,
                "bootstrap_seed": args.seed,
                "interval": "percentile 95% patient-level bootstrap interval",
                "aggregation": "mean of each patient's observed-target NMAE",
                "source": str(args.patient_metrics),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "summary_rows": len(summary),
                "cross_site_rows": len(cross_site_summary),
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
