#!/usr/bin/env python3
"""Build a reproducible overlap audit against Chen et al. (2026).

The comparison review reports 14 strict empirical studies but does not provide
an explicit machine-readable roster. The list below is therefore a
high-confidence reconstruction: ten studies appear in its representative
model table, and four additional studies are named in the empirical synthesis,
bringing the total to the reported 14.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path


COMPARISON_STUDIES = [
    {
        "citation_key": "ref084",
        "title": "Cardiac Copilot: Automatic Probe Guidance for Echocardiography with World Model",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref047",
        "title": "EHRWorld: A Patient-Centric Medical World Model for Long-Horizon Clinical Trajectories",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref046",
        "title": "EchoJEPA: A Latent Predictive Foundation Model for Echocardiography",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref050",
        "title": "Brain-WM: Brain Glioblastoma World Model",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref070",
        "title": "CLARITY: Medical World Model for Guiding Treatment Decisions by Modeling Context-Aware Disease Trajectories in Latent Space",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref040",
        "title": "Xray2Xray: World Model from Chest X-rays with Volumetric Context",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref074",
        "title": "EchoWorld: Learning Motion-Aware World Models for Echocardiography Probe Guidance",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref039",
        "title": "Medical World Model",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref051",
        "title": "SAW: Toward a Surgical Action World Model via Controllable and Scalable Video Generation",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref054",
        "title": "ChronoMedicalWorld: A Medical World Model for Learning Patient Trajectories from Longitudinal Care Data",
        "source_basis": "representative-model table",
        "source_pages": "20",
    },
    {
        "citation_key": "ref020",
        "title": "Treatment-Aware Diffusion Probabilistic Model for Longitudinal MRI Generation and Diffuse Glioma Growth Prediction",
        "source_basis": "treatment-response empirical synthesis",
        "source_pages": "24-25",
    },
    {
        "citation_key": "ref036",
        "title": "Surgical Vision World Model",
        "source_basis": "action-semantics empirical synthesis",
        "source_pages": "25",
    },
    {
        "citation_key": "ref048",
        "title": "Policy4OOD: A Knowledge-Guided World Model for Policy Intervention Simulation against the Opioid Overdose Crisis",
        "source_basis": "planning empirical synthesis",
        "source_pages": "19",
    },
    {
        "citation_key": "ref049",
        "title": "World Model Enhanced Offline Reinforcement Learning for Sequential Intervention Optimization in Acute Kidney Injury",
        "source_basis": "counterfactual/planning empirical synthesis",
        "source_pages": "18, 36",
    },
]


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def index_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        normalize_title(row.get("title", "")): row
        for row in rows
        if row.get("title", "").strip()
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "comparison_review_citation_key",
        "comparison_review_title",
        "source_basis",
        "source_pages",
        "our_disposition",
        "our_candidate_id",
        "our_matched_title",
        "our_reason_code",
        "our_rationale",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--supplement-decisions", type=Path, required=True)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    if not args.source_pdf.exists():
        raise FileNotFoundError(args.source_pdf)

    corpus_rows = read_csv(args.corpus)
    supplement_rows = read_csv(args.supplement_decisions)
    corpus_index = index_rows(corpus_rows)
    supplement_index = index_rows(supplement_rows)

    output_rows: list[dict[str, str]] = []
    for study in COMPARISON_STUDIES:
        key = normalize_title(study["title"])
        included = corpus_index.get(key)
        screened = supplement_index.get(key)
        if included:
            disposition = "included"
            matched = included
        elif screened:
            disposition = screened.get("final_decision", "screened")
            matched = screened
        else:
            disposition = "not located"
            matched = {}

        output_rows.append(
            {
                "comparison_review_citation_key": study["citation_key"],
                "comparison_review_title": study["title"],
                "source_basis": study["source_basis"],
                "source_pages": study["source_pages"],
                "our_disposition": disposition,
                "our_candidate_id": matched.get("candidate_id", ""),
                "our_matched_title": matched.get("title", ""),
                "our_reason_code": matched.get("final_reason_code", ""),
                "our_rationale": matched.get(
                    "adjudication_rationale",
                    matched.get("reviewer_notes", ""),
                ),
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "chen-2026-study-overlap.csv"
    md_path = args.output_dir / "chen-2026-study-overlap.md"
    write_csv(csv_path, output_rows)

    overlap = sum(row["our_disposition"] == "included" for row in output_rows)
    excluded = sum(row["our_disposition"] == "exclude" for row in output_rows)
    not_located = len(output_rows) - overlap - excluded
    ours_n = len(corpus_rows)
    comparison_n = len(COMPARISON_STUDIES)
    union_n = ours_n + comparison_n - overlap
    comparison_coverage = overlap / comparison_n
    provisional_jaccard = overlap / union_n

    table_rows = []
    for row in output_rows:
        reason = row["our_reason_code"] or "—"
        table_rows.append(
            f"| {row['comparison_review_title']} | {row['source_basis']} "
            f"(p. {row['source_pages']}) | {row['our_disposition']} | {reason} |"
        )

    md_path.write_text(
        "\n".join(
            [
                "# Study-level overlap with Chen et al. (2026)",
                "",
                "## Reconstruction status",
                "",
                "Chen et al. report a nested strict empirical subset of 14 studies "
                "but do not provide an explicit machine-readable roster. This is a "
                "high-confidence reconstruction from the official article PDF: ten "
                "studies are listed in the representative-model table and four "
                "additional studies are named in the empirical synthesis, matching "
                "the reported total of 14. It should not be described as an "
                "author-supplied inclusion list.",
                "",
                f"Source PDF: `{args.source_pdf}`",
                "",
                "## Provisional overlap",
                "",
                f"- Comparison-review studies reconstructed: {comparison_n}",
                f"- Included in our current empirical corpus: {overlap} "
                f"({comparison_coverage:.1%})",
                f"- Located but excluded by our operational eligibility rule: {excluded}",
                f"- Not located: {not_located}",
                f"- Current empirical corpus size: {ours_n}",
                f"- Provisional title-level Jaccard overlap: {overlap}/{union_n} "
                f"({provisional_jaccard:.1%})",
                "",
                "These figures are provisional because our expanded search audit is "
                "still active. The Jaccard value is descriptive, not a comparative "
                "quality score: the reviews use different eligibility boundaries, "
                "search dates, and corpus roles.",
                "",
                "## Study dispositions",
                "",
                "| Reconstructed Chen et al. study | Source basis | Our disposition | Reason code |",
                "|---|---|---|---|",
                *table_rows,
                "",
                "## Boundary difference",
                "",
                "The only reconstructed strict-subset study not included in our "
                "current empirical corpus is EchoJEPA. It was located through citation "
                "chasing and independently screened, then excluded at adjudication "
                "because the reported evaluation assessed representation transfer and "
                "robustness rather than future-state rollout, action-response "
                "simulation, or planning. This difference is substantive rather than "
                "a search miss: Chen et al. admit an L1 predictive-representation "
                "capability, whereas our operational corpus requires direct empirical "
                "evaluation of modeled state evolution or interaction.",
                "",
                "## Interpretation",
                "",
                "The 13/14 overlap supports strong recovery of the field's established "
                "anchor studies. The much larger current corpus reflects our broader "
                "operational search across medical, physiological, and procedural "
                "systems, but its final size and interpretation must remain unfrozen "
                "until the expanded alternate-term screen, full-text review, and "
                "adjudication are complete.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(
        {
            "comparison_studies": comparison_n,
            "overlap": overlap,
            "excluded": excluded,
            "not_located": not_located,
            "current_corpus": ours_n,
            "union": union_n,
            "comparison_coverage": round(comparison_coverage, 4),
            "jaccard": round(provisional_jaccard, 4),
            "csv": str(csv_path),
            "markdown": str(md_path),
        }
    )


if __name__ == "__main__":
    main()
