#!/usr/bin/env python3
"""Build a deterministic, stratified audit of discovery-filter exclusions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from pathlib import Path


MEDICAL_RE = re.compile(
    r"\b("
    r"medical|medicine|clinical|clinic|patient|health|healthcare|hospital|"
    r"ehr|electronic health|physiolog|surg|echocardi|ultrasound|radiolog|"
    r"oncolog|tumou?r|glioma|cardiac|brain|treatment|intervention|therapy|"
    r"disease|intensive care|critical care|biomedical"
    r")",
    re.IGNORECASE,
)
ALTERNATE_DYNAMICS_RE = re.compile(
    r"\b("
    r"model[- ]based reinforcement learning|patient simulators?|"
    r"(?:clinical|medical|health) digital twins?|latent dynamics?|"
    r"transition models?|dynamics models?|world[- ]action models?|"
    r"trajectory simulators?|generative (?:ehr|clinical|patient) models?|"
    r"disease progression models?|future states?|counterfactual simulators?|"
    r"autoregressive rollouts?|imagined environments?"
    r")\b",
    re.IGNORECASE,
)


def record_uid(row: dict[str, object]) -> str:
    identity = str(
        row.get("doi")
        or row.get("arxiv_id")
        or row.get("title")
        or row.get("url")
        or ""
    ).strip().lower()
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"AUD-{digest}"


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def select_random(
    rows: list[dict[str, object]], count: int, seed: int
) -> list[dict[str, object]]:
    if count > len(rows):
        raise ValueError(f"Requested {count} rows from a stratum of {len(rows)}")
    return random.Random(seed).sample(rows, count)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excluded", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phrase-random-n", type=int, default=100)
    parser.add_argument("--medical-random-n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args()

    excluded = load_jsonl(args.excluded)
    phrase_absent = [
        row
        for row in excluded
        if row.get("exclusion_reason")
        == "world-model phrase absent from title and abstract"
    ]
    medical_absent = [
        row
        for row in excluded
        if row.get("exclusion_reason")
        == "medical-domain term absent from title and abstract"
    ]
    enriched = []
    phrase_remainder = []
    for row in phrase_absent:
        text = f"{row.get('title', '')} {row.get('abstract', '')}"
        if MEDICAL_RE.search(text) and ALTERNATE_DYNAMICS_RE.search(text):
            enriched.append(row)
        else:
            phrase_remainder.append(row)

    selected: list[tuple[str, dict[str, object]]] = [
        ("alternate_dynamics_enriched", row)
        for row in sorted(enriched, key=lambda item: str(item.get("title", "")))
    ]
    selected.extend(
        ("phrase_absent_random", row)
        for row in select_random(
            phrase_remainder, args.phrase_random_n, args.seed
        )
    )
    selected.extend(
        ("medical_term_absent_random", row)
        for row in select_random(
            medical_absent, args.medical_random_n, args.seed + 1
        )
    )

    with args.candidates.open(newline="", encoding="utf-8") as handle:
        current_candidates = list(csv.DictReader(handle))
    policy_record = next(
        row
        for row in current_candidates
        if row["title"]
        == "Medical World Model: From Passive Prediction to Active Simulation in Medicine"
    )
    selected.append(("publisher_policy_correction", policy_record))

    fieldnames = [
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
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for stratum, row in selected:
        uid = record_uid(row)
        if uid in seen:
            continue
        seen.add(uid)
        output = {field: str(row.get(field, "")) for field in fieldnames}
        output["audit_id"] = uid
        output["stratum"] = stratum
        output["original_exclusion_reason"] = str(
            row.get("exclusion_reason", "")
        )
        rows.append(output)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["stratum"]] = counts.get(row["stratum"], 0) + 1
    summary = {
        "seed": args.seed,
        "excluded_phrase_absent": len(phrase_absent),
        "alternate_dynamics_enriched_total": len(enriched),
        "phrase_absent_remainder": len(phrase_remainder),
        "excluded_medical_term_absent": len(medical_absent),
        "audit_records": len(rows),
        "audit_strata": counts,
    }
    (args.output.parent / "sampling-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
