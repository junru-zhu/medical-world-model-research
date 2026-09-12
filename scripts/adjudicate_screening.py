#!/usr/bin/env python3
"""Create an auditable title/abstract screening result after adjudication."""

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
    "reviewer_b_decision",
    "reviewer_b_reason_code",
    "final_decision",
    "final_corpus_type",
    "final_reason_code",
    "resolution_route",
    "adjudication_rationale",
]


def rows_by_id(path: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
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

    candidates, candidate_map = rows_by_id(args.candidates)
    _, reviewer_a = rows_by_id(args.reviewer_a)
    _, reviewer_b = rows_by_id(args.reviewer_b)
    _, adjudications = rows_by_id(args.adjudications)

    expected = set(candidate_map)
    for label, mapping in (("reviewer A", reviewer_a), ("reviewer B", reviewer_b)):
        if set(mapping) != expected:
            raise ValueError(
                f"{label} IDs differ from candidates: "
                f"missing={sorted(expected - set(mapping))[:10]}, "
                f"extra={sorted(set(mapping) - expected)[:10]}"
            )

    outputs: list[dict[str, str]] = []
    used_adjudications: set[str] = set()
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        row_a = reviewer_a[candidate_id]
        row_b = reviewer_b[candidate_id]
        if (
            row_a["decision"] == row_b["decision"]
            and row_a["decision"] != "uncertain"
            and candidate_id not in adjudications
        ):
            final_decision = row_a["decision"]
            final_corpus_type = (
                row_a["corpus_type"]
                if row_a["corpus_type"] == row_b["corpus_type"]
                else "uncertain"
            )
            final_reason = (
                row_a["reason_code"]
                if row_a["reason_code"] == row_b["reason_code"]
                else row_a["reason_code"]
            )
            route = "reviewer_consensus"
            rationale = (
                row_a["rationale"]
                if row_a["rationale"] == row_b["rationale"]
                else f"A: {row_a['rationale']} B: {row_b['rationale']}"
            )
        else:
            if candidate_id not in adjudications:
                raise ValueError(f"Missing adjudication for {candidate_id}")
            adjudication = adjudications[candidate_id]
            used_adjudications.add(candidate_id)
            final_decision = adjudication["final_decision"]
            final_corpus_type = adjudication["final_corpus_type"]
            final_reason = adjudication["final_reason_code"]
            route = "third_adjudication"
            rationale = adjudication["adjudication_rationale"]
        outputs.append(
            {
                **candidate,
                "reviewer_a_decision": row_a["decision"],
                "reviewer_a_reason_code": row_a["reason_code"],
                "reviewer_b_decision": row_b["decision"],
                "reviewer_b_reason_code": row_b["reason_code"],
                "final_decision": final_decision,
                "final_corpus_type": final_corpus_type,
                "final_reason_code": final_reason,
                "resolution_route": route,
                "adjudication_rationale": rationale,
            }
        )

    unused = set(adjudications) & expected - used_adjudications
    if unused:
        raise ValueError(f"Unused adjudications for this stratum: {sorted(unused)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "adjudicated": (args.output_dir / "adjudicated.csv", outputs),
        "full_text_candidates": (
            args.output_dir / "full-text-candidates.csv",
            [row for row in outputs if row["final_decision"] != "exclude"],
        ),
        "excluded": (
            args.output_dir / "excluded-title-abstract.csv",
            [row for row in outputs if row["final_decision"] == "exclude"],
        ),
    }
    for _, (path, rows) in paths.items():
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    counts = {
        decision: sum(row["final_decision"] == decision for row in outputs)
        for decision in ("include", "exclude", "uncertain")
    }
    print(
        f"{args.candidates}: total={len(outputs)}, "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
