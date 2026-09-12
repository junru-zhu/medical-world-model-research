#!/usr/bin/env python3
"""Assemble the canonical review reference section from the frozen ledger."""

from __future__ import annotations

import argparse
from pathlib import Path


METHOD_REFERENCES = [
    "Tricco AC, Lillie E, Zarin W, et al. PRISMA Extension for Scoping Reviews (PRISMA-ScR): Checklist and Explanation. *Annals of Internal Medicine*. 2018;169(7):467-473. doi:10.7326/M18-0850.",
    "Rethlefsen ML, Kirtley S, Waffenschmidt S, et al. PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews. *Systematic Reviews*. 2021;10(1):39. doi:10.1186/s13643-020-01542-z.",
    "Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI Statement: Updated Guidance for Reporting Clinical Prediction Models That Use Regression or Machine Learning Methods. *BMJ*. 2024;385:e078378. doi:10.1136/bmj-2023-078378.",
    "Vasey B, Nagendran M, Campbell B, et al. Reporting Guideline for the Early-Stage Clinical Evaluation of Decision Support Systems Driven by Artificial Intelligence: DECIDE-AI. *Nature Medicine*. 2022;28(5):924-933. doi:10.1038/s41591-022-01772-9.",
    "Hernán MA, Robins JM. Using Big Data to Emulate a Target Trial When a Randomized Trial Is Not Available. *American Journal of Epidemiology*. 2016;183(8):758-764. doi:10.1093/aje/kwv254.",
    "Reyna MA, Josef CS, Jeter R, et al. Early Prediction of Sepsis from Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019. *PhysioNet*. 2019. Version 1.0.0. doi:10.13026/v64v-d857.",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()

    manuscript = args.manuscript.read_text(encoding="utf-8")
    marker = "## References"
    if marker not in manuscript:
        raise ValueError("Manuscript has no References heading.")
    body = manuscript.split(marker, 1)[0].rstrip()

    ledger_lines = args.ledger.read_text(encoding="utf-8").splitlines()
    references = [
        line.strip()
        for line in ledger_lines
        if line.strip() and not line.startswith("# ")
    ]
    if not references:
        raise ValueError("The included-study reference ledger is empty.")
    method_references = [
        f"{number}. {reference}"
        for number, reference in enumerate(
            METHOD_REFERENCES, start=len(references) + 1
        )
    ]

    assembled = (
        body
        + "\n\n## References\n\n"
        + "\n\n".join(references + method_references)
        + "\n"
    )
    args.manuscript.write_text(assembled, encoding="utf-8")
    print(f"Assembled {len(references) + len(method_references)} references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
