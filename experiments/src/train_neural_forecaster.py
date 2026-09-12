#!/usr/bin/env python3
"""Train probabilistic GRU-D, Transformer, or recurrent state-space models."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torch.utils.data import DataLoader, Dataset

from neural_models import ForecastOutput, RecurrentStateSpaceModel, build_model


@dataclass
class TrainingConfiguration:
    model: str
    seed: int
    epochs: int
    batch_size: int
    maximum_sequence: int
    maximum_rollout_horizon: int
    hidden_size: int
    latent_size: int
    transformer_layers: int
    transformer_heads: int
    dropout: float
    learning_rate: float
    weight_decay: float
    mask_loss_weight: float
    kl_weight: float
    gradient_clip: float
    patience: int
    device: str


class PreparedSplit:
    def __init__(self, path: Path) -> None:
        data = np.load(path, allow_pickle=False)
        self.values = data["values"]
        self.observed_values = data["observed_values"]
        self.masks = data["masks"]
        self.deltas = data["deltas"]
        self.time = data["time"]
        self.offsets = data["offsets"]
        self.patient_ids = data["patient_ids"].astype(str)
        self.selected_names = data["selected_names"].astype(str).tolist()

    def patient(self, index: int) -> dict[str, np.ndarray]:
        start, end = self.offsets[index : index + 2]
        return {
            "values": self.values[start:end],
            "observed_values": self.observed_values[start:end],
            "masks": self.masks[start:end].astype(np.float32),
            "deltas": self.deltas[start:end],
            "time": self.time[start:end],
        }


class RandomPatientWindows(Dataset[dict[str, np.ndarray]]):
    def __init__(
        self,
        split: PreparedSplit,
        maximum_sequence: int,
        seed: int,
    ) -> None:
        self.split = split
        self.maximum_sequence = maximum_sequence
        self.seed = seed
        self.epoch = 0
        lengths = np.diff(split.offsets)
        self.patient_indices = np.flatnonzero(lengths >= 2).tolist()

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch

    def __len__(self) -> int:
        return len(self.patient_indices)

    def __getitem__(self, item: int) -> dict[str, np.ndarray]:
        patient_index = self.patient_indices[item]
        patient = self.split.patient(patient_index)
        length = len(patient["values"])
        window_rows = min(length, self.maximum_sequence + 1)
        if length == window_rows:
            start = 0
        else:
            generator = np.random.default_rng(
                self.seed + self.epoch * 1_000_003 + patient_index
            )
            start = int(generator.integers(0, length - window_rows + 1))
        end = start + window_rows
        return {key: value[start:end] for key, value in patient.items()}


class ExhaustivePatientWindows(Dataset[dict[str, np.ndarray]]):
    def __init__(self, split: PreparedSplit, maximum_sequence: int) -> None:
        self.split = split
        self.maximum_sequence = maximum_sequence
        self.windows: list[tuple[int, int, int]] = []
        for patient_index, (start, end) in enumerate(
            zip(split.offsets[:-1], split.offsets[1:], strict=True)
        ):
            length = int(end - start)
            if length < 2:
                continue
            for window_start in range(0, length - 1, maximum_sequence):
                window_end = min(length, window_start + maximum_sequence + 1)
                if window_end - window_start >= 2:
                    self.windows.append(
                        (patient_index, window_start, window_end)
                    )

    def __len__(self) -> int:
        return len(self.windows)

    def __getitem__(self, item: int) -> dict[str, np.ndarray]:
        patient_index, start, end = self.windows[item]
        patient = self.split.patient(patient_index)
        return {key: value[start:end] for key, value in patient.items()}


def collate_windows(rows: list[dict[str, np.ndarray]]) -> dict[str, Tensor]:
    lengths = torch.tensor([len(row["values"]) - 1 for row in rows])
    maximum = int(lengths.max())
    variables = rows[0]["values"].shape[1]

    def allocate(last_dimension: int) -> Tensor:
        return torch.zeros(len(rows), maximum, last_dimension, dtype=torch.float32)

    values = allocate(variables)
    masks = allocate(variables)
    deltas = allocate(variables)
    time = allocate(1)
    targets = allocate(variables)
    target_masks = allocate(variables)
    for index, row in enumerate(rows):
        steps = len(row["values"]) - 1
        values[index, :steps] = torch.from_numpy(row["values"][:-1])
        masks[index, :steps] = torch.from_numpy(row["masks"][:-1])
        deltas[index, :steps] = torch.from_numpy(row["deltas"][:-1])
        time[index, :steps] = torch.from_numpy(row["time"][:-1])
        targets[index, :steps] = torch.from_numpy(
            row["observed_values"][1:]
        )
        target_masks[index, :steps] = torch.from_numpy(row["masks"][1:])
    return {
        "values": values,
        "masks": masks,
        "deltas": deltas,
        "time": time,
        "targets": targets,
        "target_masks": target_masks,
        "lengths": lengths,
    }


def select_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def sequence_mask(lengths: Tensor, maximum: int) -> Tensor:
    positions = torch.arange(maximum, device=lengths.device)
    return positions.unsqueeze(0) < lengths.unsqueeze(1)


def forward_model(
    model: nn.Module,
    batch: dict[str, Tensor],
    padding_mask: Tensor,
) -> ForecastOutput:
    if isinstance(model, RecurrentStateSpaceModel):
        return model(
            batch["values"],
            batch["masks"],
            batch["deltas"],
            batch["time"],
            batch["targets"],
            batch["target_masks"],
        )
    if model.__class__.__name__.startswith("CausalTransformer"):
        return model(
            batch["values"],
            batch["masks"],
            batch["deltas"],
            batch["time"],
            padding_mask=padding_mask,
        )
    return model(
        batch["values"],
        batch["masks"],
        batch["deltas"],
        batch["time"],
    )


def loss_components(
    output: ForecastOutput,
    batch: dict[str, Tensor],
    *,
    mask_loss_weight: float,
    kl_weight: float,
) -> dict[str, Tensor]:
    valid = sequence_mask(batch["lengths"], output.mean.shape[1])
    valid_variables = valid.unsqueeze(-1)
    observed = batch["target_masks"].bool() & valid_variables
    scale = torch.exp(output.log_scale)
    gaussian_nll = (
        0.5 * ((batch["targets"] - output.mean) / scale).square()
        + output.log_scale
        + 0.5 * math.log(2.0 * math.pi)
    )
    value_nll = gaussian_nll.masked_select(observed).mean()
    mask_loss = F.binary_cross_entropy_with_logits(
        output.mask_logits,
        batch["target_masks"],
        reduction="none",
    ).masked_select(valid_variables.expand_as(output.mask_logits)).mean()
    if output.kl is None:
        kl = torch.zeros((), device=output.mean.device)
    else:
        kl = output.kl.masked_select(valid).mean()
    total = value_nll + mask_loss_weight * mask_loss + kl_weight * kl
    return {
        "loss": total,
        "value_nll": value_nll,
        "mask_bce": mask_loss,
        "kl": kl,
        "observed_targets": observed.sum(),
        "valid_mask_targets": valid.sum() * output.mean.shape[-1],
    }


def move_batch(batch: dict[str, Tensor], device: torch.device) -> dict[str, Tensor]:
    return {key: value.to(device) for key, value in batch.items()}


def run_epoch(
    model: nn.Module,
    loader: DataLoader[dict[str, Tensor]],
    *,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None,
    configuration: TrainingConfiguration,
) -> dict[str, float]:
    training = optimizer is not None
    model.train(training)
    totals = {
        "loss": 0.0,
        "value_nll": 0.0,
        "mask_bce": 0.0,
        "kl": 0.0,
        "batches": 0.0,
    }
    context = torch.enable_grad if training else torch.no_grad
    with context():
        for batch in loader:
            batch = move_batch(batch, device)
            padding_mask = ~sequence_mask(
                batch["lengths"], batch["values"].shape[1]
            )
            if optimizer is not None:
                optimizer.zero_grad(set_to_none=True)
            output = forward_model(model, batch, padding_mask)
            components = loss_components(
                output,
                batch,
                mask_loss_weight=configuration.mask_loss_weight,
                kl_weight=configuration.kl_weight,
            )
            if optimizer is not None:
                components["loss"].backward()
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), configuration.gradient_clip
                )
                optimizer.step()
            for key in ("loss", "value_nll", "mask_bce", "kl"):
                totals[key] += float(components[key].detach().cpu())
            totals["batches"] += 1
    if not totals["batches"]:
        raise ValueError("No batches were generated")
    return {
        key: value / totals["batches"]
        for key, value in totals.items()
        if key != "batches"
    }


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def write_history(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", choices=("grud", "transformer", "rssm"), required=True)
    parser.add_argument("--seed", type=int, default=20260912)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--maximum-sequence", type=int, default=72)
    parser.add_argument("--maximum-rollout-horizon", type=int, default=24)
    parser.add_argument("--hidden-size", type=int, default=96)
    parser.add_argument("--latent-size", type=int, default=32)
    parser.add_argument("--transformer-layers", type=int, default=3)
    parser.add_argument("--transformer-heads", type=int, default=4)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--mask-loss-weight", type=float, default=0.25)
    parser.add_argument("--kl-weight", type=float, default=1e-3)
    parser.add_argument("--gradient-clip", type=float, default=1.0)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    device = select_device(args.device)
    configuration = TrainingConfiguration(
        model=args.model,
        seed=args.seed,
        epochs=args.epochs,
        batch_size=args.batch_size,
        maximum_sequence=args.maximum_sequence,
        maximum_rollout_horizon=args.maximum_rollout_horizon,
        hidden_size=args.hidden_size,
        latent_size=args.latent_size,
        transformer_layers=args.transformer_layers,
        transformer_heads=args.transformer_heads,
        dropout=args.dropout,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        mask_loss_weight=args.mask_loss_weight,
        kl_weight=args.kl_weight,
        gradient_clip=args.gradient_clip,
        patience=args.patience,
        device=str(device),
    )
    set_seed(args.seed)
    train_split = PreparedSplit(args.data_dir / "train.npz")
    validation_split = PreparedSplit(args.data_dir / "validation.npz")
    if train_split.selected_names != validation_split.selected_names:
        raise ValueError("Training and validation variable orders differ")
    variables = len(train_split.selected_names)
    train_dataset = RandomPatientWindows(
        train_split, args.maximum_sequence, args.seed
    )
    validation_dataset = ExhaustivePatientWindows(
        validation_split, args.maximum_sequence
    )
    generator = torch.Generator().manual_seed(args.seed)
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
        collate_fn=collate_windows,
        num_workers=0,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_windows,
        num_workers=0,
    )
    model = build_model(
        args.model,
        variables,
        hidden_size=args.hidden_size,
        latent_size=args.latent_size,
        transformer_layers=args.transformer_layers,
        transformer_heads=args.transformer_heads,
        dropout=args.dropout,
        maximum_length=args.maximum_sequence + args.maximum_rollout_horizon,
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    history: list[dict[str, Any]] = []
    best_validation = float("inf")
    epochs_without_improvement = 0
    checkpoint_path = args.output_dir / "model.pt"
    for epoch in range(1, args.epochs + 1):
        train_dataset.set_epoch(epoch)
        train_metrics = run_epoch(
            model,
            train_loader,
            device=device,
            optimizer=optimizer,
            configuration=configuration,
        )
        validation_metrics = run_epoch(
            model,
            validation_loader,
            device=device,
            optimizer=None,
            configuration=configuration,
        )
        row: dict[str, Any] = {"epoch": epoch}
        row.update({f"train_{key}": value for key, value in train_metrics.items()})
        row.update(
            {f"validation_{key}": value for key, value in validation_metrics.items()}
        )
        history.append(row)
        print(json.dumps(row), flush=True)
        if validation_metrics["loss"] < best_validation:
            best_validation = validation_metrics["loss"]
            epochs_without_improvement = 0
            temporary = checkpoint_path.with_suffix(".tmp")
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "configuration": asdict(configuration),
                    "selected_variables": train_split.selected_names,
                    "parameter_count": parameter_count(model),
                    "best_validation_loss": best_validation,
                    "best_epoch": epoch,
                },
                temporary,
            )
            os.replace(temporary, checkpoint_path)
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                break

    write_history(args.output_dir / "training-history.csv", history)
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    result = {
        "status": "complete",
        "model": args.model,
        "seed": args.seed,
        "best_epoch": checkpoint["best_epoch"],
        "best_validation_loss": checkpoint["best_validation_loss"],
        "parameter_count": checkpoint["parameter_count"],
        "epochs_run": len(history),
        "configuration": asdict(configuration),
        "selected_variables": train_split.selected_names,
        "training_patients": len(train_dataset),
        "validation_windows": len(validation_dataset),
        "checkpoint": str(checkpoint_path),
        "determinism_note": (
            "Patient windows and data order are seeded. Accelerator kernels may "
            "remain nondeterministic; the publication protocol requires five seeds."
        ),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
