#!/usr/bin/env python3
"""Build a non-scored, domain-level methodological appraisal matrix."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def reporting_status(value: str) -> str:
    text = value.strip()
    lower = text.casefold()
    if re.match(r"^na(?:\b|\s|\()", lower):
        return "not_applicable"
    if (
        re.match(r"^ni(?:\b|\s|\()", lower)
        or "not reported" in lower
        or "not identified" in lower
        or lower in {"none", "none reported", "unclear"}
    ):
        return "not_identified"
    return "described"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    pilot = {row["candidate_id"]: row for row in read(args.pilot)}
    extraction = {
        row["candidate_id"]: row for row in read(args.extraction)
    }
    annotations = {
        row["candidate_id"]: row for row in read(args.annotations)
    }
    if set(pilot) != set(extraction) or set(pilot) != set(annotations):
        raise ValueError(
            "Pilot, extraction, and annotation candidate IDs differ."
        )

    output: list[dict[str, str]] = []
    for candidate_id, coded in pilot.items():
        extracted = extraction[candidate_id]
        annotation = annotations[candidate_id]
        output.append(
            {
                "candidate_id": candidate_id,
                "title": coded["title"],
                "domain_group": annotation["domain_group"],
                "highest_capability_claim": coded[
                    "highest_capability_claim"
                ],
                "missingness_reporting": reporting_status(
                    extracted["missingness"]
                ),
                "censoring_reporting": reporting_status(
                    extracted["censoring_or_competing_events"]
                ),
                "formal_calibration": coded["formal_calibration"],
                "frozen_external_validation": coded[
                    "frozen_external_validation"
                ],
                "explicit_causal_estimand": coded[
                    "explicit_causal_estimand"
                ],
                "action_perturbation": coded["action_perturbation"],
                "closed_loop_evaluation": coded[
                    "closed_loop_evaluation"
                ],
                "safety_hazard_test": coded["safety_hazard_test"],
                "public_code": coded["public_code"],
                "reproducibility_evidence": coded[
                    "reproducibility_evidence"
                ],
                "appraisal_strengths": extracted["appraisal_strengths"],
                "appraisal_limitations": extracted[
                    "appraisal_limitations"
                ],
                "evidence_anchors": extracted["evidence_anchors"],
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = args.output_dir / "methodological-appraisal.csv"
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)

    domains: dict[str, dict[str, object]] = {}
    for domain in sorted({row["domain_group"] for row in output}):
        subset = [row for row in output if row["domain_group"] == domain]
        domains[domain] = {
            "records": len(subset),
            "missingness_reporting": dict(
                sorted(Counter(row["missingness_reporting"] for row in subset).items())
            ),
            "censoring_reporting": dict(
                sorted(Counter(row["censoring_reporting"] for row in subset).items())
            ),
            "formal_calibration_yes": sum(
                row["formal_calibration"] == "yes" for row in subset
            ),
            "frozen_external_validation_yes": sum(
                row["frozen_external_validation"] == "yes" for row in subset
            ),
            "explicit_causal_estimand_yes": sum(
                row["explicit_causal_estimand"] == "yes" for row in subset
            ),
            "action_perturbation_yes": sum(
                row["action_perturbation"] == "yes" for row in subset
            ),
            "closed_loop_real_or_simulation": sum(
                row["closed_loop_evaluation"] in {"real", "simulation"}
                for row in subset
            ),
            "safety_hazard_test_yes": sum(
                row["safety_hazard_test"] == "yes" for row in subset
            ),
            "public_code_yes": sum(
                row["public_code"] == "yes" for row in subset
            ),
            "reproducibility_evidence_strong": sum(
                row["reproducibility_evidence"] == "2" for row in subset
            ),
        }
    payload = {
        "records": len(output),
        "domains": domains,
        "interpretation": (
            "This is a descriptive, study-type-sensitive appraisal of "
            "reported methods and evidence. It is not a validated risk-of-bias "
            "instrument and no aggregate quality score is calculated."
        ),
    }
    (args.output_dir / "methodological-appraisal.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Domain-Level Methodological Appraisal",
        "",
        (
            "This appraisal reports study-type-sensitive methodological "
            "features without calculating an aggregate quality score. It is "
            "not a validated risk-of-bias instrument."
        ),
        "",
        "| Domain | Studies | Missingness described | Censoring described | Calibration | Frozen external | Causal estimand | Action perturbation | Real/sim closed loop | Safety test | Public code | Strong reproducibility |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for domain, item in domains.items():
        lines.append(
            f"| {domain.replace('_', ' ')} | {item['records']} | "
            f"{item['missingness_reporting'].get('described', 0)} | "
            f"{item['censoring_reporting'].get('described', 0)} | "
            f"{item['formal_calibration_yes']} | "
            f"{item['frozen_external_validation_yes']} | "
            f"{item['explicit_causal_estimand_yes']} | "
            f"{item['action_perturbation_yes']} | "
            f"{item['closed_loop_real_or_simulation']} | "
            f"{item['safety_hazard_test_yes']} | "
            f"{item['public_code_yes']} | "
            f"{item['reproducibility_evidence_strong']} |"
        )
    (args.output_dir / "methodological-appraisal.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
