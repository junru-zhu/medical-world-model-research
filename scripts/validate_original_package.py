#!/usr/bin/env python3
"""Validate the original-paper methods package and final-result gates."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_PHRASES = (
    "prespecified post-hoc",
    "Causal Transformer",
    "causal Transformer",
    "same data, parameter budget",
    "paired internal and external",
)
REQUIRED_PHRASES = (
    "passive forecasting",
    "moment-matched Gaussian negative log score",
    "five fixed trained instances",
    "sampled rollout states",
    "post-pilot",
    "Declaration of Generative AI",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def citation_numbers(body: str) -> set[int]:
    numbers: set[int] = set()
    for content in re.findall(r"\[([0-9,\-]+)\]", body):
        values: set[int] = set()
        for part in content.split(","):
            if "-" in part:
                start, end = (int(value) for value in part.split("-", 1))
                values.update(range(start, end + 1))
            else:
                values.add(int(part))
        # Bracketed physiological ranges such as [0,100] are not citations.
        if 0 not in values and max(values, default=0) <= 20:
            numbers.update(values)
    return numbers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.project_root.resolve()
    manuscript_path = root / "manuscript/original-paper.md"
    bibliography_path = root / "manuscript/original-references.bib"
    specification_path = root / "experiments/frozen-analysis-specification.md"
    amendment_path = (
        root / "experiments/protocol-deviations-and-amendments.md"
    )
    data_validation_path = root / "experiments/results/neural-data/validation.json"
    required_files = (
        manuscript_path,
        bibliography_path,
        specification_path,
        amendment_path,
        data_validation_path,
        root / "experiments/src/run_neural_matrix.py",
        root / "experiments/src/evaluate_neural_forecaster.py",
        root / "experiments/src/analyze_frozen_results.py",
        root / "experiments/src/run_monte_carlo_sensitivity.py",
    )
    missing_files = [
        str(path.relative_to(root)) for path in required_files if not path.is_file()
    ]
    if missing_files:
        raise FileNotFoundError(f"Missing required files: {missing_files}")

    manuscript = manuscript_path.read_text(encoding="utf-8")
    normalized_manuscript = re.sub(r"\s+", " ", manuscript)
    body, reference_section = manuscript.split("## References", 1)
    reference_numbers = {
        int(value)
        for value in re.findall(r"(?m)^(\d+)\.\s", reference_section)
    }
    citations = citation_numbers(body)
    data_validation = read_json(data_validation_path)
    forbidden_hits = [
        phrase for phrase in FORBIDDEN_PHRASES if phrase in normalized_manuscript
    ]
    missing_phrases = [
        phrase
        for phrase in REQUIRED_PHRASES
        if phrase not in normalized_manuscript
    ]
    tbd_count = len(re.findall(r"\bTBD\b|To be populated|To be completed", manuscript))

    frozen_analysis_path = root / "experiments/results/frozen-analysis/analysis-summary.json"
    monte_carlo_path = root / "experiments/results/monte-carlo-sensitivity/summary.json"
    frozen_analysis = (
        read_json(frozen_analysis_path) if frozen_analysis_path.is_file() else None
    )
    monte_carlo = (
        read_json(monte_carlo_path) if monte_carlo_path.is_file() else None
    )
    methods_checks = {
        "required_files": {
            "pass": not missing_files,
            "missing": missing_files,
        },
        "references": {
            "pass": bool(reference_numbers)
            and citations == reference_numbers
            and reference_numbers == set(range(1, max(reference_numbers) + 1)),
            "citations": sorted(citations),
            "reference_entries": sorted(reference_numbers),
        },
        "forbidden_wording": {
            "pass": not forbidden_hits,
            "hits": forbidden_hits,
        },
        "required_wording": {
            "pass": not missing_phrases,
            "missing": missing_phrases,
        },
        "neural_data_validation": {
            "pass": data_validation.get("status") == "pass",
            "status": data_validation.get("status"),
            "unique_patients": data_validation.get("unique_patients"),
            "selected_variables": len(
                data_validation.get("selected_variables", [])
            ),
        },
        "verified_counts": {
            "pass": all(
                value in manuscript
                for value in (
                    "40,336",
                    "14,247",
                    "3,015",
                    "3,074",
                    "2,069",
                    "17,931",
                    "1,841",
                    "10,622",
                    "5,143",
                    "30,450",
                    "24 variables",
                )
            )
        },
    }
    methods_pass = all(check["pass"] for check in methods_checks.values())
    result_gates = {
        "no_draft_placeholders": {
            "pass": tbd_count == 0,
            "placeholder_count": tbd_count,
        },
        "frozen_analysis": {
            "pass": bool(
                frozen_analysis
                and frozen_analysis.get("status") == "complete"
            ),
            "status": (
                frozen_analysis.get("status")
                if frozen_analysis
                else "pending"
            ),
        },
        "monte_carlo_sensitivity": {
            "pass": bool(
                monte_carlo and monte_carlo.get("status") == "complete"
            ),
            "status": (
                monte_carlo.get("status") if monte_carlo else "pending"
            ),
        },
    }
    results_pass = all(check["pass"] for check in result_gates.values())
    status = (
        "technical_pass_submission_gates_pending"
        if methods_pass and results_pass
        else (
            "methods_pass_results_pending"
            if methods_pass
            else "technical_fail"
        )
    )
    independent_review_files = (
        root
        / "ccfa-review-reports/original-paper-independent-reviewer-1-final.md",
        root
        / "ccfa-review-reports/original-paper-independent-reviewer-2-final.md",
    )
    payload = {
        "status": status,
        "methods_checks": methods_checks,
        "result_gates": result_gates,
        "submission_gates": {
            "clinical_expert_review": "pending",
            "author_metadata_funding_competing_interests_credit": "pending",
            "ethics_determination_confirmation": "pending",
            "stable_code_and_artifact_repository": "pending",
            "independent_results_and_claims_review": (
                "complete"
                if all(path.is_file() for path in independent_review_files)
                else "pending"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    return 0 if methods_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
