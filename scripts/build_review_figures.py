#!/usr/bin/env python3
"""Build editable SVG review figures from frozen review artifacts."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import textwrap
from pathlib import Path


FONT = "Arial, Helvetica, sans-serif"
INK = "#222222"
MUTED = "#666666"
LINE = "#A6A6A6"
PALE = "#F2F2F2"
BLUE = "#0072B2"
LIGHT_BLUE = "#56B4E9"
GREEN = "#009E73"
ORANGE = "#E69F00"
MAGENTA = "#CC79A7"


def esc(text: object) -> str:
    return html.escape(str(text))


def text(
    x: float,
    y: float,
    value: object,
    *,
    size: int = 24,
    weight: str = "normal",
    anchor: str = "start",
    fill: str = INK,
) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" '
        f'text-anchor="{anchor}" fill="{fill}">{esc(value)}</text>'
    )


def multiline(
    x: float,
    y: float,
    value: str,
    *,
    width: int,
    size: int = 22,
    weight: str = "normal",
    anchor: str = "middle",
    fill: str = INK,
    line_height: int | None = None,
) -> str:
    lines = textwrap.wrap(value, width=width, break_long_words=False)
    line_height = line_height or int(size * 1.25)
    start_y = y - (len(lines) - 1) * line_height / 2
    tspans = "".join(
        f'<tspan x="{x}" y="{start_y + i * line_height}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<text font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">'
        f"{tspans}</text>"
    )


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str = "white",
    stroke: str = LINE,
    stroke_width: int = 2,
    radius: int = 12,
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="{radius}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}"/>'
    )


def arrow(x1: float, y1: float, x2: float, y2: float) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{MUTED}" stroke-width="3" marker-end="url(#arrow)"/>'
    )


def svg_document(width: int, height: int, content: list[str]) -> str:
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">',
            "<defs>",
            '<marker id="arrow" markerWidth="10" markerHeight="10" '
            'refX="8" refY="3" orient="auto" markerUnits="strokeWidth">',
            '<path d="M0,0 L0,6 L9,3 z" fill="#666666"/>',
            "</marker>",
            "</defs>",
            f'<rect width="{width}" height="{height}" fill="white"/>',
            *content,
            "</svg>",
            "",
        ]
    )


def build_prisma_audit(prisma: dict[str, object]) -> str:
    width, height = 1600, 1120
    parts: list[str] = []
    main_x, main_w, box_h = 475, 650, 92
    left_x, left_w = 55, 350
    right_x, right_w = 1195, 350
    ys = [45, 170, 315, 500, 650, 815, 970]
    center_x = main_x + main_w / 2

    parts.append(text(25, 90, "Identification", size=24, weight="bold"))
    parts.append(text(25, 555, "Screening", size=24, weight="bold"))
    parts.append(text(25, 865, "Included", size=24, weight="bold"))

    central = [
        (
            ys[0],
            "Records identified from public databases and repositories",
            prisma["raw_records"],
            "#EAF3F8",
        ),
        (
            ys[1],
            "Records after identifier and normalized-title deduplication",
            prisma["deduplicated_records"],
            "#EAF3F8",
        ),
        (
            ys[2],
            "Database and repository records entering title and abstract screening",
            prisma.get(
                "database_title_abstract_records",
                prisma["unique_title_abstract_records"],
            ),
            "white",
        ),
        (
            ys[3],
            "Unique title and abstract decisions across all screened routes",
            prisma["unique_title_abstract_records"],
            "white",
        ),
        (
            ys[4],
            "Full texts assessed for eligibility",
            prisma["full_texts_assessed"],
            "white",
        ),
        (
            ys[5],
            "Publications included after full-text assessment and lineage resolution",
            prisma["included_total"],
            "#E8F5EF",
        ),
    ]
    for index, (y, label, count, fill) in enumerate(central):
        parts.append(rect(main_x, y, main_w, box_h, fill=fill))
        parts.append(
            multiline(
                center_x,
                y + 35,
                label,
                width=52,
                size=21,
                weight="bold",
            )
        )
        parts.append(
            text(center_x, y + 72, f"n = {count:,}", size=21, anchor="middle")
        )
        if index < len(central) - 1:
            parts.append(arrow(center_x, y + box_h, center_x, central[index + 1][0]))

    parts.append(rect(right_x, ys[1], right_w, 120, fill="#EAF3F8", stroke=BLUE))
    parts.append(
        multiline(
            right_x + right_w / 2,
            ys[1] + 34,
            "Fresh alternate-term records after deduplication",
            width=29,
            size=19,
            weight="bold",
        )
    )
    parts.append(
        text(
            right_x + right_w / 2,
            ys[1] + 82,
            f"n = {prisma.get('fresh_alternate_search_unique_records', 0):,}",
            size=20,
            anchor="middle",
        )
    )
    parts.append(
        text(
            right_x + right_w / 2,
            ys[1] + 108,
            "added to the corrected screening pool",
            size=16,
            anchor="middle",
            fill=MUTED,
        )
    )
    parts.append(arrow(right_x, ys[1] + 60, main_x + main_w, ys[2] + 46))

    routes = prisma.get("screening_routes", {})
    if routes:
        audit_n = int(
            routes["sampled_discovery_filter_audit"]["title_abstract_records"]
        )
        alternate_primary_n = (
            int(routes["expanded_alternate_term_search"]["title_abstract_records"])
            - int(prisma.get("fresh_alternate_search_unique_records", 0))
        )
        residual_n = int(
            routes["exhaustive_residual_filter_rescreen"][
                "title_abstract_records"
            ]
        )
        parts.append(rect(right_x, ys[2] + 5, right_w, 125, fill="#FFF4E5", stroke=ORANGE))
        parts.append(
            multiline(
                right_x + right_w / 2,
                ys[2] + 38,
                "All primary-search filter exclusions re-screened",
                width=29,
                size=19,
                weight="bold",
            )
        )
        parts.append(
            text(
                right_x + right_w / 2,
                ys[2] + 82,
                f"audit {audit_n:,} • alternate subset {alternate_primary_n:,}",
                size=17,
                anchor="middle",
            )
        )
        parts.append(
            text(
                right_x + right_w / 2,
                ys[2] + 111,
                f"exhaustive residual {residual_n:,}",
                size=17,
                anchor="middle",
                fill=MUTED,
            )
        )

    parts.append(rect(left_x, ys[2] + 5, left_w, 125, fill="#EAF3F8", stroke=BLUE))
    parts.append(
        multiline(
            left_x + left_w / 2,
            ys[2] + 34,
            "Citation-chasing records assessed",
            width=28,
            size=19,
            weight="bold",
        )
    )
    parts.append(
        text(
            left_x + left_w / 2,
            ys[2] + 76,
            f"n = {prisma['citation_chasing_records_assessed']:,}",
            size=20,
            anchor="middle",
        )
    )
    parts.append(
        text(
            left_x + left_w / 2,
            ys[2] + 105,
            (
                f"{prisma['citation_chasing_database_duplicates']} database "
                f"duplicates; {prisma['unique_citation_chasing_additions']} unique"
            ),
            size=15,
            anchor="middle",
            fill=MUTED,
        )
    )
    parts.append(arrow(left_x + left_w, ys[2] + 67, main_x, ys[3] + 46))

    parts.append(rect(right_x, ys[3] + 5, right_w, 100, fill=PALE))
    parts.append(
        multiline(
            right_x + right_w / 2,
            ys[3] + 38,
            "Excluded after title and abstract assessment",
            width=30,
            size=19,
            weight="bold",
        )
    )
    parts.append(
        text(
            right_x + right_w / 2,
            ys[3] + 82,
            f"n = {prisma['title_abstract_exclusions']:,}",
            size=20,
            anchor="middle",
        )
    )
    parts.append(arrow(main_x + main_w, ys[3] + 46, right_x, ys[3] + 46))

    parts.append(rect(right_x, ys[4] - 5, right_w, 190, fill=PALE))
    parts.append(
        text(
            right_x + right_w / 2,
            ys[4] + 22,
            f"Full texts excluded, n = {prisma['full_text_exclusions']:,}",
            size=19,
            weight="bold",
            anchor="middle",
        )
    )
    if routes:
        route_labels = [
            ("initial_search_and_citation_chasing", "Initial route"),
            ("sampled_discovery_filter_audit", "Filter audit"),
            ("expanded_alternate_term_search", "Alternate-term route"),
            ("exhaustive_residual_filter_rescreen", "Residual rescreen"),
        ]
        for index, (key, label) in enumerate(route_labels):
            parts.append(
                text(
                    right_x + 20,
                    ys[4] + 58 + index * 29,
                    (
                        f"{label}: "
                        f"{int(routes[key]['full_text_exclusions']):,}"
                    ),
                    size=16,
                )
            )
    parts.append(arrow(main_x + main_w, ys[4] + 46, right_x, ys[4] + 46))

    child_w = 300
    gap = 50
    left_child_x = center_x - child_w - gap / 2
    right_child_x = center_x + gap / 2
    for x, label, count in [
        (
            left_child_x,
            "Empirical studies (primary strict core: 82)",
            prisma["included_empirical"],
        ),
        (right_child_x, "Core review articles", prisma["included_reviews"]),
    ]:
        parts.append(rect(x, ys[6], child_w, 100, fill="#E8F5EF", stroke=GREEN))
        parts.append(
            multiline(
                x + child_w / 2,
                ys[6] + 35,
                label,
                width=25,
                size=20,
                weight="bold",
            )
        )
        parts.append(
            text(
                x + child_w / 2,
                ys[6] + 76,
                f"n = {count:,}",
                size=20,
                anchor="middle",
            )
        )
    branch_y = ys[6] - 28
    parts.append(
        f'<line x1="{center_x}" y1="{ys[5] + box_h}" '
        f'x2="{center_x}" y2="{branch_y}" stroke="{MUTED}" stroke-width="3"/>'
    )
    parts.append(
        f'<line x1="{left_child_x + child_w / 2}" y1="{branch_y}" '
        f'x2="{right_child_x + child_w / 2}" y2="{branch_y}" '
        f'stroke="{MUTED}" stroke-width="3"/>'
    )
    parts.append(arrow(left_child_x + child_w / 2, branch_y, left_child_x + child_w / 2, ys[6]))
    parts.append(arrow(right_child_x + child_w / 2, branch_y, right_child_x + child_w / 2, ys[6]))
    parts.append(
        text(
            1560,
            1100,
            "Detailed route arithmetic and quality-control history are reported in the Supplement",
            size=16,
            anchor="end",
            fill=MUTED,
        )
    )
    return svg_document(width, height, parts)


def build_prisma(prisma: dict[str, object]) -> str:
    """Build the reader-facing main-paper flow; retain route detail in Supplement."""
    width, height = 1500, 1020
    parts: list[str] = []
    main_x, main_w = 360, 650
    right_x, right_w = 1070, 360
    box_h = 105
    center_x = main_x + main_w / 2
    y_identified, y_screened, y_fulltext, y_included, y_children = (
        55,
        245,
        455,
        665,
        855,
    )

    parts.append(text(28, 105, "Identification", size=25, weight="bold"))
    parts.append(text(28, 320, "Screening", size=25, weight="bold"))
    parts.append(text(28, 720, "Included", size=25, weight="bold"))

    parts.append(rect(main_x, y_identified, main_w, 135, fill="#EAF3F8"))
    parts.append(
        multiline(
            center_x,
            y_identified + 38,
            "Records identified across public search routes",
            width=48,
            size=23,
            weight="bold",
        )
    )
    parts.append(
        text(
            center_x,
            y_identified + 83,
            (
                f"initial databases/repositories {int(prisma['raw_records']):,}  •  "
                f"fresh alternate-term records "
                f"{int(prisma.get('fresh_alternate_search_unique_records', 0)):,}"
            ),
            size=18,
            anchor="middle",
        )
    )
    parts.append(
        text(
            center_x,
            y_identified + 112,
            (
                "citation-chasing records assessed "
                f"{int(prisma['citation_chasing_records_assessed']):,}"
            ),
            size=17,
            anchor="middle",
            fill=MUTED,
        )
    )

    parts.append(rect(main_x, y_screened, main_w, box_h))
    parts.append(
        multiline(
            center_x,
            y_screened + 38,
            "Unique records screened after cross-route deduplication",
            width=48,
            size=22,
            weight="bold",
        )
    )
    parts.append(
        text(
            center_x,
            y_screened + 79,
            f"n = {int(prisma['unique_title_abstract_records']):,}",
            size=21,
            anchor="middle",
        )
    )
    parts.append(rect(right_x, y_screened, right_w, box_h, fill=PALE))
    parts.append(
        multiline(
            right_x + right_w / 2,
            y_screened + 38,
            "Excluded after title and abstract assessment",
            width=30,
            size=20,
            weight="bold",
        )
    )
    parts.append(
        text(
            right_x + right_w / 2,
            y_screened + 79,
            f"n = {int(prisma['title_abstract_exclusions']):,}",
            size=20,
            anchor="middle",
        )
    )

    parts.append(rect(main_x, y_fulltext, main_w, box_h))
    parts.append(
        multiline(
            center_x,
            y_fulltext + 38,
            "Full texts assessed for eligibility",
            width=48,
            size=22,
            weight="bold",
        )
    )
    parts.append(
        text(
            center_x,
            y_fulltext + 79,
            f"n = {int(prisma['full_texts_assessed']):,}",
            size=21,
            anchor="middle",
        )
    )
    parts.append(rect(right_x, y_fulltext, right_w, box_h, fill=PALE))
    parts.append(
        multiline(
            right_x + right_w / 2,
            y_fulltext + 38,
            "Full texts excluded",
            width=30,
            size=20,
            weight="bold",
        )
    )
    parts.append(
        text(
            right_x + right_w / 2,
            y_fulltext + 79,
            f"n = {int(prisma['full_text_exclusions']):,}",
            size=20,
            anchor="middle",
        )
    )

    parts.append(rect(main_x, y_included, main_w, box_h, fill="#E8F5EF"))
    parts.append(
        multiline(
            center_x,
            y_included + 38,
            "Publications included after lineage resolution",
            width=48,
            size=22,
            weight="bold",
        )
    )
    parts.append(
        text(
            center_x,
            y_included + 79,
            f"n = {int(prisma['included_total']):,}",
            size=21,
            anchor="middle",
        )
    )

    for y1, y2 in [
        (y_identified + 135, y_screened),
        (y_screened + box_h, y_fulltext),
        (y_fulltext + box_h, y_included),
    ]:
        parts.append(arrow(center_x, y1, center_x, y2))
    parts.append(
        arrow(
            main_x + main_w,
            y_screened + box_h / 2,
            right_x,
            y_screened + box_h / 2,
        )
    )
    parts.append(
        arrow(
            main_x + main_w,
            y_fulltext + box_h / 2,
            right_x,
            y_fulltext + box_h / 2,
        )
    )

    child_w = 310
    gap = 30
    left_child_x = center_x - child_w - gap / 2
    right_child_x = center_x + gap / 2
    children = [
        (
            left_child_x,
            "Empirical publications",
            int(prisma["included_empirical"]),
            "Primary strict clinical/biomedical set: n = 82; boundary set: n = 3",
        ),
        (
            right_child_x,
            "Review articles",
            int(prisma["included_reviews"]),
            "Used for field definition and comparison",
        ),
    ]
    for x, label, count, note in children:
        parts.append(rect(x, y_children, child_w, 120, fill="#E8F5EF", stroke=GREEN))
        parts.append(
            text(
                x + child_w / 2,
                y_children + 35,
                label,
                size=20,
                weight="bold",
                anchor="middle",
            )
        )
        parts.append(
            text(
                x + child_w / 2,
                y_children + 70,
                f"n = {count:,}",
                size=20,
                anchor="middle",
            )
        )
        parts.append(
            multiline(
                x + child_w / 2,
                y_children + 101,
                note,
                width=41,
                size=14,
                anchor="middle",
                fill=MUTED,
            )
        )

    branch_y = y_children - 35
    parts.append(
        f'<line x1="{center_x}" y1="{y_included + box_h}" '
        f'x2="{center_x}" y2="{branch_y}" stroke="{MUTED}" stroke-width="3"/>'
    )
    parts.append(
        f'<line x1="{left_child_x + child_w / 2}" y1="{branch_y}" '
        f'x2="{right_child_x + child_w / 2}" y2="{branch_y}" '
        f'stroke="{MUTED}" stroke-width="3"/>'
    )
    parts.append(
        arrow(
            left_child_x + child_w / 2,
            branch_y,
            left_child_x + child_w / 2,
            y_children,
        )
    )
    parts.append(
        arrow(
            right_child_x + child_w / 2,
            branch_y,
            right_child_x + child_w / 2,
            y_children,
        )
    )
    parts.append(
        text(
            1460,
            1005,
            "Detailed route arithmetic and quality-control history are reported in the Supplement",
            size=15,
            anchor="end",
            fill=MUTED,
        )
    )
    return svg_document(width, height, parts)


def build_evidence(summary: dict[str, object]) -> str:
    width, height = 1500, 820
    parts: list[str] = []
    capabilities = summary["capability_claims"]
    features = summary["descriptive_features"]
    joints = summary["joint_evidence_intersections"]
    ordinal = summary["ordinal_evidence_domains"]
    total = int(summary["records"])

    panel_x = [70, 540, 1050]
    panel_w = [390, 430, 380]
    parts.append(text(panel_x[0], 52, "(a) Highest capability claim", size=26, weight="bold"))
    parts.append(text(panel_x[1], 52, "(b) Corpus-wide reported evidence", size=26, weight="bold"))
    parts.append(text(panel_x[2], 52, "(c) Closed-loop setting", size=26, weight="bold"))

    cap_rows = [
        ("Planning", capabilities["planning"], BLUE),
        ("Action-conditioned", capabilities["action_conditioned"], LIGHT_BLUE),
        ("Counterfactual", capabilities["counterfactual"], ORANGE),
        ("Passive forecasting", capabilities["passive_forecasting"], GREEN),
    ]
    max_cap = max(int(count) for _, count, _ in cap_rows)
    for i, (label, count, color) in enumerate(cap_rows):
        y = 118 + i * 118
        parts.append(text(panel_x[0], y, label, size=22, weight="bold"))
        parts.append(rect(panel_x[0], y + 20, 330, 34, fill=PALE, stroke=PALE, radius=5))
        parts.append(
            rect(
                panel_x[0],
                y + 20,
                330 * count / max_cap,
                34,
                fill=color,
                stroke=color,
                radius=5,
            )
        )
        parts.append(
            text(
                panel_x[0] + 345,
                y + 47,
                f"{count}/{total}",
                size=22,
                weight="bold",
            )
        )
    parts.append(
        text(
            panel_x[0],
            640,
            "Claims describe the highest stated capability,",
            size=17,
            fill=MUTED,
        )
    )
    parts.append(
        text(
            panel_x[0],
            665,
            "not the level demonstrated by the evidence.",
            size=17,
            fill=MUTED,
        )
    )

    causal_distribution = ordinal["causal_evidence"]
    causal_strong = int(causal_distribution.get("2", 0))
    causal_applicable = total - int(causal_distribution.get("NA", 0))
    feature_rows = [
        (
            "Directly auditable causal evidence",
            causal_strong,
            causal_applicable,
            MAGENTA,
            f"{int(causal_distribution.get('NA', 0))} not applicable",
        ),
        (
            "Formal calibration",
            features["formal_calibration"]["yes"],
            features["formal_calibration"]["total_denominator"],
            BLUE,
            "",
        ),
        (
            "Frozen external validation",
            features["frozen_external_validation"]["yes"],
            features["frozen_external_validation"]["total_denominator"],
            BLUE,
            (
                f"{features['frozen_external_validation']['distribution'].get('unclear', 0)} "
                "unclear"
            ),
        ),
        (
            "Free rollout + horizon + calibration",
            joints["rollout_horizon_calibration"]["yes"],
            joints["rollout_horizon_calibration"]["total_denominator"],
            BLUE,
            "",
        ),
        (
            "Free rollout + horizon + external",
            joints["rollout_horizon_external"]["yes"],
            joints["rollout_horizon_external"]["total_denominator"],
            BLUE,
            "",
        ),
        (
            "Four-item reporting intersection",
            joints["rollout_horizon_calibration_external"]["yes"],
            joints["rollout_horizon_calibration_external"]["total_denominator"],
            MAGENTA,
            "rollout + horizon + calibration + external validation",
        ),
    ]
    feature_bar_w = 300
    for i, (label, count, denominator, color, note) in enumerate(feature_rows):
        y = 102 + i * 83
        percent = 100 * count / denominator
        parts.append(text(panel_x[1], y, label, size=19, weight="bold"))
        parts.append(
            rect(
                panel_x[1],
                y + 15,
                feature_bar_w,
                24,
                fill=PALE,
                stroke=PALE,
                radius=4,
            )
        )
        if count:
            parts.append(
                rect(
                    panel_x[1],
                    y + 15,
                    feature_bar_w * percent / 100,
                    24,
                    fill=color,
                    stroke=color,
                    radius=4,
                )
            )
        parts.append(
            text(
                panel_x[1] + feature_bar_w + 14,
                y + 30,
                f"{count}/{denominator} ({percent:.0f}%)",
                size=18,
                weight="bold",
            )
        )
        if note:
            parts.append(
                text(
                    panel_x[1] + feature_bar_w + 14,
                    y + 51,
                    note,
                    size=14,
                    fill=MUTED,
                )
            )
    parts.append(
        text(
            panel_x[1],
            720,
            "Reporting bars use displayed denominators; applicability differs.",
            size=17,
            fill=MUTED,
        )
    )

    closed = features["closed_loop_evaluation"]["distribution"]
    loop_rows = [
        ("No closed loop", closed["no"], "#A6A6A6"),
        ("Offline decision evaluation", closed["offline"], LIGHT_BLUE),
        ("Simulation closed loop", closed["simulation"], ORANGE),
        ("Real-system closed loop", closed["real"], GREEN),
    ]
    for i, (label, count, color) in enumerate(loop_rows):
        y = 120 + i * 120
        parts.append(text(panel_x[2], y, label, size=21, weight="bold"))
        parts.append(rect(panel_x[2], y + 20, 270, 32, fill=PALE, stroke=PALE, radius=5))
        parts.append(
            rect(
                panel_x[2],
                y + 20,
                270 * count / max(int(item[1]) for item in loop_rows),
                32,
                fill=color,
                stroke=color,
                radius=5,
            )
        )
        parts.append(
            text(
                panel_x[2] + 285,
                y + 45,
                f"{count}/{total}",
                size=21,
                weight="bold",
            )
        )
    parts.append(
        multiline(
            panel_x[2],
            650,
            "Offline, simulated, and real-system evaluations test different validity claims.",
            width=38,
            size=18,
            anchor="start",
            fill=MUTED,
        )
    )
    parts.append(
        text(
            1450,
            790,
            f"Primary strict clinical and biomedical corpus, n = {total}",
            size=16,
            anchor="end",
            fill=MUTED,
        )
    )
    return svg_document(width, height, parts)


def heat_color(rate: float | None) -> tuple[str, str]:
    if rate is None:
        return "#FFFFFF", MUTED
    if rate == 0:
        return "#F2F2F2", INK
    if rate <= 0.25:
        return "#D7ECF7", INK
    if rate <= 0.5:
        return LIGHT_BLUE, INK
    if rate <= 0.75:
        return BLUE, "white"
    return "#005580", "white"


def build_capability_domain_heatmap(sensitivity: dict[str, object]) -> str:
    width, height = 1700, 1040
    parts: list[str] = []
    parts.append(
        text(
            60,
            56,
            "(a) Strongest MedWM-Eval evidence level by stated capability",
            size=27,
            weight="bold",
        )
    )
    capability_order = [
        ("planning", "Planning"),
        ("counterfactual", "Counterfactual"),
        ("action_conditioned", "Action-conditioned"),
        ("passive_forecasting", "Passive forecasting"),
    ]
    evidence_order = [
        ("rollout_evidence", "Rollout"),
        ("action_evidence", "Action"),
        ("uncertainty_evidence", "Uncertainty"),
        ("causal_evidence", "Causal"),
        ("external_evidence", "External"),
        ("decision_evidence", "Decision"),
        ("safety_evidence", "Safety"),
    ]
    cap_data = sensitivity["capability_by_evidence"]
    x0, y0 = 360, 115
    cell_w, cell_h = 165, 95
    for column, (_, label) in enumerate(evidence_order):
        parts.append(
            multiline(
                x0 + column * cell_w + cell_w / 2,
                y0 - 28,
                label,
                width=14,
                size=19,
                weight="bold",
            )
        )
    for row_index, (key, label) in enumerate(capability_order):
        item = cap_data[key]
        y = y0 + row_index * cell_h
        parts.append(
            text(
                x0 - 24,
                y + 46,
                f"{label} (n={item['records']})",
                size=20,
                weight="bold",
                anchor="end",
            )
        )
        for column, (field, _) in enumerate(evidence_order):
            evidence = item["ordinal"][field]
            denominator = int(evidence["applicable"])
            strong = int(evidence["strong"])
            rate = strong / denominator if denominator else None
            fill, ink = heat_color(rate)
            x = x0 + column * cell_w
            parts.append(
                rect(
                    x,
                    y,
                    cell_w - 8,
                    cell_h - 8,
                    fill=fill,
                    stroke="white",
                    stroke_width=2,
                    radius=4,
                )
            )
            label_text = (
                "NA"
                if denominator == 0
                else f"{strong}/{denominator}{'*' if denominator < 5 else ''}"
            )
            parts.append(
                text(
                    x + (cell_w - 8) / 2,
                    y + 42,
                    label_text,
                    size=23,
                    weight="bold",
                    anchor="middle",
                    fill=ink,
                )
            )
            if denominator:
                parts.append(
                    text(
                        x + (cell_w - 8) / 2,
                        y + 68,
                        f"{100 * rate:.0f}%",
                        size=16,
                        anchor="middle",
                        fill=ink,
                    )
                )
    parts.append(
        text(
            60,
            530,
            "(b) Selected reported evidence by domain",
            size=27,
            weight="bold",
        )
    )
    domain_order = [
        ("longitudinal_physiology_decision", "Longitudinal / physiology / decision"),
        ("imaging_biological", "Imaging / biological"),
        ("procedural_embodied", "Procedural / embodied"),
    ]
    feature_order = [
        ("free_running_rollout", "Free rollout"),
        ("horizon_resolved_results", "Horizon results"),
        ("formal_calibration", "Calibration"),
        ("frozen_external_validation", "External validation"),
        ("explicit_causal_estimand", "Causal estimand"),
        ("safety_hazard_test", "Safety test"),
    ]
    domain_data = sensitivity["domain_by_evidence"]
    x1, y1 = 430, 610
    cell_w2, cell_h2 = 190, 88
    for column, (_, label) in enumerate(feature_order):
        parts.append(
            multiline(
                x1 + column * cell_w2 + cell_w2 / 2,
                y1 - 31,
                label,
                width=16,
                size=18,
                weight="bold",
            )
        )
    for row_index, (key, label) in enumerate(domain_order):
        item = domain_data[key]
        y = y1 + row_index * cell_h2
        parts.append(
            text(
                x1 - 24,
                y + 44,
                f"{label} (n={item['records']})",
                size=19,
                weight="bold",
                anchor="end",
            )
        )
        for column, (field, _) in enumerate(feature_order):
            evidence = item["features"][field]
            yes = int(evidence["yes"])
            denominator = int(item["records"])
            rate = yes / denominator if denominator else None
            fill, ink = heat_color(rate)
            x = x1 + column * cell_w2
            parts.append(
                rect(
                    x,
                    y,
                    cell_w2 - 8,
                    cell_h2 - 8,
                    fill=fill,
                    stroke="white",
                    stroke_width=2,
                    radius=4,
                )
            )
            parts.append(
                text(
                    x + (cell_w2 - 8) / 2,
                    y + 39,
                    f"{yes}/{denominator}",
                    size=22,
                    weight="bold",
                    anchor="middle",
                    fill=ink,
                )
            )
            parts.append(
                text(
                    x + (cell_w2 - 8) / 2,
                    y + 64,
                    f"{100 * rate:.0f}%",
                    size=15,
                    anchor="middle",
                    fill=ink,
                )
            )
    legend_x = 1260
    parts.append(
        text(
            60,
            995,
            "* Applicable denominator below five; compare cautiously.",
            size=15,
            fill=MUTED,
        )
    )
    parts.append(text(legend_x, 960, "Cell shading", size=17, weight="bold"))
    for index, (label, rate) in enumerate(
        [("0%", 0), ("1-25%", 0.2), ("26-50%", 0.4), ("51-75%", 0.65), (">75%", 0.9)]
    ):
        fill, ink = heat_color(rate)
        x = legend_x + index * 80
        parts.append(rect(x, 977, 70, 28, fill=fill, stroke="white", radius=2))
        parts.append(text(x + 35, 997, label, size=12, anchor="middle", fill=ink))
    total = int(sensitivity["subsets"]["strict_core"]["records"])
    parts.append(
        text(
            1650,
            1022,
            f"Counts use the {total}-study strict clinical and biomedical corpus",
            size=15,
            anchor="end",
            fill=MUTED,
        )
    )
    return svg_document(width, height, parts)


def build_graphical_abstract() -> str:
    width, height = 2000, 800
    parts: list[str] = []
    parts.append(
        text(
            width / 2,
            52,
            "Medical world model claims require capability-matched evidence",
            size=32,
            weight="bold",
            anchor="middle",
        )
    )
    parts.append(
        text(
            250,
            102,
            "Claim",
            size=24,
            weight="bold",
            anchor="middle",
            fill=MUTED,
        )
    )
    parts.append(
        text(
            950,
            102,
            "Proposed evidence considerations",
            size=24,
            weight="bold",
            anchor="middle",
            fill=MUTED,
        )
    )
    parts.append(
        text(
            1700,
            102,
            "Interpretation, if assumptions hold",
            size=24,
            weight="bold",
            anchor="middle",
            fill=MUTED,
        )
    )

    rows = [
        (
            "Passive forecasting",
            "State fidelity • rollout stability • calibration by horizon",
            "Forecast under the observed process",
            GREEN,
        ),
        (
            "Action-conditioned simulation",
            "Defined action • action-agnostic comparator • action perturbation",
            "Response to an in-support action",
            LIGHT_BLUE,
        ),
        (
            "Counterfactual comparison",
            "Estimand • confounding and overlap • counterfactual validation",
            "Alternative treatment or policy contrast",
            ORANGE,
        ),
        (
            "Closed-loop planning",
            "Decision utility • causal design when clinical • mismatch, safety, external validity",
            "Sequential decisions within validated scope",
            BLUE,
        ),
    ]
    row_y = [125, 250, 375, 500]
    for i, (claim, evidence, interpretation, color) in enumerate(rows):
        y = row_y[i]
        parts.append(
            rect(
                55,
                y,
                390,
                94,
                fill=color,
                stroke=color,
                radius=16,
            )
        )
        parts.append(
            multiline(
                250,
                y + 51,
                claim,
                width=29,
                size=22,
                weight="bold",
                fill="white",
            )
        )
        parts.append(arrow(445, y + 47, 545, y + 47))
        parts.append(rect(545, y, 810, 94, fill="white", stroke=color, radius=16))
        parts.append(
            multiline(
                950,
                y + 51,
                evidence,
                width=71,
                size=22,
                weight="bold",
            )
        )
        parts.append(arrow(1355, y + 47, 1455, y + 47))
        parts.append(
            rect(
                1455,
                y,
                490,
                94,
                fill="#F7F7F7",
                stroke=color,
                radius=16,
            )
        )
        parts.append(
            multiline(
                1700,
                y + 51,
                interpretation,
                width=42,
                size=21,
                weight="bold",
            )
        )

    parts.append(
        rect(
            400,
            650,
            1200,
            66,
            fill="#EAF3F8",
            stroke=BLUE,
            radius=14,
        )
    )
    parts.append(
        text(
            1000,
            692,
            "Descriptive gap: calibrated free rollout with frozen external validation",
            size=24,
            weight="bold",
            anchor="middle",
            fill=BLUE,
        )
    )
    parts.append(
        text(
            1940,
            780,
            "MedWM-Eval",
            size=16,
            anchor="end",
            fill=MUTED,
        )
    )
    return svg_document(width, height, parts)


def export(svg_path: Path, png_path: Path, pdf_path: Path) -> None:
    subprocess.run(
        [
            "/opt/homebrew/bin/rsvg-convert",
            "--format=png",
            "--width=2400",
            "--output",
            str(png_path),
            str(svg_path),
        ],
        check=True,
    )
    subprocess.run(
        [
            "/opt/homebrew/bin/rsvg-convert",
            "--format=pdf",
            "--output",
            str(pdf_path),
            str(svg_path),
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prisma", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--sensitivity", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    prisma = json.loads(args.prisma.read_text(encoding="utf-8"))
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    sensitivity = json.loads(args.sensitivity.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = [
        (
            "figure1-prisma-flow",
            build_prisma(prisma),
        ),
        (
            "figure2-evidence-map",
            build_evidence(summary),
        ),
        (
            "figure3-capability-domain-heatmap",
            build_capability_domain_heatmap(sensitivity),
        ),
        (
            "graphical-abstract",
            build_graphical_abstract(),
        ),
    ]
    for stem, svg in artifacts:
        svg_path = args.output_dir / f"{stem}.svg"
        png_path = args.output_dir / f"{stem}.png"
        pdf_path = args.output_dir / f"{stem}.pdf"
        svg_path.write_text(svg, encoding="utf-8")
        export(svg_path, png_path, pdf_path)
        print(f"Wrote {svg_path}, {png_path}, and {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
