#!/usr/bin/env python3
"""Merge exact-identifier/title matches across provisional inclusion sources.

This script does not perform fuzzy publication-lineage adjudication. It creates
an auditable exact-match ledger and flags groups that still require manual
lineage review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize_doi(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    return value


def normalize_arxiv(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"^(?:arxiv:|https?://arxiv\.org/(?:abs|pdf)/)", "", value)
    return value.removesuffix(".pdf")


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def identity_keys(row: dict[str, str]) -> set[str]:
    keys: set[str] = set()
    doi = normalize_doi(row.get("doi", ""))
    arxiv_id = normalize_arxiv(row.get("arxiv_id", ""))
    title = normalize_title(row.get("title", ""))
    if doi:
        keys.add(f"doi:{doi}")
    if arxiv_id:
        keys.add(f"arxiv:{arxiv_id}")
    if title:
        keys.add(f"title:{title}")
    return keys


def row_id(row: dict[str, str]) -> str:
    return row.get("candidate_id") or row.get("audit_id") or ""


def corpus_type(row: dict[str, str]) -> str:
    return row.get("final_corpus_type") or row.get("corpus_type") or ""


def canonical_score(item: dict[str, object]) -> tuple[int, ...]:
    row = item["row"]
    assert isinstance(row, dict)
    record_type = str(row.get("record_type", "")).lower()
    source_status = str(row.get("source_status", "")).lower()
    peer_reviewed = int(
        record_type
        in {
            "article",
            "journal-article",
            "conference-paper",
            "proceedings-article",
        }
        and "preprint" not in source_status
    )
    existing_stable_id = int(str(row_id(row)).startswith("MWM-"))
    fields_present = sum(
        bool(str(row.get(field, "")).strip())
        for field in (
            "title",
            "abstract",
            "authors",
            "year",
            "publication_date",
            "venue",
            "doi",
            "arxiv_id",
            "url",
        )
    )
    source_priority = -int(item["source_index"])
    return existing_stable_id, peer_reviewed, fields_present, source_priority


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        lroot, rroot = self.find(left), self.find(right)
        if lroot != rroot:
            self.parent[rroot] = lroot


def stable_new_id(keys: set[str], title: str) -> str:
    identity = sorted(keys)[0] if keys else normalize_title(title)
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:10].upper()
    return f"MWM-X{digest}"


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Repeat as LABEL=PATH; earlier sources have canonical priority.",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    items: list[dict[str, object]] = []
    for source_index, specification in enumerate(args.source):
        if "=" not in specification:
            raise ValueError(f"Invalid source specification: {specification}")
        label, path_text = specification.split("=", 1)
        path = Path(path_text)
        for row in read(path):
            if row.get("final_decision") not in {"", None, "include"}:
                continue
            if corpus_type(row) not in {"empirical", "review"}:
                continue
            items.append(
                {
                    "source_index": source_index,
                    "source_label": label,
                    "source_path": str(path),
                    "row": row,
                    "keys": identity_keys(row),
                }
            )
    if not items:
        raise ValueError("No included records were loaded.")

    union = UnionFind(len(items))
    key_owner: dict[str, int] = {}
    for index, item in enumerate(items):
        keys = item["keys"]
        assert isinstance(keys, set)
        for key in keys:
            if key in key_owner:
                union.union(index, key_owner[key])
            else:
                key_owner[key] = index

    groups: dict[int, list[dict[str, object]]] = {}
    for index, item in enumerate(items):
        groups.setdefault(union.find(index), []).append(item)

    canonical_rows: list[dict[str, str]] = []
    ledger_rows: list[dict[str, str]] = []
    for members in groups.values():
        canonical_item = max(members, key=canonical_score)
        canonical = canonical_item["row"]
        assert isinstance(canonical, dict)
        all_keys: set[str] = set()
        for member in members:
            keys = member["keys"]
            assert isinstance(keys, set)
            all_keys.update(keys)
        stable_id = row_id(canonical)
        if not stable_id.startswith("MWM-"):
            stable_id = stable_new_id(all_keys, canonical.get("title", ""))

        types = {corpus_type(member["row"]) for member in members}
        titles = {
            str(member["row"].get("title", "")).strip()
            for member in members
            if str(member["row"].get("title", "")).strip()
        }
        dois = {
            normalize_doi(str(member["row"].get("doi", "")))
            for member in members
            if normalize_doi(str(member["row"].get("doi", "")))
        }
        arxiv_ids = {
            normalize_arxiv(str(member["row"].get("arxiv_id", "")))
            for member in members
            if normalize_arxiv(str(member["row"].get("arxiv_id", "")))
        }
        title_variants = {normalize_title(title) for title in titles}
        manual_lineage_review = (
            len(types) > 1
            or len(dois) > 1
            or len(arxiv_ids) > 1
            or len(title_variants) > 1
        )
        final_type = next(iter(types)) if len(types) == 1 else "conflict"
        source_labels = sorted(
            {str(member["source_label"]) for member in members}
        )
        source_ids = sorted(
            {
                row_id(member["row"])
                for member in members
                if row_id(member["row"])
            }
        )
        canonical_rows.append(
            {
                "candidate_id": stable_id,
                "title": canonical.get("title", ""),
                "abstract": canonical.get("abstract", ""),
                "final_corpus_type": final_type,
                "authors": canonical.get("authors", ""),
                "year": canonical.get("year", ""),
                "publication_date": canonical.get("publication_date", ""),
                "venue": canonical.get("venue", ""),
                "doi": canonical.get("doi", ""),
                "arxiv_id": canonical.get("arxiv_id", ""),
                "url": canonical.get("url", ""),
                "record_type": canonical.get("record_type", ""),
                "sources": canonical.get("sources", ""),
                "query_labels": canonical.get("query_labels", ""),
                "source_status": canonical.get("source_status", ""),
                "final_decision": "include",
                "final_reason_code": canonical.get(
                    "final_reason_code",
                    (
                        "include_empirical"
                        if final_type == "empirical"
                        else "include_review"
                    ),
                ),
                "resolution_route": "merged_inclusion_sources",
                "adjudication_rationale": canonical.get(
                    "adjudication_rationale", ""
                ),
                "source_routes": ";".join(source_labels),
                "source_record_ids": ";".join(source_ids),
                "exact_match_group_size": str(len(members)),
                "manual_lineage_review_required": (
                    "yes" if manual_lineage_review else "no"
                ),
            }
        )
        for member in members:
            source_row = member["row"]
            assert isinstance(source_row, dict)
            ledger_rows.append(
                {
                    "candidate_id": stable_id,
                    "source_label": str(member["source_label"]),
                    "source_path": str(member["source_path"]),
                    "source_record_id": row_id(source_row),
                    "source_title": source_row.get("title", ""),
                    "source_corpus_type": corpus_type(source_row),
                    "source_doi": source_row.get("doi", ""),
                    "source_arxiv_id": source_row.get("arxiv_id", ""),
                    "selected_as_canonical": (
                        "yes" if member is canonical_item else "no"
                    ),
                }
            )

    canonical_rows.sort(key=lambda row: (row["final_corpus_type"], row["title"]))
    ledger_rows.sort(key=lambda row: (row["candidate_id"], row["source_label"]))
    canonical_fields = [
        "candidate_id",
        "title",
        "abstract",
        "final_corpus_type",
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
        "final_decision",
        "final_reason_code",
        "resolution_route",
        "adjudication_rationale",
        "source_routes",
        "source_record_ids",
        "exact_match_group_size",
        "manual_lineage_review_required",
    ]
    ledger_fields = [
        "candidate_id",
        "source_label",
        "source_path",
        "source_record_id",
        "source_title",
        "source_corpus_type",
        "source_doi",
        "source_arxiv_id",
        "selected_as_canonical",
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write(args.output_dir / "provisional-included.csv", canonical_rows, canonical_fields)
    write(args.output_dir / "source-record-ledger.csv", ledger_rows, ledger_fields)
    counts = Counter(row["final_corpus_type"] for row in canonical_rows)
    summary = {
        "source_records": len(items),
        "exact_match_groups": len(canonical_rows),
        "corpus_types": dict(sorted(counts.items())),
        "multi_record_groups": sum(
            int(row["exact_match_group_size"]) > 1 for row in canonical_rows
        ),
        "manual_lineage_review_groups": sum(
            row["manual_lineage_review_required"] == "yes"
            for row in canonical_rows
        ),
        "status": "provisional_until_all_search_corrections_complete",
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
