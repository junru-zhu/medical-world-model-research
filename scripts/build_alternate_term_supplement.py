#!/usr/bin/env python3
"""Build an expanded alternate-terminology screening supplement."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


DOMAIN_RE = re.compile(
    r"\b("
    r"medical|medicine|clinical|patient|health|healthcare|hospital|ehr|"
    r"electronic health|physiolog\w*|surg\w*|echocardi\w*|ultrasound|"
    r"radiolog\w*|oncolog\w*|tumou?r|glioma|cardiac|brain|treatment|"
    r"intervention|therapy|disease|intensive care|critical care|biomedical|"
    r"sepsis|diabet\w*|cancer|cell\w*|molecular|genom\w*|omic\w*|immune|"
    r"microbiome|malaria|drug|pharma\w*|robot\w*|imaging|mri|ct|x-ray"
    r")\b",
    re.IGNORECASE,
)
ALTERNATE_RE = re.compile(
    r"\b("
    r"model[- ]based reinforcement learning|patient simulators?|"
    r"clinical simulators?|medical simulators?|digital twins?|"
    r"latent dynamics?|temporal dynamics?|transition models?|"
    r"dynamics models?|world[- ]action models?|"
    r"trajectory (?:models?|simulators?|forecast\w*)|"
    r"progression models?|generative (?:ehr|clinical|patient|"
    r"physiolog\w*|cell\w*) models?|future (?:states?|trajectory|observation)|"
    r"counterfactual simul\w*|autoregressive (?:rollouts?|forecast\w*)|"
    r"imagined environments?|intervention[- ]conditioned forecast\w*|"
    r"action[- ]conditioned forecast\w*|multistep forecast\w*|"
    r"multi-step forecast\w*|long[- ]horizon forecast\w*|"
    r"disease progression|patient progression|simulation model|"
    r"future prediction"
    r")\b",
    re.IGNORECASE,
)


def uid(row: dict[str, object]) -> str:
    identity = str(
        row.get("doi")
        or row.get("arxiv_id")
        or row.get("title")
        or row.get("url")
        or ""
    ).strip().lower()
    return "AUD-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excluded", type=Path, required=True)
    parser.add_argument("--prior-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with args.prior_audit.open(newline="", encoding="utf-8") as handle:
        prior_ids = {row["audit_id"] for row in csv.DictReader(handle)}
    selected: list[dict[str, object]] = []
    for row in load_jsonl(args.excluded):
        text = f"{row.get('title', '')} {row.get('abstract', '')}"
        if DOMAIN_RE.search(text) and ALTERNATE_RE.search(text):
            if uid(row) not in prior_ids:
                selected.append(row)
    selected.sort(key=lambda row: str(row.get("title", "")).lower())

    fields = [
        "audit_id",
        "stratum",
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
        "original_exclusion_reason",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in selected:
            output = {field: str(row.get(field, "")) for field in fields}
            output["audit_id"] = uid(row)
            output["stratum"] = "expanded_alternate_terms"
            output["original_exclusion_reason"] = str(
                row.get("exclusion_reason", "")
            )
            writer.writerow(output)
    summary = {
        "expanded_alternate_term_candidates_total": len(selected) + sum(
            1
            for row in load_jsonl(args.excluded)
            if DOMAIN_RE.search(
                f"{row.get('title', '')} {row.get('abstract', '')}"
            )
            and ALTERNATE_RE.search(
                f"{row.get('title', '')} {row.get('abstract', '')}"
            )
            and uid(row) in prior_ids
        ),
        "previously_screened_in_filter_audit": sum(
            1
            for row in load_jsonl(args.excluded)
            if DOMAIN_RE.search(
                f"{row.get('title', '')} {row.get('abstract', '')}"
            )
            and ALTERNATE_RE.search(
                f"{row.get('title', '')} {row.get('abstract', '')}"
            )
            and uid(row) in prior_ids
        ),
        "new_candidates": len(selected),
    }
    (args.output.parent / "sampling-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
