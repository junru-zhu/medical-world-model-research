#!/usr/bin/env python3
"""Validate the review development snapshot and its supporting artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import struct
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def expand_citations(body: str) -> set[int]:
    numbers: set[int] = set()
    for match in re.finditer(r"\[([0-9,\-– ]+)\]", body):
        for item in match.group(1).replace("–", "-").split(","):
            item = item.strip()
            if not item:
                continue
            if "-" in item:
                start_text, end_text = item.split("-", 1)
                numbers.update(range(int(start_text), int(end_text) + 1))
            else:
                numbers.add(int(item))
    return numbers


def words(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text))


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")
    return struct.unpack(">II", header[16:24])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("submission/review-validation.json"),
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    final_dir = (
        root / "output/literature-search/medical-world-models/final-corpus"
    )
    included = read_csv(final_dir / "included.csv")
    extraction = read_csv(final_dir / "study-extraction.csv")
    pilot = read_csv(final_dir / "medwm-eval-final.csv")
    summary = json.loads(
        (final_dir / "medwm-eval-summary.json").read_text(encoding="utf-8")
    )
    strict_summary = json.loads(
        (final_dir / "medwm-eval-summary-strict.json").read_text(
            encoding="utf-8"
        )
    )
    flow = json.loads(
        (
            root
            / "output/literature-search/medical-world-models/screening/"
            "prisma-flow-data.json"
        ).read_text(encoding="utf-8")
    )
    reference_map = json.loads(
        (final_dir / "included-reference-map.json").read_text(encoding="utf-8")
    )
    manuscript = (root / "manuscript/review.md").read_text(encoding="utf-8")
    body, references = manuscript.split("## References", 1)
    abstract = body.split("## Abstract", 1)[1].split(
        "## Statement of Significance", 1
    )[0]

    checks: dict[str, object] = {}
    empirical_ids = {
        row["candidate_id"]
        for row in included
        if row["final_corpus_type"] == "empirical"
    }
    review_ids = {
        row["candidate_id"]
        for row in included
        if row["final_corpus_type"] == "review"
    }
    extraction_ids = {row["candidate_id"] for row in extraction}
    pilot_ids = {row["candidate_id"] for row in pilot}
    checks["corpus_counts"] = {
        "pass": (
            len(included) == len(empirical_ids) + len(review_ids)
            and flow["included_total"] == len(included)
            and flow["included_empirical"] == len(empirical_ids)
            and flow["included_reviews"] == len(review_ids)
            and flow["full_texts_assessed"]
            == flow["included_total"] + flow["full_text_exclusions"]
        ),
        "included_total": len(included),
        "empirical": len(empirical_ids),
        "reviews": len(review_ids),
    }
    checks["empirical_id_alignment"] = {
        "pass": empirical_ids == extraction_ids == pilot_ids,
        "extraction_records": len(extraction_ids),
        "pilot_records": len(pilot_ids),
    }
    checks["pilot_summary"] = {
        "pass": (
            summary["records"] == len(empirical_ids)
            and sum(summary["capability_claims"].values()) == len(empirical_ids)
            and strict_summary["records"] == 82
            and strict_summary["corpus_boundary"] == "strict_core"
            and sum(strict_summary["capability_claims"].values())
            == strict_summary["records"]
        ),
        "records": summary["records"],
        "capability_claims": summary["capability_claims"],
        "primary_records": strict_summary["records"],
        "primary_capability_claims": strict_summary["capability_claims"],
        "primary_joint_evidence": strict_summary[
            "joint_evidence_intersections"
        ],
    }

    reference_numbers = [
        int(match.group(1))
        for match in re.finditer(r"(?m)^(\d+)\.", references)
    ]
    cited_numbers = expand_citations(body)
    reference_set = set(reference_numbers)
    checks["references"] = {
        "pass": (
            len(reference_map) == len(included)
            and reference_numbers
            == list(range(1, len(included) + 7 + 1))
            and cited_numbers == reference_set
        ),
        "included_references": len(reference_map),
        "total_references": len(reference_numbers),
        "highest_citation": max(cited_numbers),
        "uncited_references": sorted(reference_set - cited_numbers),
        "unknown_citations": sorted(cited_numbers - reference_set),
    }

    figure_paths = [
        root / f"figures/review/{stem}.{extension}"
        for stem in [
            "figure1-prisma-flow",
            "figure2-evidence-map",
            "figure3-capability-domain-heatmap",
            "graphical-abstract",
        ]
        for extension in ["svg", "pdf", "png"]
    ]
    checks["figures"] = {
        "pass": all(path.is_file() and path.stat().st_size > 0 for path in figure_paths),
        "files": [str(path.relative_to(root)) for path in figure_paths],
    }
    graphical_png = root / "figures/review/graphical-abstract.png"
    graphical_width, graphical_height = png_dimensions(graphical_png)
    checks["graphical_abstract"] = {
        "pass": graphical_width >= 1328 and graphical_height >= 531,
        "width_pixels": graphical_width,
        "height_pixels": graphical_height,
        "aspect_ratio": graphical_width / graphical_height,
        "journal_minimum": "1328 x 531 pixels or proportionally larger",
    }
    analysis_paths = [
        final_dir / "analysis/analysis-annotations.csv",
        final_dir / "analysis/claim-provenance-audit.csv",
        final_dir / "analysis/claim-provenance-summary.json",
        final_dir / "analysis/methodological-appraisal.csv",
        final_dir / "analysis/methodological-appraisal.json",
        final_dir / "analysis/methodological-appraisal.md",
        final_dir / "analysis/review-sensitivity-analysis.json",
        final_dir / "analysis/applicability-joint-gap.csv",
        final_dir / "analysis/study-characteristics.csv",
    ]
    checks["analysis_artifacts"] = {
        "pass": all(
            path.is_file() and path.stat().st_size > 0
            for path in analysis_paths
        ),
        "files": [str(path.relative_to(root)) for path in analysis_paths],
    }
    table_count = sum(
        1 for line in body.splitlines() if line.startswith("| ---")
    )
    figure_count = len(re.findall(r"!\[[^\]]+\]\([^)]+\)", body))
    checks["venue_budget"] = {
        "pass": (
            words(abstract) <= 350
            and words(body) <= 6000
            and table_count + figure_count <= 8
        ),
        "abstract_words": words(abstract),
        "body_words": words(body),
        "tables": table_count,
        "figures": figure_count,
        "combined_figures_tables": table_count + figure_count,
        "limits_status": (
            "verified against the Journal of Biomedical Informatics "
            "Guide for Authors on 2026-09-12"
        ),
    }
    capabilities = strict_summary["capability_claims"]
    required_text = [
        f"{len(empirical_ids)} empirical studies",
        f"{len(review_ids)} reviews",
        f"{strict_summary['records']}-study primary",
        f"planning ({capabilities['planning']})",
        (
            "action-conditioned simulation "
            f"({capabilities['action_conditioned']})"
        ),
        f"counterfactual comparison ({capabilities['counterfactual']})",
        f"passive forecasting ({capabilities['passive_forecasting']})",
        (
            "corpus-wide four-feature reporting intersection was 0/82"
            if strict_summary["joint_evidence_intersections"][
                "rollout_horizon_calibration_external"
            ]["yes"]
            == 0
            else ""
        ),
    ]
    checks["manuscript_count_strings"] = {
        "pass": all(item in manuscript for item in required_text),
        "required": required_text,
    }
    required_ai_heading = (
        "## Declaration of Generative AI and AI-assisted technologies "
        "in the writing process"
    )
    checks["generative_ai_declaration"] = {
        "pass": (
            required_ai_heading in manuscript
            and "OpenAI Codex" in manuscript
            and "take full responsibility" in manuscript
        ),
        "required_heading": required_ai_heading,
    }

    screening_root = (
        root / "output/literature-search/medical-world-models/screening"
    )
    correction_paths = {
        "discovery_filter_audit": (
            screening_root / "discovery-filter-audit/resolved-final/summary.json"
        ),
        "expanded_alternate_search": (
            screening_root
            / "expanded-search-screening/resolved-final/summary.json"
        ),
        "exhaustive_filter_rescreen": (
            screening_root
            / "exhaustive-exclusion-rescreen/resolved-final/summary.json"
        ),
    }
    correction_status: dict[str, str] = {}
    for name, path in correction_paths.items():
        if path.is_file():
            correction_status[name] = "complete"
            continue
        if name == "discovery_filter_audit":
            correction_status[name] = "pending"
            continue
        track_dir = (
            screening_root / "expanded-search-screening"
            if name == "expanded_alternate_search"
            else screening_root / "exhaustive-exclusion-rescreen"
        )
        fulltext_outputs = list(track_dir.glob("fulltext-reviewer-*.csv"))
        if (track_dir / "qc-final/summary.json").is_file():
            correction_status[name] = "lineage_resolution_pending"
        elif (track_dir / "final/summary.json").is_file():
            correction_status[name] = "independent_inclusion_qc_in_progress"
        elif (
            track_dir
            / "fulltext-comparison/third-adjudications.csv"
        ).is_file():
            correction_status[name] = "raw_finalization_pending"
        elif fulltext_outputs:
            correction_status[name] = "full_text_in_progress"
        elif (track_dir / "comparison/agreement-summary.json").is_file():
            correction_status[name] = "full_text_pending"
        else:
            correction_status[name] = "title_abstract_pending"
    lineage_summary_path = (
        screening_root / "corrected-lineage-resolved/summary.json"
    )
    correction_status["cross_source_publication_lineage"] = (
        "complete" if lineage_summary_path.is_file() else "pending"
    )
    corrected_new_validation_path = (
        screening_root / "corrected-new-records/validation.json"
    )
    if corrected_new_validation_path.is_file():
        corrected_new_validation = json.loads(
            corrected_new_validation_path.read_text(encoding="utf-8")
        )
        correction_status["novel_extraction_and_coding"] = (
            "complete"
            if corrected_new_validation.get("status") == "pass"
            else "fail"
        )
    else:
        correction_status["novel_extraction_and_coding"] = "pending"
    canonical_freeze_path = final_dir / "correction-freeze.json"
    if canonical_freeze_path.is_file():
        canonical_freeze = json.loads(
            canonical_freeze_path.read_text(encoding="utf-8")
        )
        correction_status["canonical_regeneration"] = (
            "complete"
            if canonical_freeze.get("status") == "complete"
            else "fail"
        )
    else:
        correction_status["canonical_regeneration"] = "pending"
    search_screening_and_lineage_complete = all(
        correction_status[name] == "complete"
        for name in (
            "discovery_filter_audit",
            "expanded_alternate_search",
            "exhaustive_filter_rescreen",
            "cross_source_publication_lineage",
        )
    )
    search_correction_complete = all(
        value == "complete" for value in correction_status.values()
    )
    developmental_disclosure = (
        "Developmental search correction" in manuscript
        and "All study counts, references, tables" in manuscript
    )
    checks["developmental_status_disclosure"] = {
        "pass": search_correction_complete or developmental_disclosure,
        "search_screening_and_lineage_complete": (
            search_screening_and_lineage_complete
        ),
        "search_correction_complete": search_correction_complete,
        "correction_status": correction_status,
    }

    if corrected_new_validation_path.is_file():
        corrected_validation = json.loads(
            corrected_new_validation_path.read_text(encoding="utf-8")
        )
    else:
        corrected_validation = {}
    checks["corrected_addition_extraction_and_coding"] = {
        "pass": (
            corrected_validation.get("status") == "pass"
            and corrected_validation.get("records") == 35
            and corrected_validation.get("completed_prior_sample") == 5
            and corrected_validation.get("completed_current_batches") == 30
            and not corrected_validation.get("errors")
        ),
        "records": corrected_validation.get("records", 0),
        "completed_prior_sample": corrected_validation.get(
            "completed_prior_sample", 0
        ),
        "completed_current_batches": corrected_validation.get(
            "completed_current_batches", 0
        ),
        "errors": corrected_validation.get("errors", []),
        "validation_file": str(corrected_new_validation_path.relative_to(root)),
    }

    technical_pass = all(bool(item["pass"]) for item in checks.values())
    submission_gates = {
        "search_correction": (
            "complete" if search_correction_complete else "pending"
        ),
        "human_dual_verification": "pending",
        "authenticated_database_update": "pending",
        "criteria_binding_venue_check": "pending",
        "information_specialist_search_review": "pending",
        "healthcare_professional_involvement": "pending",
        "author_metadata_competing_interests_and_credit": "pending",
    }
    if not technical_pass:
        status = "fail"
    elif not search_correction_complete:
        if not search_screening_and_lineage_complete:
            status = "development_snapshot_pass_search_or_lineage_pending"
        elif correction_status["novel_extraction_and_coding"] != "complete":
            status = "development_snapshot_pass_novel_extraction_pending"
        else:
            status = "corrected_corpus_pass_canonical_regeneration_pending"
    else:
        status = "technical_pass_submission_gates_pending"
    payload = {
        "status": status,
        "checks": checks,
        "submission_gates": submission_gates,
    }
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))
    return 0 if technical_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
