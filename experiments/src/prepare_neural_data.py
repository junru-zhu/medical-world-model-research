#!/usr/bin/env python3
"""Prepare leakage-safe patient arrays for probabilistic neural forecasters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from run_baselines import (
    DYNAMIC_COLUMNS,
    fit_statistics,
    locf_arrays,
    read_manifest,
    read_patient,
)


def compute_deltas(mask: np.ndarray, clip_hours: int) -> np.ndarray:
    """Return hours since last observation, clipped and scaled to [0, 1]."""
    deltas = np.zeros(mask.shape, dtype=np.float32)
    elapsed = np.full(mask.shape[1], clip_hours, dtype=np.float32)
    for index in range(mask.shape[0]):
        elapsed = np.where(mask[index], 0.0, np.minimum(elapsed + 1.0, clip_hours))
        deltas[index] = elapsed / float(clip_hours)
    return deltas


def prepare_split(
    *,
    data_root: Path,
    manifest: list[dict[str, str]],
    split: str,
    statistics: dict[str, Any],
    delta_clip_hours: int,
    time_scale_hours: int,
    output: Path,
) -> dict[str, Any]:
    selected_indices = np.flatnonzero(statistics["selected"])
    medians = statistics["medians"][selected_indices]
    iqr = statistics["iqr"][selected_indices]
    patients = [row for row in manifest if row["split"] == split]
    values_parts: list[np.ndarray] = []
    observed_parts: list[np.ndarray] = []
    mask_parts: list[np.ndarray] = []
    delta_parts: list[np.ndarray] = []
    time_parts: list[np.ndarray] = []
    offsets = [0]
    patient_ids: list[str] = []
    cohorts: list[str] = []

    for row in patients:
        raw_values, iculos = read_patient(data_root / row["relative_path"])
        raw_values = raw_values[:, selected_indices]
        mask = np.isfinite(raw_values)
        filled, _ = locf_arrays(raw_values, medians)
        scaled_filled = ((filled - medians) / iqr).astype(np.float32)
        scaled_observed = np.where(
            mask,
            (raw_values - medians) / iqr,
            0.0,
        ).astype(np.float32)
        values_parts.append(scaled_filled)
        observed_parts.append(scaled_observed)
        mask_parts.append(mask.astype(np.uint8))
        delta_parts.append(compute_deltas(mask, delta_clip_hours))
        time_parts.append(
            np.minimum(iculos.astype(np.float32), time_scale_hours)
            .reshape(-1, 1)
            / float(time_scale_hours)
        )
        offsets.append(offsets[-1] + len(raw_values))
        patient_ids.append(row["patient_id"])
        cohorts.append(row["cohort"])

    if not values_parts:
        raise ValueError(f"No patients found for split {split!r}")
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        output,
        values=np.concatenate(values_parts, axis=0),
        observed_values=np.concatenate(observed_parts, axis=0),
        masks=np.concatenate(mask_parts, axis=0),
        deltas=np.concatenate(delta_parts, axis=0),
        time=np.concatenate(time_parts, axis=0),
        offsets=np.asarray(offsets, dtype=np.int64),
        patient_ids=np.asarray(patient_ids),
        cohorts=np.asarray(cohorts),
        selected_indices=selected_indices.astype(np.int64),
        selected_names=np.asarray(
            [DYNAMIC_COLUMNS[index] for index in selected_indices]
        ),
    )
    return {
        "split": split,
        "patients": len(patients),
        "patient_hours": offsets[-1],
        "variables": len(selected_indices),
        "output": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--coverage-threshold", type=float, default=0.05)
    parser.add_argument("--hour-cap", type=int, default=72)
    parser.add_argument("--delta-clip-hours", type=int, default=24)
    parser.add_argument("--time-scale-hours", type=int, default=72)
    parser.add_argument(
        "--splits",
        default="train,validation,internal_test,external_calibration,external_test",
    )
    args = parser.parse_args()

    manifest = read_manifest(args.split_manifest)
    statistics = fit_statistics(
        args.data_root,
        manifest,
        args.coverage_threshold,
        args.hour_cap,
    )
    selected_indices = np.flatnonzero(statistics["selected"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    np.savez(
        args.output_dir / "statistics.npz",
        selected_indices=selected_indices.astype(np.int64),
        selected_names=np.asarray(
            [DYNAMIC_COLUMNS[index] for index in selected_indices]
        ),
        medians=statistics["medians"][selected_indices],
        iqr=statistics["iqr"][selected_indices],
        low=statistics["low"][selected_indices],
        high=statistics["high"][selected_indices],
        coverage=statistics["coverage"][selected_indices],
    )

    split_summaries = [
        prepare_split(
            data_root=args.data_root,
            manifest=manifest,
            split=split,
            statistics=statistics,
            delta_clip_hours=args.delta_clip_hours,
            time_scale_hours=args.time_scale_hours,
            output=args.output_dir / f"{split}.npz",
        )
        for split in [item.strip() for item in args.splits.split(",") if item.strip()]
    ]
    summary = {
        "dataset": "PhysioNet/Computing in Cardiology Challenge 2019 v1.0.0",
        "coverage_threshold": args.coverage_threshold,
        "delta_clip_hours": args.delta_clip_hours,
        "time_scale_hours": args.time_scale_hours,
        "selected_variables": [
            DYNAMIC_COLUMNS[index] for index in selected_indices
        ],
        "splits": split_summaries,
        "leakage_boundary": (
            "Variable selection, medians, IQRs, clipping statistics, and all "
            "normalization parameters were fit on cohort-A training patients only."
        ),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
