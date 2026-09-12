#!/usr/bin/env python3
"""Run a public-database supplement without requiring the phrase world model."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

import search_literature as base


ALT_QUERIES = [
    '"model-based reinforcement learning" medical',
    '"model-based reinforcement learning" surgical',
    '"patient simulator" clinical',
    '"clinical digital twin" intervention',
    '"medical digital twin" trajectory',
    '"latent dynamics" medical',
    '"latent dynamics" physiological',
    '"intervention-conditioned forecasting" clinical',
    '"world-action model" surgical',
    '"cell world model"',
    '"virtual cell" temporal dynamics',
    '"disease progression model" generative intervention',
    '"patient trajectory" autoregressive',
    '"physiological trajectory" forecasting',
]
PUBMED_ALT_QUERY = (
    "("
    '("model-based reinforcement learning"[Title/Abstract]) OR '
    '("patient simulator"[Title/Abstract]) OR '
    '("clinical digital twin"[Title/Abstract]) OR '
    '("medical digital twin"[Title/Abstract]) OR '
    '("latent dynamics"[Title/Abstract]) OR '
    '("intervention-conditioned forecasting"[Title/Abstract]) OR '
    '("world-action model"[Title/Abstract]) OR '
    '("cell world model"[Title/Abstract]) OR '
    '("disease progression model"[Title/Abstract])'
    ") AND ("
    "medical[Title/Abstract] OR clinical[Title/Abstract] OR "
    "patient[Title/Abstract] OR health[Title/Abstract] OR "
    "surgical[Title/Abstract] OR physiological[Title/Abstract] OR "
    "cell[Title/Abstract] OR treatment[Title/Abstract] OR "
    "intervention[Title/Abstract]"
    ")"
)
EUROPE_PMC_ALT_QUERY = (
    "("
    '"model-based reinforcement learning" OR "patient simulator" OR '
    '"clinical digital twin" OR "medical digital twin" OR '
    '"latent dynamics" OR "intervention-conditioned forecasting" OR '
    '"world-action model" OR "cell world model" OR '
    '"disease progression model"'
    ") AND (medical OR clinical OR patient OR health OR surgical OR "
    "physiological OR cell OR treatment OR intervention)"
)
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
DYNAMICS_RE = re.compile(
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


def identity_keys(record: base.Record | dict[str, object]) -> set[str]:
    def get(name: str) -> str:
        if isinstance(record, dict):
            return str(record.get(name, "") or "")
        return str(getattr(record, name, "") or "")

    keys: set[str] = set()
    doi = base.normalize_doi(get("doi"))
    arxiv_id = get("arxiv_id")
    title = base.normalize_title(get("title"))
    if doi:
        keys.add(f"doi:{doi}")
    if arxiv_id:
        keys.add(f"arxiv:{arxiv_id}")
    if title:
        keys.add(f"title:{title}")
    return keys


def record_uid(record: base.Record) -> str:
    identity = sorted(identity_keys(record))
    text = identity[0] if identity else record.url or record.title
    return "ALT-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def load_existing_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            keys.update(identity_keys(json.loads(line)))
    return keys


def write_candidates(path: Path, records: list[base.Record]) -> None:
    fields = [
        "audit_id",
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
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            payload = asdict(record)
            writer.writerow(
                {
                    "audit_id": record_uid(record),
                    "title": record.title,
                    "abstract": record.abstract,
                    "authors": record.authors,
                    "year": record.year,
                    "publication_date": record.publication_date,
                    "venue": record.venue,
                    "doi": record.doi,
                    "arxiv_id": record.arxiv_id,
                    "url": record.url,
                    "record_type": record.record_type,
                    "sources": ";".join(payload["sources"]),
                    "query_labels": ";".join(payload["query_labels"]),
                    "source_status": record.source_status,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--existing-deduplicated", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cutoff", default="2026-09-12")
    parser.add_argument(
        "--sources",
        default="pubmed,europe_pmc,openalex,crossref",
        help="Comma-separated public sources to query.",
    )
    args = parser.parse_args()

    base.DISCOVERY_QUERIES = ALT_QUERIES
    base.PUBMED_QUERY = PUBMED_ALT_QUERY
    base.EUROPE_PMC_QUERY = EUROPE_PMC_ALT_QUERY
    client = base.SearchClient()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.output_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    source_functions = [
        ("pubmed", base.search_pubmed),
        ("europe_pmc", base.search_europe_pmc),
        ("openalex", base.search_openalex),
        ("crossref", base.search_crossref),
    ]
    selected_sources = {
        value.strip() for value in args.sources.split(",") if value.strip()
    }
    available_sources = {name for name, _ in source_functions}
    unknown = selected_sources - available_sources
    if unknown:
        raise ValueError(f"Unknown sources: {sorted(unknown)}")
    records: list[base.Record] = []
    logs: dict[str, object] = {}
    failures: dict[str, str] = {}
    for name, function in source_functions:
        if name not in selected_sources:
            continue
        try:
            source_records, source_log = function(client, args.cutoff)
            records.extend(source_records)
            logs[name] = source_log
            base.write_jsonl(cache_dir / f"{name}.jsonl", source_records)
        except Exception as exc:
            failures[name] = f"{type(exc).__name__}: {exc}"

    merged = base.merge_records(records)
    existing_keys = load_existing_keys(args.existing_deduplicated)
    novel = [
        record
        for record in merged
        if not identity_keys(record).intersection(existing_keys)
    ]
    candidates = []
    for record in novel:
        text = f"{record.title} {record.abstract}"
        if DOMAIN_RE.search(text) and DYNAMICS_RE.search(text):
            candidates.append(record)
    candidates.sort(key=lambda record: (-int(record.year or 0), record.title.lower()))

    base.write_jsonl(args.output_dir / "all-deduplicated.jsonl", merged)
    base.write_jsonl(args.output_dir / "novel-records.jsonl", novel)
    base.write_jsonl(args.output_dir / "candidate-records.jsonl", candidates)
    write_candidates(args.output_dir / "candidates.csv", candidates)
    summary = {
        "run_date": "2026-09-12",
        "cutoff": args.cutoff,
        "queries": ALT_QUERIES,
        "source_logs": logs,
        "source_failures": failures,
        "raw_records": len(records),
        "deduplicated_records": len(merged),
        "novel_vs_primary_search": len(novel),
        "alternate_term_candidates": len(candidates),
        "publisher_or_venue_exclusions": 0,
    }
    (args.output_dir / "search-log.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 1 if failures and not candidates else 0


if __name__ == "__main__":
    raise SystemExit(main())
