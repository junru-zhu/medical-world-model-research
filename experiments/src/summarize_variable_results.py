#!/usr/bin/env python3
"""Summarize frozen external 12-hour variable-level errors."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


MODEL_LABELS = {
    "locf": "LOCF",
    "global_median": "Global median",
    "hourly_median": "Hourly median",
    "ridge_var": "Ridge VAR",
    "grud": "GRU-D-style",
    "transformer": "Masked Transformer",
    "rssm": "State-space model",
}
NEURAL_MODELS = ("grud", "transformer", "rssm")
DISPLAY_VARIABLES = (
    "HR",
    "O2Sat",
    "Temp",
    "SBP",
    "MAP",
    "DBP",
    "Resp",
    "BaseExcess",
    "HCO3",
    "FiO2",
    "pH",
    "PaCO2",
    "SaO2",
    "BUN",
    "Chloride",
    "Creatinine",
    "Glucose",
    "Magnesium",
    "Phosphate",
    "Potassium",
    "Hct",
    "Hgb",
    "WBC",
    "Platelets",
)
VARIABLE_UNITS = {
    "HR": "beats/min",
    "O2Sat": "%",
    "Temp": "degrees C",
    "SBP": "mm Hg",
    "MAP": "mm Hg",
    "DBP": "mm Hg",
    "Resp": "breaths/min",
    "BaseExcess": "mmol/L",
    "HCO3": "mmol/L",
    "FiO2": "fraction",
    "pH": "unitless",
    "PaCO2": "mm Hg",
    "SaO2": "%",
    "BUN": "mg/dL",
    "Chloride": "mmol/L",
    "Creatinine": "mg/dL",
    "Glucose": "mg/dL",
    "Magnesium": "mg/dL",
    "Phosphate": "mg/dL",
    "Potassium": "mmol/L",
    "Hct": "%",
    "Hgb": "g/dL",
    "WBC": "10^3/uL",
    "Platelets": "10^3/uL",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--baseline-dir", type=Path, required=True)
    parser.add_argument("--ridge-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--seeds",
        default="20260912,20260913,20260914,20260915,20260916",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seeds = tuple(int(value) for value in args.seeds.split(","))
    statistics = np.load(args.data_dir / "statistics.npz")
    iqr = dict(
        zip(
            statistics["selected_names"].tolist(),
            statistics["iqr"].astype(float).tolist(),
        )
    )

    frames: list[pd.DataFrame] = []
    for model in NEURAL_MODELS:
        for seed in seeds:
            path = (
                args.result_root
                / model
                / f"seed-{seed}"
                / "evaluation"
                / "metrics-by-variable.csv"
            )
            frame = pd.read_csv(path)
            frame = frame[
                (frame["split"] == "external_test")
                & (frame["horizon_hours"] == 12)
            ].copy()
            frame["seed"] = seed
            frame["mae_original"] = frame.apply(
                lambda row: float(row["nmae"]) * iqr[str(row["variable"])],
                axis=1,
            )
            frames.append(
                frame[
                    [
                        "model",
                        "seed",
                        "variable",
                        "observed_targets",
                        "nmae",
                        "mae_original",
                    ]
                ]
            )

    neural = pd.concat(frames, ignore_index=True)
    summary = (
        neural.groupby(["model", "variable"], as_index=False)
        .agg(
            observed_targets=("observed_targets", "first"),
            nmae_mean=("nmae", "mean"),
            nmae_seed_sd=("nmae", "std"),
            mae_original_mean=("mae_original", "mean"),
            mae_original_seed_sd=("mae_original", "std"),
        )
    )

    deterministic_frames: list[pd.DataFrame] = []
    for path in (
        args.baseline_dir / "metrics-by-variable.csv",
        args.ridge_dir / "metrics-by-variable.csv",
    ):
        frame = pd.read_csv(path)
        frame = frame[
            (frame["split"] == "external_test")
            & (frame["horizon_hours"] == 12)
        ].copy()
        frame = frame.rename(
            columns={
                "nmae": "nmae_mean",
                "mae": "mae_original_mean",
            }
        )
        frame["nmae_seed_sd"] = 0.0
        frame["mae_original_seed_sd"] = 0.0
        deterministic_frames.append(
            frame[
                [
                    "model",
                    "variable",
                    "observed_targets",
                    "nmae_mean",
                    "nmae_seed_sd",
                    "mae_original_mean",
                    "mae_original_seed_sd",
                ]
            ]
        )

    summary = pd.concat(
        [summary, *deterministic_frames],
        ignore_index=True,
    )
    summary["model_label"] = summary["model"].map(MODEL_LABELS)
    summary["unit"] = summary["variable"].map(VARIABLE_UNITS)
    summary = summary[
        [
            "model",
            "model_label",
            "variable",
            "unit",
            "observed_targets",
            "nmae_mean",
            "nmae_seed_sd",
            "mae_original_mean",
            "mae_original_seed_sd",
        ]
    ].sort_values(["variable", "model"])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(
        args.output_dir / "external-12h-variable-results.csv",
        index=False,
    )

    display = summary[
        summary["variable"].isin(DISPLAY_VARIABLES)
        & summary["model"].isin(("ridge_var", *NEURAL_MODELS))
    ].copy()
    lines = [
        "# External 12-hour variable-level error",
        "",
        "MAE is in the dataset's original units. Neural values are means across "
        "five seeds; parentheses are across-seed SDs.",
        "Variable-level values pool observed targets and are not an additive "
        "decomposition of the patient-macro primary outcome.",
        "",
        "| Variable | Unit | Targets | Ridge VAR | GRU-D-style | Masked Transformer | "
        "State-space model |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variable in DISPLAY_VARIABLES:
        group = display[display["variable"] == variable].set_index("model")
        cells = []
        for model in ("ridge_var", *NEURAL_MODELS):
            row = group.loc[model]
            if model == "ridge_var":
                cells.append(f"{row.mae_original_mean:.3f}")
            else:
                cells.append(
                    f"{row.mae_original_mean:.3f} "
                    f"({row.mae_original_seed_sd:.3f})"
                )
        lines.append(
            f"| {variable} | {VARIABLE_UNITS[variable]} | "
            f"{int(group.iloc[0].observed_targets):,} | "
            + " | ".join(cells)
            + " |"
        )
    (args.output_dir / "external-12h-variable-results.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {len(summary)} rows to "
        f"{args.output_dir / 'external-12h-variable-results.csv'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
