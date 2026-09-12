#!/usr/bin/env python3
"""Create the final AI-assisted full-text eligibility corpus."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


OUTPUT_COLUMNS = [
    "candidate_id",
    "title",
    "abstract",
    "authors",
    "year",
    "publication_date",
    "venue",
    "doi",
    "arxiv_id",
    "url",
    "record_type",
    "sources",
    "query_labels",
    "source_status",
    "reviewer_a_decision",
    "reviewer_a_reason_code",
    "reviewer_a_dynamics",
    "reviewer_a_evaluation",
    "reviewer_a_lineage",
    "reviewer_a_full_text_url",
    "reviewer_b_decision",
    "reviewer_b_reason_code",
    "reviewer_b_dynamics",
    "reviewer_b_evaluation",
    "reviewer_b_lineage",
    "reviewer_b_full_text_url",
    "final_decision",
    "final_corpus_type",
    "final_reason_code",
    "resolution_route",
    "adjudication_rationale",
]


def read(path: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return rows, {row["candidate_id"]: row for row in rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--adjudications", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    candidates, candidate_map = read(args.candidates)
    _, reviewer_a = read(args.reviewer_a)
    _, reviewer_b = read(args.reviewer_b)
    _, adjudications = read(args.adjudications)
    expected = set(candidate_map)
    if set(reviewer_a) != expected or set(reviewer_b) != expected:
        raise ValueError("Reviewer IDs do not match full-text candidates.")

    outputs: list[dict[str, str]] = []
    used: set[str] = set()
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        row_a = reviewer_a[candidate_id]
        row_b = reviewer_b[candidate_id]
        if (
            row_a["decision"] == row_b["decision"]
            and row_a["decision"] != "uncertain"
            and candidate_id not in adjudications
        ):
            decision = row_a["decision"]
            corpus_type = (
                row_a["corpus_type"]
                if row_a["corpus_type"] == row_b["corpus_type"]
                else "uncertain"
            )
            reason = (
                row_a["primary_reason_code"]
                if row_a["primary_reason_code"] == row_b["primary_reason_code"]
                else row_a["primary_reason_code"]
            )
            route = "reviewer_consensus"
            rationale = (
                row_a["rationale"]
                if row_a["rationale"] == row_b["rationale"]
                else f"A: {row_a['rationale']} B: {row_b['rationale']}"
            )
        else:
            if candidate_id not in adjudications:
                raise ValueError(f"Missing full-text adjudication for {candidate_id}")
            adjudication = adjudications[candidate_id]
            used.add(candidate_id)
            decision = adjudication["final_decision"]
            corpus_type = adjudication["final_corpus_type"]
            reason = adjudication["final_reason_code"]
            route = "third_adjudication"
            rationale = adjudication["adjudication_rationale"]
        outputs.append(
            {
                **candidate,
                "reviewer_a_decision": row_a["decision"],
                "reviewer_a_reason_code": row_a["primary_reason_code"],
                "reviewer_a_dynamics": row_a["evidence_for_dynamics"],
                "reviewer_a_evaluation": row_a["evidence_for_evaluation"],
                "reviewer_a_lineage": row_a["publication_lineage"],
                "reviewer_a_full_text_url": row_a["full_text_url"],
                "reviewer_b_decision": row_b["decision"],
                "reviewer_b_reason_code": row_b["primary_reason_code"],
                "reviewer_b_dynamics": row_b["evidence_for_dynamics"],
                "reviewer_b_evaluation": row_b["evidence_for_evaluation"],
                "reviewer_b_lineage": row_b["publication_lineage"],
                "reviewer_b_full_text_url": row_b["full_text_url"],
                "final_decision": decision,
                "final_corpus_type": corpus_type,
                "final_reason_code": reason,
                "resolution_route": route,
                "adjudication_rationale": rationale,
            }
        )

    unused = set(adjudications) & expected - used
    if unused:
        raise ValueError(f"Unused adjudications: {sorted(unused)}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("adjudicated.csv", outputs),
        ("included.csv", [row for row in outputs if row["final_decision"] == "include"]),
        ("excluded.csv", [row for row in outputs if row["final_decision"] == "exclude"]),
    ):
        with (args.output_dir / filename).open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(
                handle, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(rows)

    print(
        f"total={len(outputs)}, "
        f"included={sum(row['final_decision'] == 'include' for row in outputs)}, "
        f"excluded={sum(row['final_decision'] == 'exclude' for row in outputs)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
