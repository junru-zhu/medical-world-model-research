#!/usr/bin/env python3
"""Build publication figures for the ICU world-model benchmark.

The script consumes only frozen analysis tables. Matplotlib is the exclusive
rendering backend. Add the Nature figure-skill scripts directory to PYTHONPATH
so the mandatory rendered panel-alignment gate can be imported.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

try:
    from audit_panel_alignment import require_matplotlib_panel_alignment
except ImportError as exc:  # pragma: no cover - environment-specific guard
    raise RuntimeError(
        "Add the Nature figure-skill scripts directory to PYTHONPATH before "
        "running this renderer."
    ) from exc


FIGURE_62MM_HEIGHT_IN = 2.4409448819
FIGURE_82MM_HEIGHT_IN = 3.2283464567
FIGURE_65MM_HEIGHT_IN = 2.5590551181
FIGURE_67MM_HEIGHT_IN = 2.6377952756
FIGURE_78MM_HEIGHT_IN = 3.0708661417
FIGURE_126MM_HEIGHT_IN = 4.9606299213
FIGURE_132MM_HEIGHT_IN = 5.1968503937
HORIZONS = (1, 3, 6, 12, 24)
NEURAL_MODELS = ("grud", "transformer", "rssm")
MODEL_ORDER = (
    "locf",
    "global_median",
    "hourly_median",
    "ridge_var",
    "grud",
    "transformer",
    "rssm",
)
MODEL_LABELS = {
    "locf": "LOCF",
    "global_median": "Global median",
    "hourly_median": "Hourly median",
    "ridge_var": "Ridge VAR",
    "grud": "GRU-D-style",
    "transformer": "Masked Transformer",
    "rssm": "State-space model",
}
MODEL_COLORS = {
    "locf": "#252525",
    "global_median": "#B7B7B7",
    "hourly_median": "#888888",
    "ridge_var": "#53616D",
    "grud": "#0072B2",
    "transformer": "#D55E00",
    "rssm": "#7A5195",
}
MODEL_MARKERS = {
    "locf": "s",
    "global_median": "D",
    "hourly_median": "v",
    "ridge_var": "P",
    "grud": "o",
    "transformer": "^",
    "rssm": "X",
}
MODEL_LINESTYLES = {
    "locf": "--",
    "global_median": ":",
    "hourly_median": "-.",
    "ridge_var": "--",
    "grud": "-",
    "transformer": "-",
    "rssm": "-",
}
TEXT_COLOR = "#202124"
AXIS_COLOR = "#343A40"
GRID_COLOR = "#E5E7EB"
REFERENCE_COLOR = "#6B7280"
ZERO_COLOR = "#9B4A45"


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Arial",
                "Helvetica",
                "Liberation Sans",
                "DejaVu Sans",
                "sans-serif",
            ],
            "font.size": 7,
            "axes.titlesize": 7.6,
            "axes.titleweight": "normal",
            "axes.labelsize": 6.8,
            "xtick.labelsize": 6.2,
            "ytick.labelsize": 6.2,
            "legend.fontsize": 6.0,
            "text.color": TEXT_COLOR,
            "axes.labelcolor": TEXT_COLOR,
            "axes.edgecolor": AXIS_COLOR,
            "xtick.color": AXIS_COLOR,
            "ytick.color": AXIS_COLOR,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
            "axes.axisbelow": True,
            "axes.titlepad": 5,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 2.6,
            "ytick.major.size": 2.6,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "grid.color": GRID_COLOR,
            "grid.linewidth": 0.45,
            "grid.alpha": 1.0,
            "lines.linewidth": 1.3,
            "lines.markersize": 3.9,
            "lines.solid_capstyle": "round",
            "lines.dash_capstyle": "round",
            "legend.frameon": False,
            "legend.handlelength": 2.1,
            "legend.handletextpad": 0.45,
            "legend.columnspacing": 1.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def add_panel_label(axis: mpl.axes.Axes, label: str) -> None:
    axis.annotate(
        label,
        xy=(0.0, 1.0),
        xycoords="axes fraction",
        xytext=(-10, 6),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=8.2,
        fontweight="bold",
        annotation_clip=False,
    )


def style_marker(model: str) -> dict[str, object]:
    if model in NEURAL_MODELS:
        return {
            "markeredgecolor": "white",
            "markeredgewidth": 0.55,
        }
    return {
        "markeredgecolor": MODEL_COLORS[model],
        "markeredgewidth": 0.25,
    }


def style_axis_grid(
    axis: mpl.axes.Axes,
    *,
    direction: str,
) -> None:
    axis.grid(axis=direction)
    axis.spines["left"].set_color(AXIS_COLOR)
    axis.spines["bottom"].set_color(AXIS_COLOR)


def save_figure(
    fig: mpl.figure.Figure,
    output_base: Path,
    *,
    exclude_axes: Iterable[mpl.axes.Axes] = (),
) -> None:
    output_base.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    require_matplotlib_panel_alignment(
        fig,
        json_out=output_base.with_suffix(".alignment.json"),
        overlay_svg=output_base.with_suffix(".alignment.svg"),
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        require_panel_labels=True,
        strict=True,
        exclude_axes=list(exclude_axes),
    )
    fig.savefig(output_base.with_suffix(".svg"))
    fig.savefig(output_base.with_suffix(".pdf"))
    fig.savefig(output_base.with_suffix(".png"), dpi=300)
    fig.savefig(output_base.with_suffix(".tiff"), dpi=600)
    plt.close(fig)


def write_source_data(
    output_dir: Path, name: str, frame: pd.DataFrame
) -> None:
    source_dir = output_dir / "source-data"
    source_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(source_dir / name, index=False)


def draw_box(
    axis: mpl.axes.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str,
    edgecolor: str = "#424242",
    textcolor: str = "#202020",
    linewidth: float = 0.8,
    fontsize: float = 6.4,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        linewidth=linewidth,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    axis.add_patch(patch)
    axis.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=textcolor,
        linespacing=1.15,
    )
    return patch


def arrow(
    axis: mpl.axes.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = "#555555",
    connectionstyle: str = "arc3",
    linestyle: str = "-",
) -> None:
    axis.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=7,
            linewidth=0.8,
            color=color,
            linestyle=linestyle,
            connectionstyle=connectionstyle,
        )
    )


def build_figure_1(data_summary: Path, output_dir: Path) -> None:
    summary = json.loads(data_summary.read_text(encoding="utf-8"))
    split_counts = {
        row["split"]: int(row["patients"]) for row in summary["splits"]
    }
    expected = {
        "train",
        "validation",
        "internal_test",
        "external_calibration",
        "external_test",
    }
    if set(split_counts) != expected:
        raise ValueError("Unexpected patient-split schema.")

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(7.0866141732, FIGURE_82MM_HEIGHT_IN),  # 180 mm wide
        constrained_layout=False,
    )
    fig.subplots_adjust(
        left=0.035,
        right=0.985,
        bottom=0.08,
        top=0.84,
        wspace=0.18,
    )

    axis = axes[0]
    axis.set_title(
        "Patient-level splits and evidence path",
        loc="left",
        pad=8,
        fontsize=7.5,
    )
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    add_panel_label(axis, "a")
    axis.text(
        0.02,
        0.91,
        "Cohort A  (n = 20,336)",
        fontsize=6.8,
        fontweight="bold",
        color="#284B63",
    )
    draw_box(
        axis,
        0.02,
        0.67,
        0.27,
        0.14,
        f"Train\nn = {split_counts['train']:,}",
        facecolor="#DCEAF2",
        edgecolor="#48748D",
    )
    draw_box(
        axis,
        0.35,
        0.67,
        0.27,
        0.14,
        f"Validation\nn = {split_counts['validation']:,}",
        facecolor="#DCEAF2",
        edgecolor="#48748D",
    )
    draw_box(
        axis,
        0.69,
        0.67,
        0.29,
        0.14,
        f"Internal test\nn = {split_counts['internal_test']:,}",
        facecolor="#EFF4F7",
        edgecolor="#48748D",
    )
    draw_box(
        axis,
        0.21,
        0.43,
        0.41,
        0.12,
        "Fit, select and freeze",
        facecolor="#BFD8E6",
        edgecolor="#48748D",
    )
    arrow(axis, (0.16, 0.67), (0.31, 0.55), color="#48748D")
    arrow(axis, (0.49, 0.67), (0.48, 0.55), color="#48748D")

    axis.text(
        0.02,
        0.32,
        "Cohort B  (n = 20,000)",
        fontsize=6.8,
        fontweight="bold",
        color="#7A431E",
    )
    draw_box(
        axis,
        0.02,
        0.08,
        0.38,
        0.14,
        f"External calibration\nn = {split_counts['external_calibration']:,}",
        facecolor="#F6E5D5",
        edgecolor="#B36A36",
    )
    draw_box(
        axis,
        0.54,
        0.08,
        0.44,
        0.14,
        f"Frozen external test\nn = {split_counts['external_test']:,}",
        facecolor="#FBF1E8",
        edgecolor="#B36A36",
        linewidth=1.15,
    )
    arrow(
        axis,
        (0.62, 0.49),
        (0.83, 0.67),
        color="#555555",
        connectionstyle="arc3,rad=0.24",
    )
    arrow(
        axis,
        (0.57, 0.43),
        (0.76, 0.22),
        color="#48748D",
        connectionstyle="arc3,rad=-0.12",
    )
    arrow(
        axis,
        (0.40, 0.15),
        (0.54, 0.15),
        color="#B36A36",
        connectionstyle="arc3,rad=0",
        linestyle="--",
    )

    axis = axes[1]
    axis.set_title(
        "Free-running rollout on common support",
        loc="left",
        pad=8,
        fontsize=7.5,
    )
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    add_panel_label(axis, "b")
    axis.add_patch(
        FancyBboxPatch(
            (0.03, 0.34),
            0.33,
            0.35,
            boxstyle="round,pad=0.005,rounding_size=0.01",
            linewidth=0,
            facecolor="#DCEAF2",
        )
    )
    axis.add_patch(
        FancyBboxPatch(
            (0.36, 0.34),
            0.61,
            0.35,
            boxstyle="round,pad=0.005,rounding_size=0.01",
            linewidth=0,
            facecolor="#F6E5D5",
        )
    )
    axis.plot([0.36, 0.36], [0.30, 0.78], color="#333333", linewidth=0.9)
    axis.text(
        0.19,
        0.75,
        "Observed context\n12–72 h",
        ha="center",
        va="bottom",
        fontsize=6.1,
        color="#284B63",
    )
    axis.text(
        0.67,
        0.75,
        "Generated future",
        ha="center",
        va="bottom",
        fontsize=6.1,
        color="#7A431E",
    )
    x_positions = np.linspace(0.04, 0.96, 37)
    y_positions = 0.51 + 0.09 * np.sin(np.linspace(0, 2.2 * np.pi, 37))
    anchor_index = int(np.argmin(np.abs(x_positions - 0.36)))
    axis.plot(
        x_positions[: anchor_index + 1],
        y_positions[: anchor_index + 1],
        color="#48748D",
        linewidth=1.5,
    )
    axis.plot(
        x_positions[anchor_index:],
        y_positions[anchor_index:],
        color="#B36A36",
        linewidth=1.5,
    )
    horizon_positions = {
        1: 0.385,
        3: 0.435,
        6: 0.515,
        12: 0.665,
        24: 0.96,
    }
    for horizon, x_value in horizon_positions.items():
        y_value = float(np.interp(x_value, x_positions, y_positions))
        axis.plot(
            x_value,
            y_value,
            marker="o",
            markersize=3.8,
            color="#B36A36",
            markeredgecolor="white",
            markeredgewidth=0.5,
        )
        axis.text(
            x_value,
            0.27,
            str(horizon),
            ha="center",
            va="top",
            fontsize=5.8,
            color="#333333",
        )
    axis.text(
        0.35,
        0.27,
        "0",
        ha="center",
        va="top",
        fontsize=5.8,
        color="#333333",
    )
    axis.annotate(
        "Generated value + mask\nbecome the next input",
        xy=(0.58, 0.45),
        xytext=(0.54, 0.03),
        textcoords="axes fraction",
        ha="center",
        va="bottom",
        fontsize=5.8,
        arrowprops={
            "arrowstyle": "-|>",
            "color": "#8D522D",
            "linewidth": 0.7,
        },
    )
    axis.text(
        0.50,
        0.88,
        "All horizons use anchors with 24 future hours available",
        ha="center",
        va="center",
        fontsize=5.7,
        color="#5A5A5A",
    )

    axis = axes[2]
    axis.set_title(
        "Measured evidence and claim boundary",
        loc="left",
        pad=8,
        fontsize=7.5,
    )
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    add_panel_label(axis, "c")
    outcome_boxes = [
        (0.04, 0.70, "Trajectory error", "#E4EEF4", "#48748D"),
        (0.53, 0.70, "Finite-draw uncertainty", "#F3EAF8", "#7A5AA6"),
        (0.04, 0.48, "Mask fidelity", "#E9F1E5", "#5E7C50"),
        (0.53, 0.48, "Chart-state constraints", "#F6E5D5", "#B36A36"),
        (0.28, 0.26, "Cross-cohort transfer", "#EEEEEE", "#666666"),
    ]
    for x, y, label, face, edge in outcome_boxes:
        width = 0.43 if x != 0.28 else 0.46
        draw_box(
            axis,
            x,
            y,
            width,
            0.14,
            label,
            facecolor=face,
            edgecolor=edge,
            fontsize=5.8,
        )
    draw_box(
        axis,
        0.04,
        0.02,
        0.92,
        0.13,
        "Not identified\nTreatment effects • counterfactuals • policies\n"
        "Clinical benefit • deployment safety",
        facecolor="#FBE8E8",
        edgecolor="#A94B4B",
        textcolor="#7A2929",
        linewidth=1.0,
        fontsize=5.5,
    )

    save_figure(fig, output_dir / "figure1-evaluation-design")

    source = pd.DataFrame(
        [
            {"split": key, "patients": value}
            for key, value in split_counts.items()
        ]
    )
    write_source_data(output_dir, "figure1-split-counts.csv", source)


def model_horizon_summary(seed_metrics: pd.DataFrame, metric: str) -> pd.DataFrame:
    selected = seed_metrics[
        (seed_metrics["evaluation"] == "zero_shot")
        & (seed_metrics["split"] == "external_test")
    ].copy()
    rows: list[dict[str, float | int | str]] = []
    for (model, horizon), group in selected.groupby(
        ["model", "horizon_hours"], sort=False
    ):
        numeric = pd.to_numeric(group[metric], errors="coerce").to_numpy(
            dtype=float
        )
        values = numeric[np.isfinite(numeric)]
        if not len(values):
            continue
        rows.append(
            {
                "model": model,
                "horizon_hours": int(horizon),
                "mean": float(values.mean()),
                "seed_sd": (
                    float(values.std(ddof=1)) if len(values) > 1 else 0.0
                ),
                "seeds": int(len(values)),
                "input_rows": int(len(group)),
                "finite_rows": int(len(values)),
            }
        )
    return pd.DataFrame(rows)


def plot_horizon_lines(
    axis: mpl.axes.Axes,
    frame: pd.DataFrame,
    *,
    ylabel: str,
    models: Iterable[str],
    show_seed_band: bool = True,
) -> None:
    for model in models:
        group = (
            frame[frame["model"] == model]
            .sort_values("horizon_hours")
            .set_index("horizon_hours")
            .reindex(HORIZONS)
        )
        if group["mean"].isna().all():
            continue
        x_values = np.asarray(HORIZONS, dtype=float)
        y_values = group["mean"].to_numpy(dtype=float)
        seed_sd = group["seed_sd"].fillna(0.0).to_numpy(dtype=float)
        axis.plot(
            x_values,
            y_values,
            color=MODEL_COLORS[model],
            marker=MODEL_MARKERS[model],
            linestyle=MODEL_LINESTYLES[model],
            linewidth=1.55 if model in NEURAL_MODELS else 0.95,
            markersize=4.2 if model in NEURAL_MODELS else 3.5,
            alpha=1.0 if model in NEURAL_MODELS else 0.78,
            label=MODEL_LABELS[model],
            zorder=4 if model in NEURAL_MODELS else 2,
            **style_marker(model),
        )
        if show_seed_band and model in NEURAL_MODELS:
            axis.fill_between(
                x_values,
                y_values - seed_sd,
                y_values + seed_sd,
                color=MODEL_COLORS[model],
                alpha=0.09,
                linewidth=0,
                zorder=1,
            )
    axis.set_xticks(HORIZONS)
    axis.set_xlabel("Rollout horizon (h)")
    axis.set_ylabel(ylabel)
    style_axis_grid(axis, direction="y")


def build_figure_2(analysis_dir: Path, output_dir: Path) -> None:
    seed_metrics = read_csv(analysis_dir / "seed-patient-macro.csv")
    contrasts = read_csv(analysis_dir / "paired-12h-nmae-contrasts.csv")
    cross_site = read_csv(analysis_dir / "cross-site-nmae-bootstrap.csv")
    ranks = read_csv(analysis_dir / "rank-stability.csv")

    horizon = model_horizon_summary(seed_metrics, "patient_nmae")
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(7.0866141732, FIGURE_126MM_HEIGHT_IN),  # 180 mm wide
        constrained_layout=True,
    )

    axis = axes[0, 0]
    add_panel_label(axis, "a")
    axis.set_title("Zero-shot external free-running error", loc="left", pad=8)
    plot_horizon_lines(
        axis,
        horizon,
        ylabel="Patient-macro NMAE",
        models=MODEL_ORDER,
    )
    axis = axes[0, 1]
    add_panel_label(axis, "b")
    axis.set_title("Frozen external 12-h paired contrasts", loc="left", pad=8)
    selected = contrasts[contrasts["split"] == "external_test"].copy()
    selected["label"] = selected.apply(
        lambda row: (
            f"{MODEL_LABELS[row['model_a']]} − "
            f"{MODEL_LABELS[row['model_b']]}"
        ),
        axis=1,
    )
    selected = selected.iloc[::-1].reset_index(drop=True)
    y_values = np.arange(len(selected))
    centers = selected["difference_a_minus_b"].to_numpy(dtype=float)
    lower = selected["ci_95_lower"].to_numpy(dtype=float)
    upper = selected["ci_95_upper"].to_numpy(dtype=float)
    for index, row in selected.iterrows():
        color = MODEL_COLORS[str(row["model_a"])]
        axis.errorbar(
            row["difference_a_minus_b"],
            y_values[index],
            xerr=np.asarray(
                [[
                    row["difference_a_minus_b"] - row["ci_95_lower"]
                ], [
                    row["ci_95_upper"] - row["difference_a_minus_b"]
                ]]
            ),
            fmt=MODEL_MARKERS[str(row["model_a"])],
            color=color,
            ecolor=color,
            capsize=2.2,
            linewidth=1.05,
            markersize=4.3,
            **style_marker(str(row["model_a"])),
        )
    axis.axvline(0.0, color=ZERO_COLOR, linewidth=0.8, linestyle="--")
    axis.set_yticks(y_values, selected["label"])
    axis.set_xlabel("NMAE difference (model A − model B)")
    style_axis_grid(axis, direction="x")

    axis = axes[1, 0]
    add_panel_label(axis, "c")
    axis.set_title("Internal-to-external change at 12 h", loc="left", pad=8)
    cross_site = cross_site.set_index("model").reindex(MODEL_ORDER).reset_index()
    y_values = np.arange(len(cross_site))[::-1]
    centers = cross_site["absolute_degradation"].to_numpy(dtype=float)
    lower = cross_site["absolute_ci_95_lower"].to_numpy(dtype=float)
    upper = cross_site["absolute_ci_95_upper"].to_numpy(dtype=float)
    colors = [MODEL_COLORS[model] for model in cross_site["model"]]
    for index, row in cross_site.iterrows():
        axis.errorbar(
            row["absolute_degradation"],
            y_values[index],
            xerr=np.asarray(
                [
                    [
                        row["absolute_degradation"]
                        - row["absolute_ci_95_lower"]
                    ],
                    [
                        row["absolute_ci_95_upper"]
                        - row["absolute_degradation"]
                    ],
                ]
            ),
            fmt=MODEL_MARKERS[row["model"]],
            color=colors[index],
            ecolor=colors[index],
            capsize=2.0,
            linewidth=1.0,
            markersize=4.2,
            **style_marker(str(row["model"])),
        )
    axis.axvline(0.0, color=REFERENCE_COLOR, linewidth=0.75, linestyle="--")
    axis.set_yticks(
        y_values,
        [MODEL_LABELS[model] for model in cross_site["model"]],
    )
    axis.set_xlabel("External − internal patient-macro NMAE")
    style_axis_grid(axis, direction="x")

    axis = axes[1, 1]
    add_panel_label(axis, "d")
    axis.set_title("Model-rank stability", loc="left", pad=8)
    rank_rows = (
        ranks.groupby(
            [
                "comparison_type",
                "context",
                "from_condition",
                "to_condition",
            ],
            sort=False,
        )["spearman_rank_correlation"]
        .agg(["mean", "min", "max"])
        .reset_index()
    )
    rank_rows["label"] = rank_rows.apply(
        lambda row: (
            f"{str(row['context']).replace('_', ' ').title()}: "
            f"{row['from_condition']} → "
            f"{row['to_condition']}"
            if row["comparison_type"] == "cross_horizon"
            else (
                f"{row['context']}: internal → external"
            )
        ),
        axis=1,
    )
    rank_rows = rank_rows.iloc[::-1].reset_index(drop=True)
    y_values = np.arange(len(rank_rows))
    centers = rank_rows["mean"].to_numpy(dtype=float)
    lower = rank_rows["min"].to_numpy(dtype=float)
    upper = rank_rows["max"].to_numpy(dtype=float)
    axis.errorbar(
        centers,
        y_values,
        xerr=np.vstack([centers - lower, upper - centers]),
        fmt="o",
        color="#4F5B66",
        ecolor="#83909B",
        capsize=2.0,
        linewidth=1.0,
        markersize=4.0,
    )
    axis.axvline(0.0, color="#B8BDC2", linewidth=0.7)
    axis.set_xlim(-1.05, 1.05)
    axis.set_yticks(y_values, rank_rows["label"])
    axis.set_xlabel("Spearman rank correlation, mean [seed range]")
    style_axis_grid(axis, direction="x")

    model_handles = [
        Line2D(
            [0],
            [0],
            color=MODEL_COLORS[model],
            marker=MODEL_MARKERS[model],
            linestyle=MODEL_LINESTYLES[model],
            linewidth=1.45 if model in NEURAL_MODELS else 0.95,
            markersize=4.1 if model in NEURAL_MODELS else 3.5,
            alpha=1.0 if model in NEURAL_MODELS else 0.78,
            label=MODEL_LABELS[model],
            **style_marker(model),
        )
        for model in MODEL_ORDER
    ]
    fig.legend(
        handles=model_handles,
        loc="outside upper center",
        ncol=4,
    )

    save_figure(fig, output_dir / "figure2-accuracy-and-transfer")
    write_source_data(output_dir, "figure2a-horizon-nmae.csv", horizon)
    write_source_data(
        output_dir, "figure2b-paired-contrasts.csv", selected
    )
    write_source_data(
        output_dir, "figure2c-cross-site-bootstrap.csv", cross_site
    )
    write_source_data(
        output_dir, "figure2d-rank-stability.csv", rank_rows
    )


def build_figure_3(analysis_dir: Path, output_dir: Path) -> None:
    calibration = read_csv(analysis_dir / "external-calibration-table.csv")
    metrics = [
        (
            "coverage_90",
            "Empirical 5th-95th percentile coverage",
            "Empirical interval coverage",
        ),
        (
            "mean_interval_width_scaled",
            "Mean interval width (scaled units)",
            "Interval width",
        ),
        ("patient_crps", "Patient-macro CRPS", "CRPS"),
        (
            "patient_nll",
            "Moment-matched Gaussian negative log score",
            "Gaussian negative log score",
        ),
    ]
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(7.0866141732, FIGURE_126MM_HEIGHT_IN),  # 180 mm wide
        constrained_layout=True,
    )
    for panel_index, (axis, (metric, ylabel, title)) in enumerate(
        zip(axes.flat, metrics, strict=True)
    ):
        add_panel_label(axis, chr(ord("a") + panel_index))
        axis.set_title(title, loc="left", pad=8)
        for model in NEURAL_MODELS:
            group = calibration[calibration["model"] == model].sort_values(
                "horizon_hours"
            )
            for evaluation, linestyle, marker in (
                ("zero_shot", "-", "o"),
                ("recalibrated", "--", "^"),
            ):
                mean = group[f"{evaluation}_{metric}_mean"].to_numpy(
                    dtype=float
                )
                standard_deviation = group[
                    f"{evaluation}_{metric}_seed_sd"
                ].to_numpy(dtype=float)
                x_values = group["horizon_hours"].to_numpy(dtype=float)
                axis.errorbar(
                    x_values,
                    mean,
                    yerr=standard_deviation,
                    color=MODEL_COLORS[model],
                    linestyle=linestyle,
                    marker=marker,
                    linewidth=1.4 if evaluation == "zero_shot" else 1.15,
                    markersize=4.0,
                    capsize=1.6,
                    alpha=1.0 if evaluation == "zero_shot" else 0.86,
                    markerfacecolor=(
                        MODEL_COLORS[model]
                        if evaluation == "zero_shot"
                        else "white"
                    ),
                    markeredgecolor=MODEL_COLORS[model],
                    markeredgewidth=0.55,
                )
        if metric == "coverage_90":
            axis.axhline(
                0.90,
                color="#444444",
                linewidth=0.8,
                linestyle=":",
            )
            axis.axhline(
                0.814,
                color="#8A8A8A",
                linewidth=0.8,
                linestyle="-.",
            )
            axis.set_ylim(0.74, 0.96)
            axis.text(
                0.985,
                0.90,
                "0.90 target",
                transform=axis.get_yaxis_transform(),
                ha="right",
                va="bottom",
                fontsize=5.3,
                color="#444444",
            )
            axis.text(
                0.985,
                0.814,
                "20-draw expectation",
                transform=axis.get_yaxis_transform(),
                ha="right",
                va="bottom",
                fontsize=5.3,
                color="#737373",
            )
        axis.set_xticks(HORIZONS)
        axis.set_xlabel("Rollout horizon (h)")
        axis.set_ylabel(ylabel)
        style_axis_grid(axis, direction="y")

    model_handles = [
        Line2D(
            [0],
            [0],
            color=MODEL_COLORS[model],
            marker=MODEL_MARKERS[model],
            linewidth=1.4,
            label=MODEL_LABELS[model],
            **style_marker(model),
        )
        for model in NEURAL_MODELS
    ]
    evaluation_handles = [
        Line2D(
            [0],
            [0],
            color="#555555",
            linestyle="-",
            marker="o",
            markerfacecolor="#555555",
            label="Zero-shot raw",
        ),
        Line2D(
            [0],
            [0],
            color="#555555",
            linestyle="--",
            marker="^",
            markerfacecolor="white",
            markeredgecolor="#555555",
            label="External spread-adapted",
        ),
    ]
    fig.legend(
        handles=model_handles + evaluation_handles,
        loc="outside upper center",
        ncol=5,
    )
    save_figure(fig, output_dir / "figure3-uncertainty-adaptation")
    write_source_data(
        output_dir, "figure3-calibration-and-scores.csv", calibration
    )


def build_figure_4(analysis_dir: Path, output_dir: Path) -> None:
    seed_metrics = read_csv(analysis_dir / "seed-patient-macro.csv")
    constraints = read_csv(analysis_dir / "aggregate-constraints.csv")
    mask = model_horizon_summary(seed_metrics, "mask_brier")
    external_constraints = constraints[
        constraints["split"] == "external_test"
    ].copy()

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(7.0866141732, FIGURE_78MM_HEIGHT_IN),  # 180 mm wide
        constrained_layout=False,
    )
    fig.subplots_adjust(
        left=0.085,
        right=0.985,
        bottom=0.26,
        top=0.72,
        wspace=0.32,
    )

    axis = axes[0]
    add_panel_label(axis, "a")
    axis.set_title("Measurement-mask fidelity", loc="left", pad=8)
    plot_horizon_lines(
        axis,
        mask,
        ylabel="Patient-macro mask Brier score",
        models=NEURAL_MODELS,
    )

    axis = axes[1]
    add_panel_label(axis, "b")
    axis.set_title("Arterial-pressure ordering", loc="left", pad=8)
    pressure = external_constraints[
        external_constraints["constraint"] == "pressure_order"
    ].copy()
    for model in MODEL_ORDER:
        group = (
            pressure[pressure["model"] == model]
            .sort_values("horizon_hours")
            .set_index("horizon_hours")
            .reindex(HORIZONS)
        )
        if group["mean"].isna().all():
            continue
        x_values = np.asarray(HORIZONS, dtype=float)
        means = group["mean"].to_numpy(dtype=float)
        standard_deviation = group["standard_deviation"].fillna(0.0).to_numpy(
            dtype=float
        )
        axis.plot(
            x_values,
            means,
            color=MODEL_COLORS[model],
            linestyle=MODEL_LINESTYLES[model],
            marker=MODEL_MARKERS[model],
            linewidth=1.55 if model in NEURAL_MODELS else 0.95,
            markersize=4.2 if model in NEURAL_MODELS else 3.5,
            alpha=1.0 if model in NEURAL_MODELS else 0.78,
            label=MODEL_LABELS[model],
            **style_marker(model),
        )
        if model in NEURAL_MODELS:
            axis.fill_between(
                x_values,
                np.maximum(means - standard_deviation, 0.0),
                means + standard_deviation,
                color=MODEL_COLORS[model],
                alpha=0.09,
                linewidth=0,
            )
    axis.set_xticks(HORIZONS)
    axis.set_xlabel("Rollout horizon (h)")
    axis.set_ylabel("Violations per 1,000 sampled states")
    style_axis_grid(axis, direction="y")

    figure_handles = [
        Line2D(
            [0],
            [0],
            color=MODEL_COLORS[model],
            marker=MODEL_MARKERS[model],
            linestyle=MODEL_LINESTYLES[model],
            linewidth=1.45 if model in NEURAL_MODELS else 0.95,
            label=MODEL_LABELS[model],
            alpha=1.0 if model in NEURAL_MODELS else 0.78,
            **style_marker(model),
        )
        for model in MODEL_ORDER
    ]
    fig.legend(
        handles=figure_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=4,
        fontsize=5.9,
    )

    axis = axes[2]
    add_panel_label(axis, "c")
    axis.set_title("12-h rollout-state constraint profile", loc="left", pad=8)
    constraint_order = (
        "pressure_order",
        "O2Sat_bounds",
        "SaO2_bounds",
        "FiO2_bounds",
    )
    constraint_labels = (
        "Pressure\nordering",
        "O2Sat\nbounds",
        "SaO2\nbounds",
        "FiO2\nbounds",
    )
    heat = (
        external_constraints[
            (external_constraints["horizon_hours"] == 12)
            & (external_constraints["model"].isin(NEURAL_MODELS))
            & (external_constraints["constraint"].isin(constraint_order))
        ]
        .pivot(index="model", columns="constraint", values="mean")
        .reindex(index=NEURAL_MODELS, columns=constraint_order)
    )
    if heat.isna().any().any():
        raise ValueError("Incomplete 12-hour neural constraint profile.")
    values = heat.to_numpy(dtype=float)
    axis.imshow(
        np.log1p(values),
        cmap=mpl.colors.LinearSegmentedColormap.from_list(
            "ieee_constraint_blue",
            ("#F2F6F9", "#BED7E6", "#5B9CC5", "#174F7A"),
        ),
        aspect="auto",
        interpolation="nearest",
    )
    axis.set_xticks(np.arange(len(constraint_order)), constraint_labels)
    for tick in axis.get_xticklabels():
        tick.set_rotation(0)
        tick.set_ha("center")
        tick.set_rotation_mode("anchor")
    axis.set_yticks(
        np.arange(len(NEURAL_MODELS)),
        ("GRU-D", "Transformer", "RSSM"),
    )
    axis.tick_params(axis="y", pad=4)
    axis.set_xticks(
        np.arange(-0.5, len(constraint_order), 1),
        minor=True,
    )
    axis.set_yticks(
        np.arange(-0.5, len(NEURAL_MODELS), 1),
        minor=True,
    )
    axis.grid(which="minor", color="white", linewidth=0.8)
    axis.tick_params(which="minor", bottom=False, left=False)
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            value = values[row, column]
            text_color = (
                "white"
                if np.log1p(value)
                > 0.58 * float(np.log1p(values).max())
                else "#202020"
            )
            axis.text(
                column,
                row,
                f"{value:.1f}",
                ha="center",
                va="center",
                fontsize=6.1,
                color=text_color,
            )
    axis.spines["right"].set_visible(True)
    axis.spines["top"].set_visible(True)

    save_figure(fig, output_dir / "figure4-dynamic-validity")
    write_source_data(output_dir, "figure4a-mask-brier.csv", mask)
    write_source_data(output_dir, "figure4b-pressure-order.csv", pressure)
    heat.reset_index().to_csv(
        output_dir / "source-data/figure4c-constraint-profile.csv",
        index=False,
    )


def build_extended_figure_1(
    monte_carlo_dir: Path, output_dir: Path
) -> None:
    metric = read_csv(monte_carlo_dir / "metric-sensitivity.csv")
    constraint = read_csv(monte_carlo_dir / "constraint-sensitivity.csv")
    panels = [
        ("coverage_90", "90% interval coverage", "Coverage"),
        ("patient_crps", "Patient-macro CRPS", "CRPS"),
        ("pressure_order", "Violations per 1,000 states", "Pressure ordering"),
    ]
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(7.0866141732, FIGURE_65MM_HEIGHT_IN),  # 180 mm wide
        constrained_layout=False,
    )
    fig.subplots_adjust(
        left=0.095,
        right=0.985,
        bottom=0.245,
        top=0.70,
        wspace=0.42,
    )
    source_frames: list[pd.DataFrame] = []
    for panel_index, (axis, (quantity, ylabel, title)) in enumerate(
        zip(axes, panels, strict=True)
    ):
        add_panel_label(axis, chr(ord("a") + panel_index))
        axis.set_title(title, loc="left", pad=8)
        if quantity == "pressure_order":
            frame = constraint[
                (constraint["constraint"] == quantity)
                & (constraint["horizon_hours"].isin((12, 24)))
            ].copy()
            value_column = "violations_per_1000_states"
        else:
            frame = metric[
                (metric["metric"] == quantity)
                & (metric["horizon_hours"].isin((12, 24)))
            ].copy()
            value_column = "value"
        source_frames.append(
            frame.assign(panel_quantity=quantity, panel_value=frame[value_column])
        )
        for model in NEURAL_MODELS:
            for horizon, linestyle, marker in (
                (12, "-", "o"),
                (24, "--", "^"),
            ):
                group = frame[
                    (frame["model"] == model)
                    & (frame["horizon_hours"] == horizon)
                ].sort_values("trajectory_samples")
                axis.plot(
                    group["trajectory_samples"],
                    group[value_column],
                    color=MODEL_COLORS[model],
                    linestyle=linestyle,
                    marker=marker,
                    linewidth=1.4 if horizon == 12 else 1.15,
                    markersize=4.1,
                    alpha=1.0 if horizon == 12 else 0.86,
                    markerfacecolor=(
                        MODEL_COLORS[model] if horizon == 12 else "white"
                    ),
                    markeredgecolor=MODEL_COLORS[model],
                    markeredgewidth=0.55,
                )
        if quantity == "coverage_90":
            axis.axhline(0.90, color="#444444", linestyle=":", linewidth=0.8)
        axis.set_xticks([20, 50, 100])
        axis.set_xlabel("Trajectory samples")
        axis.set_ylabel(ylabel)
        style_axis_grid(axis, direction="y")

    model_handles = [
        Line2D(
            [0],
            [0],
            color=MODEL_COLORS[model],
            marker=MODEL_MARKERS[model],
            label=MODEL_LABELS[model],
            **style_marker(model),
        )
        for model in NEURAL_MODELS
    ]
    horizon_handles = [
        Line2D(
            [0],
            [0],
            color="#555555",
            linestyle="-",
            marker="o",
            markerfacecolor="#555555",
            label="12 h",
        ),
        Line2D(
            [0],
            [0],
            color="#555555",
            linestyle="--",
            marker="^",
            markerfacecolor="white",
            markeredgecolor="#555555",
            label="24 h",
        ),
    ]
    fig.legend(
        handles=model_handles + horizon_handles,
        loc="outside upper center",
        ncol=5,
    )
    save_figure(
        fig, output_dir / "extended-data-figure1-monte-carlo-convergence"
    )
    write_source_data(
        output_dir,
        "extended-data-figure1-monte-carlo.csv",
        pd.concat(source_frames, ignore_index=True, sort=False),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--data-summary", type=Path, required=True)
    parser.add_argument("--monte-carlo-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    configure_style()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    build_figure_1(args.data_summary, args.output_dir)
    build_figure_2(args.analysis_dir, args.output_dir)
    build_figure_3(args.analysis_dir, args.output_dir)
    build_figure_4(args.analysis_dir, args.output_dir)
    if args.monte_carlo_dir is not None:
        build_extended_figure_1(args.monte_carlo_dir, args.output_dir)
    print(
        json.dumps(
            {
                "status": "complete",
                "backend": "python-matplotlib",
                "output_dir": str(args.output_dir),
                "figures": sorted(
                    path.name
                    for path in args.output_dir.glob("*.pdf")
                    if not path.name.endswith(".collision-audit.pdf")
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
