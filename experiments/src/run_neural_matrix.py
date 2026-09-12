#!/usr/bin/env python3
"""Run the prespecified neural training, evaluation, and calibration matrix."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


RANDOM_STREAM_POLICY = "split-specific-v1"
CONSTRAINT_POLICY = "rollout-state-and-emitted-v1"


def complete_json(
    path: Path,
    *,
    required_random_stream_policy: str | None = None,
    required_constraint_policy: str | None = None,
) -> bool:
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("status") != "complete":
            return False
        if required_random_stream_policy is not None:
            if (
                payload.get("random_stream_policy")
                != required_random_stream_policy
            ):
                return False
        if required_constraint_policy is not None:
            if payload.get("constraint_policy") != required_constraint_policy:
                return False
        return True
    except (json.JSONDecodeError, OSError):
        return False


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def evaluation_arguments(
    *,
    python: str,
    evaluator: Path,
    data_dir: Path,
    checkpoint: Path,
    output_dir: Path,
    splits: str,
    seed: int,
    device: str,
    horizons: str,
    minimum_context: int,
    maximum_context: int,
    stride: int,
    trajectory_samples: int,
    batch_size: int,
) -> list[str]:
    return [
        python,
        str(evaluator),
        "--data-dir",
        str(data_dir),
        "--checkpoint",
        str(checkpoint),
        "--output-dir",
        str(output_dir),
        "--splits",
        splits,
        "--horizons",
        horizons,
        "--minimum-context",
        str(minimum_context),
        "--maximum-context",
        str(maximum_context),
        "--stride",
        str(stride),
        "--trajectory-samples",
        str(trajectory_samples),
        "--batch-size",
        str(batch_size),
        "--seed",
        str(seed),
        "--device",
        device,
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument(
        "--models", default="grud,transformer,rssm"
    )
    parser.add_argument(
        "--seeds", default="20260912,20260913,20260914,20260915,20260916"
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--training-batch-size", type=int, default=64)
    parser.add_argument("--evaluation-batch-size", type=int, default=128)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--horizons", default="1,3,6,12,24")
    parser.add_argument("--minimum-context", type=int, default=12)
    parser.add_argument("--maximum-context", type=int, default=72)
    parser.add_argument("--stride", type=int, default=6)
    parser.add_argument("--trajectory-samples", type=int, default=20)
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable with the experiment dependencies installed.",
    )
    args = parser.parse_args()

    source_dir = Path(__file__).resolve().parent
    trainer = source_dir / "train_neural_forecaster.py"
    evaluator = source_dir / "evaluate_neural_forecaster.py"
    models = [value.strip() for value in args.models.split(",") if value.strip()]
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    allowed_models = {"grud", "transformer", "rssm"}
    unknown = sorted(set(models) - allowed_models)
    if unknown:
        raise ValueError(f"Unknown models: {unknown}")

    for seed in seeds:
        for model in models:
            run_dir = args.result_root / model / f"seed-{seed}"
            checkpoint = run_dir / "model.pt"
            if not complete_json(run_dir / "summary.json"):
                run(
                    [
                        args.python,
                        str(trainer),
                        "--data-dir",
                        str(args.data_dir),
                        "--output-dir",
                        str(run_dir),
                        "--model",
                        model,
                        "--seed",
                        str(seed),
                        "--epochs",
                        str(args.epochs),
                        "--batch-size",
                        str(args.training_batch_size),
                        "--maximum-sequence",
                        str(args.maximum_context),
                        "--maximum-rollout-horizon",
                        str(max(int(value) for value in args.horizons.split(","))),
                        "--device",
                        args.device,
                    ]
                )

            evaluation_dir = run_dir / "evaluation"
            if not complete_json(
                evaluation_dir / "summary.json",
                required_random_stream_policy=RANDOM_STREAM_POLICY,
                required_constraint_policy=CONSTRAINT_POLICY,
            ):
                run(
                    evaluation_arguments(
                        python=args.python,
                        evaluator=evaluator,
                        data_dir=args.data_dir,
                        checkpoint=checkpoint,
                        output_dir=evaluation_dir,
                        splits="internal_test,external_test",
                        seed=seed,
                        device=args.device,
                        horizons=args.horizons,
                        minimum_context=args.minimum_context,
                        maximum_context=args.maximum_context,
                        stride=args.stride,
                        trajectory_samples=args.trajectory_samples,
                        batch_size=args.evaluation_batch_size,
                    )
                )

            calibration_dir = run_dir / "external-calibration-fit"
            calibration_artifact = calibration_dir / "spread-calibration.json"
            if not complete_json(
                calibration_artifact,
                required_random_stream_policy=RANDOM_STREAM_POLICY,
            ):
                command = evaluation_arguments(
                    python=args.python,
                    evaluator=evaluator,
                    data_dir=args.data_dir,
                    checkpoint=checkpoint,
                    output_dir=calibration_dir,
                    splits="external_calibration",
                    seed=seed,
                    device=args.device,
                    horizons=args.horizons,
                    minimum_context=args.minimum_context,
                    maximum_context=args.maximum_context,
                    stride=args.stride,
                    trajectory_samples=args.trajectory_samples,
                    batch_size=args.evaluation_batch_size,
                )
                command.extend(
                    [
                        "--fit-spread-calibration-output",
                        str(calibration_artifact),
                    ]
                )
                run(command)

            recalibrated_dir = run_dir / "external-test-recalibrated"
            if not complete_json(
                recalibrated_dir / "summary.json",
                required_random_stream_policy=RANDOM_STREAM_POLICY,
                required_constraint_policy=CONSTRAINT_POLICY,
            ):
                command = evaluation_arguments(
                    python=args.python,
                    evaluator=evaluator,
                    data_dir=args.data_dir,
                    checkpoint=checkpoint,
                    output_dir=recalibrated_dir,
                    splits="external_test",
                    seed=seed,
                    device=args.device,
                    horizons=args.horizons,
                    minimum_context=args.minimum_context,
                    maximum_context=args.maximum_context,
                    stride=args.stride,
                    trajectory_samples=args.trajectory_samples,
                    batch_size=args.evaluation_batch_size,
                )
                command.extend(
                    ["--spread-calibration", str(calibration_artifact)]
                )
                run(command)

    print(
        json.dumps(
            {
                "status": "complete",
                "models": models,
                "seeds": seeds,
                "result_root": str(args.result_root),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
