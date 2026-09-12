#!/usr/bin/env python3
"""Apply an independent inclusion-QC pass to an adjudicated audit."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


QC_FIELDS = [
    "qc_decision",
    "qc_corpus_type",
    "qc_reason_code",
    "qc_rationale",
    "full_text_anchor",
    "confidence",
]
QC_INPUT_FIELDS = ["audit_id", "title", *QC_FIELDS]
QC_DECISIONS = {"include", "exclude"}
QC_CORPUS_TYPES = {"empirical", "review", "not_applicable"}
QC_CONFIDENCE = {"high", "medium", "low"}


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudicated", type=Path, required=True)
    parser.add_argument("--qc", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    _, adjudicated = read(args.adjudicated)
    qc_fields, qc_rows = read(args.qc)
    if qc_fields != QC_INPUT_FIELDS:
        raise ValueError(
            "Inclusion-QC schema mismatch: "
            f"expected {QC_INPUT_FIELDS}, found {qc_fields}"
        )
    qc = {row["audit_id"]: row for row in qc_rows}
    if len(qc) != len(qc_rows):
        raise ValueError("Duplicate IDs in inclusion QC.")
    initially_included_order = [
        row["audit_id"]
        for row in adjudicated
        if row["final_decision"] == "include"
    ]
    initially_included = set(initially_included_order)
    qc_order = [row["audit_id"] for row in qc_rows]
    if qc_order != initially_included_order:
        missing = initially_included - set(qc_order)
        extra = set(qc_order) - initially_included
        raise ValueError(f"QC coverage mismatch: missing={missing}, extra={extra}")
    adjudicated_by_id = {row["audit_id"]: row for row in adjudicated}
    for index, row in enumerate(qc_rows, start=2):
        audit_id = row["audit_id"]
        blank = [field for field in QC_INPUT_FIELDS if not row[field].strip()]
        if blank:
            raise ValueError(f"{args.qc}:{index}: blank fields {blank}")
        if row["title"] != adjudicated_by_id[audit_id]["title"]:
            raise ValueError(f"{args.qc}:{index}: title mismatch for {audit_id}")
        if row["qc_decision"] not in QC_DECISIONS:
            raise ValueError(
                f"{args.qc}:{index}: invalid qc_decision={row['qc_decision']!r}"
            )
        if row["qc_corpus_type"] not in QC_CORPUS_TYPES:
            raise ValueError(
                f"{args.qc}:{index}: invalid qc_corpus_type="
                f"{row['qc_corpus_type']!r}"
            )
        if row["confidence"] not in QC_CONFIDENCE:
            raise ValueError(
                f"{args.qc}:{index}: invalid confidence={row['confidence']!r}"
            )
        if (
            row["qc_decision"] == "include"
            and row["qc_corpus_type"] not in {"empirical", "review"}
        ):
            raise ValueError(
                f"{args.qc}:{index}: included row has invalid corpus type"
            )
        if (
            row["qc_decision"] == "exclude"
            and row["qc_corpus_type"] != "not_applicable"
        ):
            raise ValueError(
                f"{args.qc}:{index}: excluded row must be not_applicable"
            )

    output: list[dict[str, str]] = []
    for row in adjudicated:
        merged = dict(row)
        for field in QC_FIELDS:
            merged[field] = ""
        if row["audit_id"] in qc:
            decision = qc[row["audit_id"]]
            for field in QC_FIELDS:
                merged[field] = decision[field]
            if decision["qc_decision"] == "include":
                if decision["qc_corpus_type"] not in {"empirical", "review"}:
                    raise ValueError(
                        f"Included QC row has invalid corpus type: {row['audit_id']}"
                    )
                merged["final_decision"] = "include"
                merged["final_corpus_type"] = decision["qc_corpus_type"]
                merged["resolution_route"] = (
                    f"{row['resolution_route']}+independent_inclusion_qc"
                )
                merged["adjudication_rationale"] = decision["qc_rationale"]
            elif decision["qc_decision"] == "exclude":
                merged["final_decision"] = "exclude"
                merged["final_corpus_type"] = "not_applicable"
                merged["final_reason_code"] = decision["qc_reason_code"]
                merged["resolution_route"] = "post_adjudication_inclusion_qc"
                merged["adjudication_rationale"] = decision["qc_rationale"]
            else:
                raise ValueError(
                    f"QC decisions must be final include/exclude: {row['audit_id']}"
                )
        output.append(merged)

    fields = list(adjudicated[0]) + QC_FIELDS
    included = [row for row in output if row["final_decision"] == "include"]
    excluded = [row for row in output if row["final_decision"] == "exclude"]
    if len(included) + len(excluded) != len(output):
        raise ValueError("All post-QC decisions must be include or exclude.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / "adjudicated.csv", output, fields)
    write(args.output_dir / "included.csv", included, fields)
    write(args.output_dir / "excluded.csv", excluded, fields)
    summary = {
        "records": len(output),
        "initially_included": len(initially_included),
        "qc_retained": len(included),
        "qc_removed": len(initially_included) - len(included),
        "included_empirical": sum(
            row["final_corpus_type"] == "empirical" for row in included
        ),
        "included_reviews": sum(
            row["final_corpus_type"] == "review" for row in included
        ),
        "excluded_total": len(excluded),
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
