#!/usr/bin/env python3
"""Validate prepared neural arrays, patient boundaries, and split isolation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


REQUIRED_ARRAYS = {
    "values",
    "observed_values",
    "masks",
    "deltas",
    "time",
    "offsets",
    "patient_ids",
    "cohorts",
    "selected_indices",
    "selected_names",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary = json.loads((args.data_dir / "summary.json").read_text())
    errors: list[str] = []
    split_results: list[dict[str, object]] = []
    all_patient_ids: set[str] = set()
    expected_names = summary["selected_variables"]

    for split_summary in summary["splits"]:
        split = split_summary["split"]
        path = args.data_dir / f"{split}.npz"
        if not path.is_file():
            errors.append(f"{split}: missing {path}")
            continue
        with np.load(path, allow_pickle=False) as data:
            missing = sorted(REQUIRED_ARRAYS - set(data.files))
            if missing:
                errors.append(f"{split}: missing arrays {missing}")
                continue
            values = data["values"]
            observed = data["observed_values"]
            masks = data["masks"]
            deltas = data["deltas"]
            time = data["time"]
            offsets = data["offsets"]
            patient_ids = data["patient_ids"].astype(str)
            selected_names = data["selected_names"].astype(str).tolist()

            if selected_names != expected_names:
                errors.append(f"{split}: selected variable order mismatch")
            if not (
                values.shape == observed.shape == masks.shape == deltas.shape
            ):
                errors.append(f"{split}: dynamic array shapes differ")
            if time.shape != (len(values), 1):
                errors.append(f"{split}: invalid time shape {time.shape}")
            if len(offsets) != len(patient_ids) + 1:
                errors.append(f"{split}: offsets and patient IDs differ")
            if len(offsets) and (offsets[0] != 0 or offsets[-1] != len(values)):
                errors.append(f"{split}: offsets do not span all rows")
            if len(offsets) > 1 and np.any(np.diff(offsets) <= 0):
                errors.append(f"{split}: nonpositive patient sequence length")
            if len(patient_ids) != len(set(patient_ids)):
                errors.append(f"{split}: duplicate patient IDs within split")
            overlap = all_patient_ids.intersection(patient_ids)
            if overlap:
                errors.append(
                    f"{split}: {len(overlap)} patient IDs overlap earlier splits"
                )
            all_patient_ids.update(patient_ids)
            for label, array in (
                ("values", values),
                ("observed_values", observed),
                ("deltas", deltas),
                ("time", time),
            ):
                if not np.all(np.isfinite(array)):
                    errors.append(f"{split}: nonfinite {label}")
            if not np.all((masks == 0) | (masks == 1)):
                errors.append(f"{split}: masks are not binary")
            if np.any((deltas < 0) | (deltas > 1)):
                errors.append(f"{split}: deltas outside [0, 1]")
            if np.any((time < 0) | (time > 1)):
                errors.append(f"{split}: time outside [0, 1]")
            if np.any(observed[masks == 0] != 0):
                errors.append(f"{split}: unobserved target values are nonzero")
            if len(patient_ids) != int(split_summary["patients"]):
                errors.append(f"{split}: patient count differs from summary")
            if len(values) != int(split_summary["patient_hours"]):
                errors.append(f"{split}: patient-hour count differs from summary")

            split_results.append(
                {
                    "split": split,
                    "patients": len(patient_ids),
                    "patient_hours": len(values),
                    "variables": values.shape[1],
                    "observed_fraction": float(np.mean(masks)),
                    "minimum_sequence_hours": int(np.min(np.diff(offsets))),
                    "maximum_sequence_hours": int(np.max(np.diff(offsets))),
                }
            )

    result = {
        "status": "pass" if not errors else "fail",
        "unique_patients": len(all_patient_ids),
        "selected_variables": expected_names,
        "splits": split_results,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
