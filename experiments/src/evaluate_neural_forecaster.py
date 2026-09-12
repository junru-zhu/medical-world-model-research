#!/usr/bin/env python3
"""Evaluate probabilistic neural forecasters under free-running rollout."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import Tensor, nn

from neural_models import (
    CausalTransformerProbabilistic,
    GRUDProbabilistic,
    RecurrentStateSpaceModel,
    build_model,
)
from train_neural_forecaster import PreparedSplit, select_device, set_seed


RANDOM_STREAM_POLICY = "split-specific-v1"
CONSTRAINT_POLICY = "rollout-state-and-emitted-v1"
SPLIT_SEED_OFFSETS = {
    "train": 10_000,
    "validation": 20_000,
    "internal_test": 30_000,
    "external_calibration": 40_000,
    "external_test": 50_000,
}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_cases(
    split: PreparedSplit,
    *,
    minimum_context: int,
    maximum_context: int,
    maximum_horizon: int,
    stride: int,
    maximum_patients: int,
    patient_indices: list[int] | None = None,
) -> dict[int, list[tuple[int, int]]]:
    grouped: dict[int, list[tuple[int, int]]] = defaultdict(list)
    patient_count = len(split.patient_ids)
    if patient_indices is None:
        if maximum_patients:
            patient_count = min(patient_count, maximum_patients)
        patient_indices = list(range(patient_count))
    for patient_index in patient_indices:
        start, end = split.offsets[patient_index : patient_index + 2]
        length = int(end - start)
        last_anchor = length - maximum_horizon - 1
        if last_anchor < minimum_context - 1:
            continue
        for anchor in range(minimum_context - 1, last_anchor + 1, stride):
            context_length = min(anchor + 1, maximum_context)
            grouped[context_length].append((patient_index, anchor))
    return grouped


def context_batch(
    split: PreparedSplit,
    cases: list[tuple[int, int]],
    context_length: int,
) -> dict[str, Tensor]:
    arrays: dict[str, list[np.ndarray]] = {
        "values": [],
        "observed_values": [],
        "masks": [],
        "deltas": [],
        "time": [],
    }
    for patient_index, anchor in cases:
        patient = split.patient(patient_index)
        start = anchor - context_length + 1
        end = anchor + 1
        for key in arrays:
            arrays[key].append(patient[key][start:end])
    return {
        key: torch.from_numpy(np.stack(value)).float()
        for key, value in arrays.items()
    }


def empirical_crps(samples: Tensor, target: Tensor) -> Tensor:
    """CRPS for empirical samples, shape [batch, samples, variables]."""
    sample_count = samples.shape[1]
    first = torch.mean(torch.abs(samples - target.unsqueeze(1)), dim=1)
    ordered = torch.sort(samples, dim=1).values
    coefficients = (
        2.0 * torch.arange(1, sample_count + 1, device=samples.device)
        - sample_count
        - 1.0
    ).view(1, sample_count, 1)
    pairwise_expectation = (
        2.0
        * torch.sum(coefficients * ordered, dim=1)
        / float(sample_count * sample_count)
    )
    return first - 0.5 * pairwise_expectation


def rollout_grud(
    model: GRUDProbabilistic,
    context: dict[str, Tensor],
    *,
    horizons: list[int],
    samples: int,
    delta_step: float,
    time_step: float,
) -> tuple[dict[int, Tensor], dict[int, Tensor], dict[int, Tensor]]:
    batch_size, context_length, _ = context["values"].shape
    hidden = model.initial_state(batch_size, context["values"].device)
    for index in range(context_length - 1):
        _, hidden = model.step(
            context["values"][:, index],
            context["masks"][:, index],
            context["deltas"][:, index],
            context["time"][:, index],
            hidden,
        )
    current_values = context["values"][:, -1]
    current_masks = context["masks"][:, -1]
    current_deltas = context["deltas"][:, -1]
    current_time = context["time"][:, -1]
    hidden = hidden.repeat_interleave(samples, dim=0)
    current_values = current_values.repeat_interleave(samples, dim=0)
    current_masks = current_masks.repeat_interleave(samples, dim=0)
    current_deltas = current_deltas.repeat_interleave(samples, dim=0)
    current_time = current_time.repeat_interleave(samples, dim=0)
    value_outputs: dict[int, Tensor] = {}
    mask_outputs: dict[int, Tensor] = {}
    state_outputs: dict[int, Tensor] = {}
    for step in range(1, max(horizons) + 1):
        output, hidden = model.step(
            current_values,
            current_masks,
            current_deltas,
            current_time,
            hidden,
        )
        scale = torch.exp(output.log_scale)
        generated_values = output.mean + torch.randn_like(output.mean) * scale
        mask_probability = torch.sigmoid(output.mask_logits)
        generated_masks = torch.bernoulli(mask_probability)
        next_values = torch.where(
            generated_masks.bool(), generated_values, current_values
        )
        next_deltas = torch.where(
            generated_masks.bool(),
            torch.zeros_like(current_deltas),
            torch.clamp(current_deltas + delta_step, max=1.0),
        )
        if step in horizons:
            value_outputs[step] = generated_values.view(
                batch_size, samples, -1
            )
            mask_outputs[step] = mask_probability.view(
                batch_size, samples, -1
            )
            state_outputs[step] = next_values.view(
                batch_size, samples, -1
            )
        current_values = next_values
        current_deltas = next_deltas
        current_masks = generated_masks
        current_time = torch.clamp(current_time + time_step, max=1.0)
    return value_outputs, mask_outputs, state_outputs


def rollout_transformer(
    model: CausalTransformerProbabilistic,
    context: dict[str, Tensor],
    *,
    horizons: list[int],
    samples: int,
    delta_step: float,
    time_step: float,
) -> tuple[dict[int, Tensor], dict[int, Tensor], dict[int, Tensor]]:
    batch_size, context_length, _ = context["values"].shape
    output, caches = model.initialize_cache(
        context["values"],
        context["masks"],
        context["deltas"],
        context["time"],
    )
    mean = output.mean[:, -1].repeat_interleave(samples, dim=0)
    scale = torch.exp(output.log_scale[:, -1]).repeat_interleave(
        samples, dim=0
    )
    mask_probability = torch.sigmoid(
        output.mask_logits[:, -1]
    ).repeat_interleave(samples, dim=0)
    caches = [
        cache.repeat_interleave(samples, dim=0) for cache in caches
    ]
    previous_values = context["values"][:, -1].repeat_interleave(
        samples, dim=0
    )
    previous_deltas = context["deltas"][:, -1].repeat_interleave(
        samples, dim=0
    )
    previous_time = context["time"][:, -1].repeat_interleave(samples, dim=0)
    value_outputs: dict[int, Tensor] = {}
    mask_outputs: dict[int, Tensor] = {}
    state_outputs: dict[int, Tensor] = {}
    for step in range(1, max(horizons) + 1):
        generated_values = mean + torch.randn_like(mean) * scale
        generated_masks = torch.bernoulli(mask_probability)
        next_values = torch.where(
            generated_masks.bool(), generated_values, previous_values
        )
        next_deltas = torch.where(
            generated_masks.bool(),
            torch.zeros_like(previous_deltas),
            torch.clamp(previous_deltas + delta_step, max=1.0),
        )
        next_time = torch.clamp(previous_time + time_step, max=1.0)
        if step in horizons:
            value_outputs[step] = generated_values.view(
                batch_size, samples, -1
            )
            mask_outputs[step] = mask_probability.view(
                batch_size, samples, -1
            )
            state_outputs[step] = next_values.view(
                batch_size, samples, -1
            )
        if step < max(horizons):
            output, caches = model.cached_step(
                next_values,
                generated_masks,
                next_deltas,
                next_time,
                position_index=context_length + step - 1,
                caches=caches,
            )
            mean = output.mean[:, 0]
            scale = torch.exp(output.log_scale[:, 0])
            mask_probability = torch.sigmoid(output.mask_logits[:, 0])
            previous_values = next_values
            previous_deltas = next_deltas
            previous_time = next_time
    return value_outputs, mask_outputs, state_outputs


def rollout_rssm(
    model: RecurrentStateSpaceModel,
    context: dict[str, Tensor],
    *,
    horizons: list[int],
    samples: int,
    delta_step: float,
    time_step: float,
) -> tuple[dict[int, Tensor], dict[int, Tensor], dict[int, Tensor]]:
    batch_size, context_length, _ = context["values"].shape
    hidden, latent = model.initial_state(
        batch_size, context["values"].device
    )
    for index in range(context_length - 1):
        hidden, _, _ = model.transition_step(
            context["values"][:, index],
            context["masks"][:, index],
            context["deltas"][:, index],
            context["time"][:, index],
            hidden,
            latent,
        )
        posterior_parameters = model.posterior(
            torch.cat(
                [
                    hidden,
                    context["observed_values"][:, index + 1],
                    context["masks"][:, index + 1],
                ],
                dim=-1,
            )
        )
        latent, _ = model.distribution(posterior_parameters)
    current_values = context["values"][:, -1].repeat_interleave(samples, dim=0)
    current_masks = context["masks"][:, -1].repeat_interleave(samples, dim=0)
    current_deltas = context["deltas"][:, -1].repeat_interleave(samples, dim=0)
    current_time = context["time"][:, -1].repeat_interleave(samples, dim=0)
    hidden = hidden.repeat_interleave(samples, dim=0)
    latent = latent.repeat_interleave(samples, dim=0)
    value_outputs: dict[int, Tensor] = {}
    mask_outputs: dict[int, Tensor] = {}
    state_outputs: dict[int, Tensor] = {}
    for step in range(1, max(horizons) + 1):
        hidden, prior_mean, prior_log_scale = model.transition_step(
            current_values,
            current_masks,
            current_deltas,
            current_time,
            hidden,
            latent,
        )
        latent = prior_mean + torch.randn_like(prior_mean) * torch.exp(
            prior_log_scale
        )
        output = model.decode(hidden, latent)
        scale = torch.exp(output.log_scale)
        generated_values = output.mean + torch.randn_like(output.mean) * scale
        mask_probability = torch.sigmoid(output.mask_logits)
        generated_masks = torch.bernoulli(mask_probability)
        next_values = torch.where(
            generated_masks.bool(), generated_values, current_values
        )
        next_deltas = torch.where(
            generated_masks.bool(),
            torch.zeros_like(current_deltas),
            torch.clamp(current_deltas + delta_step, max=1.0),
        )
        if step in horizons:
            value_outputs[step] = generated_values.view(
                batch_size, samples, -1
            )
            mask_outputs[step] = mask_probability.view(
                batch_size, samples, -1
            )
            state_outputs[step] = next_values.view(
                batch_size, samples, -1
            )
        current_values = next_values
        current_deltas = next_deltas
        current_masks = generated_masks
        current_time = torch.clamp(current_time + time_step, max=1.0)
    return value_outputs, mask_outputs, state_outputs


def rollout(
    model: nn.Module,
    context: dict[str, Tensor],
    **kwargs: Any,
) -> tuple[dict[int, Tensor], dict[int, Tensor], dict[int, Tensor]]:
    if isinstance(model, GRUDProbabilistic):
        return rollout_grud(model, context, **kwargs)
    if isinstance(model, CausalTransformerProbabilistic):
        return rollout_transformer(model, context, **kwargs)
    if isinstance(model, RecurrentStateSpaceModel):
        return rollout_rssm(model, context, **kwargs)
    raise TypeError(type(model))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--splits", default="internal_test,external_test")
    parser.add_argument("--horizons", default="1,3,6,12,24")
    parser.add_argument("--minimum-context", type=int, default=12)
    parser.add_argument("--maximum-context", type=int, default=72)
    parser.add_argument("--stride", type=int, default=6)
    parser.add_argument("--trajectory-samples", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=20260912)
    parser.add_argument("--device", default="auto")
    parser.add_argument(
        "--spread-calibration",
        type=Path,
        help=(
            "Optional horizon-wise variance-scaling artifact fitted on a "
            "separate calibration split."
        ),
    )
    parser.add_argument(
        "--fit-spread-calibration-output",
        type=Path,
        help=(
            "Fit horizon-wise Gaussian-NLL variance scaling on the evaluated "
            "split and write the frozen artifact here."
        ),
    )
    parser.add_argument(
        "--maximum-patients",
        type=int,
        default=0,
        help="Nonzero is a smoke-only limit and cannot support paper claims.",
    )
    parser.add_argument(
        "--sensitivity-patient-sample",
        type=int,
        default=0,
        help=(
            "Deterministically sample this many patients per split for a "
            "numerical-sensitivity analysis."
        ),
    )
    parser.add_argument(
        "--sensitivity-sample-seed",
        type=int,
        default=20260912,
    )
    args = parser.parse_args()
    if args.spread_calibration and args.fit_spread_calibration_output:
        raise ValueError(
            "Cannot apply and fit spread calibration in the same run."
        )
    if args.maximum_patients and args.sensitivity_patient_sample:
        raise ValueError(
            "Cannot combine smoke-only and sensitivity patient limits."
        )
    if (
        args.sensitivity_patient_sample
        and args.fit_spread_calibration_output
    ):
        raise ValueError(
            "Spread calibration cannot be fitted on a sensitivity subset."
        )

    device = select_device(args.device)
    set_seed(args.seed)
    checkpoint = torch.load(
        args.checkpoint, map_location="cpu", weights_only=False
    )
    configuration = checkpoint["configuration"]
    variables = len(checkpoint["selected_variables"])
    model = build_model(
        configuration["model"],
        variables,
        hidden_size=configuration["hidden_size"],
        latent_size=configuration["latent_size"],
        transformer_layers=configuration["transformer_layers"],
        transformer_heads=configuration["transformer_heads"],
        dropout=configuration["dropout"],
        maximum_length=(
            configuration["maximum_sequence"]
            + configuration.get("maximum_rollout_horizon", 24)
        ),
    )
    model.load_state_dict(checkpoint["model_state"])
    model.to(device)
    model.eval()
    statistics = np.load(args.data_dir / "statistics.npz", allow_pickle=False)
    medians = torch.from_numpy(statistics["medians"]).float().to(device)
    iqr = torch.from_numpy(statistics["iqr"]).float().to(device)
    selected_names = statistics["selected_names"].astype(str).tolist()
    if selected_names != checkpoint["selected_variables"]:
        raise ValueError("Checkpoint and prepared-data variables differ")
    name_to_index = {name: index for index, name in enumerate(selected_names)}
    horizons = sorted(
        {int(value) for value in args.horizons.split(",") if value}
    )
    split_names = [value for value in args.splits.split(",") if value]
    model_name = configuration["model"]
    spread_scales: dict[int, float] = {}
    spread_calibration_metadata: dict[str, Any] | None = None
    if args.spread_calibration:
        spread_calibration_metadata = json.loads(
            args.spread_calibration.read_text(encoding="utf-8")
        )
        if spread_calibration_metadata["model"] != model_name:
            raise ValueError(
                "Spread-calibration model does not match checkpoint."
            )
        if int(spread_calibration_metadata["seed"]) != args.seed:
            raise ValueError(
                "Spread-calibration seed does not match evaluation seed."
            )
        if (
            Path(spread_calibration_metadata["checkpoint"]).resolve()
            != args.checkpoint.resolve()
        ):
            raise ValueError(
                "Spread-calibration checkpoint does not match evaluation "
                "checkpoint."
            )
        if spread_calibration_metadata["fit_split"] != "external_calibration":
            raise ValueError(
                "Spread calibration was not fitted on external_calibration."
            )
        if (
            spread_calibration_metadata.get("random_stream_policy")
            != RANDOM_STREAM_POLICY
        ):
            raise ValueError(
                "Spread calibration uses a stale random-stream policy."
            )
        if (
            int(spread_calibration_metadata["trajectory_samples"])
            != args.trajectory_samples
        ):
            raise ValueError(
                "Spread-calibration trajectory count does not match "
                "evaluation."
            )
        if (
            int(spread_calibration_metadata["evaluation_batch_size"])
            != args.batch_size
        ):
            raise ValueError(
                "Spread-calibration evaluation batch does not match."
            )
        spread_scales = {
            int(horizon): float(scale)
            for horizon, scale in spread_calibration_metadata[
                "horizon_scales"
            ].items()
        }
        missing_scales = sorted(set(horizons) - set(spread_scales))
        if missing_scales:
            raise ValueError(
                f"Spread calibration is missing horizons: {missing_scales}"
            )
    if args.fit_spread_calibration_output and len(split_names) != 1:
        raise ValueError(
            "Spread calibration must be fitted on exactly one split."
        )
    spread_fit_accumulators: dict[int, list[float]] = {
        horizon: [0.0, 0.0] for horizon in horizons
    }
    patient_accumulators: dict[
        tuple[str, str, int], dict[str, float]
    ] = defaultdict(
        lambda: {
            "absolute_error": 0.0,
            "observed": 0.0,
            "crps": 0.0,
            "coverage": 0.0,
            "interval_width": 0.0,
            "nll": 0.0,
            "mask_brier": 0.0,
            "mask_count": 0.0,
        }
    )
    variable_accumulators: dict[
        tuple[str, int, int], dict[str, float]
    ] = defaultdict(
        lambda: {
            "absolute_error": 0.0,
            "observed": 0.0,
            "crps": 0.0,
            "coverage": 0.0,
            "interval_width": 0.0,
            "nll": 0.0,
        }
    )
    mask_accumulators: dict[tuple[str, int, int], list[float]] = defaultdict(
        lambda: [0.0, 0.0]
    )
    constraint_accumulators: dict[tuple[str, int, str], list[int]] = defaultdict(
        lambda: [0, 0]
    )
    case_counts: dict[str, int] = {}
    sampled_patient_hashes: dict[str, str] = {}
    sampled_patient_counts: dict[str, int] = {}

    with torch.inference_mode():
        for split_name in split_names:
            if split_name not in SPLIT_SEED_OFFSETS:
                raise ValueError(
                    f"No deterministic random-stream offset for {split_name}."
                )
            split_seed = args.seed + SPLIT_SEED_OFFSETS[split_name]
            set_seed(split_seed)
            split = PreparedSplit(args.data_dir / f"{split_name}.npz")
            patient_indices: list[int] | None = None
            if args.sensitivity_patient_sample:
                sample_count = min(
                    args.sensitivity_patient_sample, len(split.patient_ids)
                )
                sample_rng = np.random.default_rng(
                    args.sensitivity_sample_seed
                    + SPLIT_SEED_OFFSETS[split_name]
                )
                patient_indices = sorted(
                    sample_rng.choice(
                        len(split.patient_ids),
                        size=sample_count,
                        replace=False,
                    ).tolist()
                )
                sampled_ids = split.patient_ids[patient_indices].astype(str)
                sampled_patient_counts[split_name] = len(sampled_ids)
                sampled_patient_hashes[split_name] = hashlib.sha256(
                    "\n".join(sampled_ids).encode("utf-8")
                ).hexdigest()
            groups = build_cases(
                split,
                minimum_context=args.minimum_context,
                maximum_context=args.maximum_context,
                maximum_horizon=max(horizons),
                stride=args.stride,
                maximum_patients=args.maximum_patients,
                patient_indices=patient_indices,
            )
            case_counts[split_name] = sum(len(cases) for cases in groups.values())
            for context_length, cases in sorted(groups.items()):
                for start in range(0, len(cases), args.batch_size):
                    current_cases = cases[start : start + args.batch_size]
                    context = {
                        key: value.to(device)
                        for key, value in context_batch(
                            split, current_cases, context_length
                        ).items()
                    }
                    value_outputs, mask_outputs, state_outputs = rollout(
                        model,
                        context,
                        horizons=horizons,
                        samples=args.trajectory_samples,
                        delta_step=1.0 / 24.0,
                        time_step=1.0 / 72.0,
                    )
                    for horizon in horizons:
                        targets = []
                        target_masks = []
                        patient_ids = []
                        for patient_index, anchor in current_cases:
                            patient = split.patient(patient_index)
                            targets.append(
                                patient["observed_values"][anchor + horizon]
                            )
                            target_masks.append(patient["masks"][anchor + horizon])
                            patient_ids.append(split.patient_ids[patient_index])
                        target = torch.from_numpy(np.stack(targets)).float().to(device)
                        target_mask = (
                            torch.from_numpy(np.stack(target_masks))
                            .bool()
                            .to(device)
                        )
                        raw_samples_scaled = value_outputs[horizon]
                        mask_probability = mask_outputs[horizon].mean(dim=1)
                        raw_sample_mean = raw_samples_scaled.mean(dim=1)
                        raw_sample_std = raw_samples_scaled.std(
                            dim=1, unbiased=False
                        ).clamp_min(1e-4)
                        if args.fit_spread_calibration_output:
                            standardized_squared_error = (
                                (target - raw_sample_mean) / raw_sample_std
                            ).square()
                            observed_values = standardized_squared_error[
                                target_mask
                            ]
                            spread_fit_accumulators[horizon][0] += float(
                                observed_values.sum().cpu()
                            )
                            spread_fit_accumulators[horizon][1] += int(
                                observed_values.numel()
                            )
                        spread_scale = spread_scales.get(horizon, 1.0)
                        samples_scaled = raw_sample_mean.unsqueeze(1) + (
                            spread_scale
                            * (
                                raw_samples_scaled
                                - raw_sample_mean.unsqueeze(1)
                            )
                        )
                        sample_mean = samples_scaled.mean(dim=1)
                        sample_std = samples_scaled.std(
                            dim=1, unbiased=False
                        ).clamp_min(1e-4)
                        absolute_error = torch.abs(sample_mean - target)
                        crps = empirical_crps(samples_scaled, target)
                        lower = torch.quantile(samples_scaled, 0.05, dim=1)
                        upper = torch.quantile(samples_scaled, 0.95, dim=1)
                        coverage = (target >= lower) & (target <= upper)
                        interval_width = upper - lower
                        nll = (
                            0.5 * ((target - sample_mean) / sample_std).square()
                            + torch.log(sample_std)
                            + 0.5 * math.log(2.0 * math.pi)
                        )
                        mask_brier = (
                            mask_probability - target_mask.float()
                        ).square()

                        for batch_index, patient_id in enumerate(patient_ids):
                            observed = target_mask[batch_index]
                            accumulator = patient_accumulators[
                                (split_name, patient_id, horizon)
                            ]
                            accumulator["absolute_error"] += float(
                                absolute_error[batch_index][observed].sum().cpu()
                            )
                            accumulator["observed"] += int(observed.sum().cpu())
                            accumulator["crps"] += float(
                                crps[batch_index][observed].sum().cpu()
                            )
                            accumulator["coverage"] += int(
                                coverage[batch_index][observed].sum().cpu()
                            )
                            accumulator["interval_width"] += float(
                                interval_width[batch_index][observed].sum().cpu()
                            )
                            accumulator["nll"] += float(
                                nll[batch_index][observed].sum().cpu()
                            )
                            accumulator["mask_brier"] += float(
                                mask_brier[batch_index].sum().cpu()
                            )
                            accumulator["mask_count"] += variables

                        for variable_index in range(variables):
                            observed = target_mask[:, variable_index]
                            if observed.any():
                                accumulator = variable_accumulators[
                                    (split_name, horizon, variable_index)
                                ]
                                accumulator["absolute_error"] += float(
                                    absolute_error[observed, variable_index].sum().cpu()
                                )
                                accumulator["observed"] += int(observed.sum().cpu())
                                accumulator["crps"] += float(
                                    crps[observed, variable_index].sum().cpu()
                                )
                                accumulator["coverage"] += int(
                                    coverage[observed, variable_index].sum().cpu()
                                )
                                accumulator["interval_width"] += float(
                                    interval_width[observed, variable_index].sum().cpu()
                                )
                                accumulator["nll"] += float(
                                    nll[observed, variable_index].sum().cpu()
                                )
                            mask_values = mask_accumulators[
                                (split_name, horizon, variable_index)
                            ]
                            mask_values[0] += float(
                                mask_brier[:, variable_index].sum().cpu()
                            )
                            mask_values[1] += len(current_cases)

                        physical_state = (
                            state_outputs[horizon] * iqr.view(1, 1, -1)
                            + medians.view(1, 1, -1)
                        )
                        physical_emission = (
                            raw_samples_scaled * iqr.view(1, 1, -1)
                            + medians.view(1, 1, -1)
                        )
                        pressure = physical_state[
                            :,
                            :,
                            [
                                name_to_index["SBP"],
                                name_to_index["MAP"],
                                name_to_index["DBP"],
                            ],
                        ]
                        pressure_violations = (
                            (pressure[:, :, 0] < pressure[:, :, 1])
                            | (pressure[:, :, 1] < pressure[:, :, 2])
                        )
                        pressure_counter = constraint_accumulators[
                            (split_name, horizon, "pressure_order")
                        ]
                        pressure_counter[0] += int(pressure_violations.sum().cpu())
                        pressure_counter[1] += pressure_violations.numel()
                        emitted_pressure = physical_emission[
                            :,
                            :,
                            [
                                name_to_index["SBP"],
                                name_to_index["MAP"],
                                name_to_index["DBP"],
                            ],
                        ]
                        emitted_pressure_violations = (
                            (
                                emitted_pressure[:, :, 0]
                                < emitted_pressure[:, :, 1]
                            )
                            | (
                                emitted_pressure[:, :, 1]
                                < emitted_pressure[:, :, 2]
                            )
                        )
                        emitted_pressure_counter = constraint_accumulators[
                            (split_name, horizon, "emitted_pressure_order")
                        ]
                        emitted_pressure_counter[0] += int(
                            emitted_pressure_violations.sum().cpu()
                        )
                        emitted_pressure_counter[1] += (
                            emitted_pressure_violations.numel()
                        )
                        for variable, low, high in (
                            ("O2Sat", 0.0, 100.0),
                            ("SaO2", 0.0, 100.0),
                            ("FiO2", 0.0, 1.0),
                        ):
                            state_values = physical_state[
                                :, :, name_to_index[variable]
                            ]
                            violations = (
                                (state_values < low) | (state_values > high)
                            )
                            counter = constraint_accumulators[
                                (split_name, horizon, f"{variable}_bounds")
                            ]
                            counter[0] += int(violations.sum().cpu())
                            counter[1] += violations.numel()
                            emitted_values = physical_emission[
                                :, :, name_to_index[variable]
                            ]
                            emitted_violations = (
                                (emitted_values < low)
                                | (emitted_values > high)
                            )
                            emitted_counter = constraint_accumulators[
                                (
                                    split_name,
                                    horizon,
                                    f"emitted_{variable}_bounds",
                                )
                            ]
                            emitted_counter[0] += int(
                                emitted_violations.sum().cpu()
                            )
                            emitted_counter[1] += emitted_violations.numel()

    patient_rows: list[dict[str, Any]] = []
    for (split, patient_id, horizon), accumulator in sorted(
        patient_accumulators.items()
    ):
        if not accumulator["observed"]:
            continue
        patient_rows.append(
            {
                "patient_id": patient_id,
                "split": split,
                "model": model_name,
                "horizon_hours": horizon,
                "observed_targets": int(accumulator["observed"]),
                "patient_nmae": accumulator["absolute_error"]
                / accumulator["observed"],
                "patient_crps": accumulator["crps"] / accumulator["observed"],
                "coverage_90": accumulator["coverage"] / accumulator["observed"],
                "mean_interval_width_scaled": accumulator["interval_width"]
                / accumulator["observed"],
                "patient_nll": accumulator["nll"] / accumulator["observed"],
                "mask_brier": accumulator["mask_brier"]
                / accumulator["mask_count"],
            }
        )
    variable_rows: list[dict[str, Any]] = []
    for (split, horizon, variable_index), accumulator in sorted(
        variable_accumulators.items()
    ):
        observed = accumulator["observed"]
        variable_rows.append(
            {
                "split": split,
                "model": model_name,
                "horizon_hours": horizon,
                "variable": selected_names[variable_index],
                "observed_targets": int(observed),
                "nmae": accumulator["absolute_error"] / observed,
                "crps_scaled": accumulator["crps"] / observed,
                "coverage_90": accumulator["coverage"] / observed,
                "coverage_error_90": abs(
                    accumulator["coverage"] / observed - 0.9
                ),
                "mean_interval_width_scaled": accumulator["interval_width"]
                / observed,
                "nll_scaled": accumulator["nll"] / observed,
            }
        )
    mask_rows = [
        {
            "split": split,
            "model": model_name,
            "horizon_hours": horizon,
            "variable": selected_names[variable_index],
            "targets": int(values[1]),
            "brier": values[0] / values[1],
        }
        for (split, horizon, variable_index), values in sorted(
            mask_accumulators.items()
        )
    ]
    constraint_rows = [
        {
            "split": split,
            "model": model_name,
            "horizon_hours": horizon,
            "constraint": constraint,
            "violations": values[0],
            "generated_states": values[1],
            "violations_per_1000_states": 1000.0 * values[0] / values[1],
        }
        for (split, horizon, constraint), values in sorted(
            constraint_accumulators.items()
        )
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "patient-metrics.csv", patient_rows)
    write_csv(args.output_dir / "metrics-by-variable.csv", variable_rows)
    write_csv(args.output_dir / "mask-metrics.csv", mask_rows)
    write_csv(args.output_dir / "constraints.csv", constraint_rows)
    patient_macro: dict[str, dict[str, dict[str, float]]] = {}
    for split in split_names:
        patient_macro[split] = {}
        for horizon in horizons:
            rows = [
                row
                for row in patient_rows
                if row["split"] == split and row["horizon_hours"] == horizon
            ]
            patient_macro[split][str(horizon)] = {
                metric: float(np.mean([row[metric] for row in rows]))
                for metric in (
                    "patient_nmae",
                    "patient_crps",
                    "coverage_90",
                    "mean_interval_width_scaled",
                    "patient_nll",
                    "mask_brier",
                )
            }
    summary = {
        "status": (
            "smoke_only"
            if args.maximum_patients
            else (
                "sensitivity_only"
                if args.sensitivity_patient_sample
                else "complete"
            )
        ),
        "model": model_name,
        "checkpoint": str(args.checkpoint),
        "checkpoint_best_epoch": checkpoint["best_epoch"],
        "seed": args.seed,
        "splits": split_names,
        "horizons": horizons,
        "minimum_context": args.minimum_context,
        "maximum_context": args.maximum_context,
        "common_anchor_maximum_horizon": max(horizons),
        "anchor_stride": args.stride,
        "trajectory_samples": args.trajectory_samples,
        "evaluation_batch_size": args.batch_size,
        "random_stream_policy": RANDOM_STREAM_POLICY,
        "constraint_policy": CONSTRAINT_POLICY,
        "split_seeds": {
            split_name: args.seed + SPLIT_SEED_OFFSETS[split_name]
            for split_name in split_names
        },
        "spread_calibration": (
            {
                "artifact": str(args.spread_calibration),
                "method": spread_calibration_metadata["method"],
                "fit_split": spread_calibration_metadata["fit_split"],
                "horizon_scales": {
                    str(horizon): spread_scales[horizon]
                    for horizon in horizons
                },
                "scope": (
                    "Post-hoc marginal predictive-spread scaling; rollout "
                    "states, point forecasts, mask predictions, and raw "
                    "trajectory constraint counts are unchanged."
                ),
            }
            if args.spread_calibration
            else None
        ),
        "case_counts": case_counts,
        "patient_macro": patient_macro,
        "maximum_patients": args.maximum_patients,
        "sensitivity_patient_sample": args.sensitivity_patient_sample,
        "sensitivity_sample_seed": args.sensitivity_sample_seed,
        "sampled_patient_counts": sampled_patient_counts,
        "sampled_patient_hashes": sampled_patient_hashes,
        "interpretation_boundary": (
            "Free-running passive forecasting only; no treatment-effect, "
            "counterfactual, planning, or clinical-deployment claim."
        ),
        "nll_definition": (
            "Moment-matched Gaussian negative log score using the empirical "
            "trajectory-sample mean and standard deviation; not the exact "
            "likelihood of the rollout distribution."
        ),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if args.fit_spread_calibration_output:
        horizon_scales: dict[str, float] = {}
        observed_targets: dict[str, int] = {}
        for horizon, (standardized_sse, count) in sorted(
            spread_fit_accumulators.items()
        ):
            if not count:
                raise ValueError(
                    f"No observed targets for calibration horizon {horizon}."
                )
            horizon_scales[str(horizon)] = math.sqrt(
                standardized_sse / count
            )
            observed_targets[str(horizon)] = int(count)
        calibration_payload = {
            "status": (
                "smoke_only" if args.maximum_patients else "complete"
            ),
            "model": model_name,
            "checkpoint": str(args.checkpoint),
            "seed": args.seed,
            "random_stream_policy": RANDOM_STREAM_POLICY,
            "fit_split_seed": (
                args.seed + SPLIT_SEED_OFFSETS[split_names[0]]
            ),
            "method": (
                "Horizon-wise scalar variance scaling fitted by minimizing "
                "Gaussian negative log likelihood on observed targets."
            ),
            "fit_split": split_names[0],
            "trajectory_samples": args.trajectory_samples,
            "evaluation_batch_size": args.batch_size,
            "horizons": horizons,
            "minimum_context": args.minimum_context,
            "maximum_context": args.maximum_context,
            "common_anchor_maximum_horizon": max(horizons),
            "anchor_stride": args.stride,
            "horizon_scales": horizon_scales,
            "observed_targets": observed_targets,
            "maximum_patients": args.maximum_patients,
            "test_boundary": (
                "No external-test observations were used to fit this artifact."
            ),
        }
        args.fit_spread_calibration_output.parent.mkdir(
            parents=True, exist_ok=True
        )
        args.fit_spread_calibration_output.write_text(
            json.dumps(calibration_payload, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        summary["fitted_spread_calibration"] = calibration_payload
        (args.output_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
