#!/usr/bin/env python3
"""Reproducible discovery search for empirical medical world models.

The script queries public scholarly APIs, stores source-level records, applies
the review's public inclusion boundary, and writes a deduplicated screening
corpus. It performs discovery only; inclusion decisions belong to screening.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


USER_AGENT = "medical-world-model-scoping-review/0.1"
START_DATE = "2020-01-01"
DEFAULT_CUTOFF = "2026-09-12"

WORLD_RE = re.compile(r"\bworld[\s-]+models?\b", re.IGNORECASE)
MEDICAL_RE = re.compile(
    r"\b("
    r"medical|medicine|clinical|clinic|patient|health|healthcare|hospital|"
    r"ehr|electronic health|physiolog|surg|echocardi|ultrasound|radiolog|"
    r"oncolog|tumou?r|glioma|cardiac|brain|treatment|intervention|therapy|"
    r"disease|intensive care|critical care|biomedical"
    r")",
    re.IGNORECASE,
)
PUBMED_QUERY = (
    '("world model"[Title/Abstract] OR "world models"[Title/Abstract] '
    'OR "world-model"[Title/Abstract] OR "world-models"[Title/Abstract]) '
    "AND (medical[Title/Abstract] OR clinical[Title/Abstract] "
    "OR patient[Title/Abstract] OR healthcare[Title/Abstract] "
    "OR health[Title/Abstract] OR surgical[Title/Abstract] "
    "OR surgery[Title/Abstract] OR echocardiography[Title/Abstract] "
    "OR ultrasound[Title/Abstract] OR physiological[Title/Abstract] "
    "OR treatment[Title/Abstract] OR intervention[Title/Abstract] "
    'OR "electronic health record"[Title/Abstract])'
)

EUROPE_PMC_QUERY = (
    '("world model" OR "world models" OR "world-model" OR "world-models") '
    "AND (medical OR clinical OR patient OR healthcare OR health OR surgical "
    "OR surgery OR echocardiography OR ultrasound OR physiological "
    'OR treatment OR intervention OR "electronic health record")'
)

DISCOVERY_QUERIES = [
    '"medical world model"',
    '"clinical world model"',
    '"patient world model"',
    '"healthcare world model"',
    '"surgical world model"',
    '"world model" medicine',
    '"world model" clinical',
    '"world model" patient',
    '"world model" treatment',
    '"world model" echocardiography',
    '"world model" EHR',
    '"world model" physiology',
]


@dataclass
class Record:
    title: str
    abstract: str = ""
    authors: str = ""
    year: str = ""
    publication_date: str = ""
    venue: str = ""
    doi: str = ""
    arxiv_id: str = ""
    url: str = ""
    record_type: str = ""
    source_ids: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    query_labels: list[str] = field(default_factory=list)
    source_status: str = ""
    policy_excluded: bool = False
    exclusion_reason: str = ""


class SearchClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def get_json(
        self, url: str, *, params: dict[str, Any] | None = None, attempts: int = 5
    ) -> dict[str, Any]:
        for attempt in range(attempts):
            response = self.session.get(url, params=params, timeout=90)
            if response.status_code == 429 or response.status_code >= 500:
                if attempt + 1 == attempts:
                    response.raise_for_status()
                time.sleep(min(2**attempt, 16))
                continue
            response.raise_for_status()
            return response.json()
        raise RuntimeError(f"Failed to retrieve {url}")

    def get_text(
        self, url: str, *, params: dict[str, Any] | None = None, attempts: int = 5
    ) -> str:
        for attempt in range(attempts):
            response = self.session.get(url, params=params, timeout=90)
            if response.status_code == 429 or response.status_code >= 500:
                if attempt + 1 == attempts:
                    response.raise_for_status()
                retry_after = response.headers.get("Retry-After", "")
                delay = int(retry_after) if retry_after.isdigit() else min(5 * (2**attempt), 60)
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response.text
        raise RuntimeError(f"Failed to retrieve {url}")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def normalize_doi(doi: str) -> str:
    return doi.lower().strip().removeprefix("https://doi.org/").removeprefix("doi:")


def extract_arxiv_id(text: str) -> str:
    match = re.search(r"(?:arxiv:|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})(?:v\d+)?", text, re.I)
    return match.group(1) if match else ""


def reconstruct_openalex_abstract(inverted: dict[str, list[int]] | None) -> str:
    if not inverted:
        return ""
    positioned: list[tuple[int, str]] = []
    for token, positions in inverted.items():
        positioned.extend((position, token) for position in positions)
    return " ".join(token for _, token in sorted(positioned))


def is_core_candidate(record: Record) -> tuple[bool, str]:
    text = f"{record.title} {record.abstract}"
    if not WORLD_RE.search(text):
        return False, "world-model phrase absent from title and abstract"
    if not MEDICAL_RE.search(text):
        return False, "medical-domain term absent from title and abstract"
    return True, ""


def parse_pubmed_articles(xml_text: str, query_label: str) -> list[Record]:
    root = ET.fromstring(xml_text)
    records: list[Record] = []
    for article in root.findall(".//PubmedArticle"):
        citation = article.find("MedlineCitation")
        if citation is None:
            continue
        article_node = citation.find("Article")
        if article_node is None:
            continue
        title = clean_text("".join(article_node.findtext("ArticleTitle", default="")))
        abstract_parts: list[str] = []
        for abstract in article_node.findall(".//AbstractText"):
            label = abstract.attrib.get("Label", "")
            body = clean_text("".join(abstract.itertext()))
            abstract_parts.append(f"{label}: {body}" if label else body)
        authors: list[str] = []
        for author in article_node.findall(".//Author"):
            collective = author.findtext("CollectiveName")
            if collective:
                authors.append(clean_text(collective))
                continue
            family = clean_text(author.findtext("LastName"))
            given = clean_text(author.findtext("ForeName"))
            name = " ".join(part for part in (given, family) if part)
            if name:
                authors.append(name)
        pmid = clean_text(citation.findtext("PMID"))
        doi = ""
        for identifier in article.findall(".//ArticleId"):
            if identifier.attrib.get("IdType") == "doi":
                doi = clean_text(identifier.text)
                break
        journal = clean_text(article_node.findtext("./Journal/Title"))
        pub_date = article_node.find("./Journal/JournalIssue/PubDate")
        year = clean_text(pub_date.findtext("Year")) if pub_date is not None else ""
        if not year and pub_date is not None:
            year = clean_text(pub_date.findtext("MedlineDate"))[:4]
        records.append(
            Record(
                title=title,
                abstract=" ".join(abstract_parts),
                authors="; ".join(authors),
                year=year,
                publication_date=year,
                venue=journal,
                doi=normalize_doi(doi),
                arxiv_id=extract_arxiv_id(" ".join(abstract_parts)),
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                record_type="journal-article",
                source_ids=[pmid] if pmid else [],
                sources=["pubmed"],
                query_labels=[query_label],
                source_status="indexed",
            )
        )
    return records


def search_pubmed(client: SearchClient, cutoff: str) -> tuple[list[Record], dict[str, Any]]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    search = client.get_json(
        f"{base}/esearch.fcgi",
        params={
            "db": "pubmed",
            "term": PUBMED_QUERY,
            "retmode": "json",
            "retmax": 10000,
            "datetype": "pdat",
            "mindate": START_DATE.replace("-", "/"),
            "maxdate": cutoff.replace("-", "/"),
        },
    )
    ids = search.get("esearchresult", {}).get("idlist", [])
    records: list[Record] = []
    for offset in range(0, len(ids), 200):
        batch = ids[offset : offset + 200]
        xml_text = client.get_text(
            f"{base}/efetch.fcgi",
            params={"db": "pubmed", "id": ",".join(batch), "retmode": "xml"},
        )
        records.extend(parse_pubmed_articles(xml_text, "pubmed_core"))
        time.sleep(0.35)
    return records, {
        "query": PUBMED_QUERY,
        "reported_count": int(search.get("esearchresult", {}).get("count", 0)),
        "retrieved_count": len(records),
    }


def search_europe_pmc(client: SearchClient, cutoff: str) -> tuple[list[Record], dict[str, Any]]:
    query = f"({EUROPE_PMC_QUERY}) AND FIRST_PDATE:[{START_DATE} TO {cutoff}]"
    cursor = "*"
    records: list[Record] = []
    hit_count = 0
    while cursor:
        payload = client.get_json(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={
                "query": query,
                "format": "json",
                "resultType": "core",
                "pageSize": 1000,
                "cursorMark": cursor,
            },
        )
        hit_count = int(payload.get("hitCount", 0))
        for item in payload.get("resultList", {}).get("result", []):
            source_id = clean_text(item.get("id"))
            doi = normalize_doi(clean_text(item.get("doi")))
            records.append(
                Record(
                    title=clean_text(item.get("title")),
                    abstract=clean_text(item.get("abstractText")),
                    authors=clean_text(item.get("authorString")),
                    year=clean_text(item.get("pubYear")),
                    publication_date=clean_text(item.get("firstPublicationDate")),
                    venue=clean_text(item.get("journalTitle")),
                    doi=doi,
                    arxiv_id=extract_arxiv_id(
                        " ".join(
                            [
                                clean_text(item.get("title")),
                                clean_text(item.get("abstractText")),
                                clean_text(item.get("bookOrReportDetails")),
                            ]
                        )
                    ),
                    url=(
                        f"https://europepmc.org/article/{clean_text(item.get('source'))}/{source_id}"
                        if source_id
                        else ""
                    ),
                    record_type=clean_text(item.get("pubType")),
                    source_ids=[source_id] if source_id else [],
                    sources=["europe_pmc"],
                    query_labels=["europe_pmc_core"],
                    source_status="indexed",
                )
            )
        next_cursor = payload.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        if len(records) >= hit_count:
            break
        time.sleep(0.35)
    return records, {
        "query": query,
        "reported_count": hit_count,
        "retrieved_count": len(records),
    }


def search_openalex(client: SearchClient, cutoff: str) -> tuple[list[Record], dict[str, Any]]:
    records: list[Record] = []
    logs: list[dict[str, Any]] = []
    for query in DISCOVERY_QUERIES:
        cursor = "*"
        retrieved = 0
        reported_count = 0
        while cursor:
            payload = client.get_json(
                "https://api.openalex.org/works",
                params={
                    "search": query,
                    "filter": f"from_publication_date:{START_DATE},to_publication_date:{cutoff}",
                    "per-page": 200,
                    "cursor": cursor,
                },
            )
            reported_count = int(payload.get("meta", {}).get("count", 0))
            batch = payload.get("results", [])
            for item in batch:
                primary_location = item.get("primary_location") or {}
                source = primary_location.get("source") or {}
                open_access = item.get("open_access") or {}
                ids = item.get("ids") or {}
                doi = normalize_doi(clean_text(item.get("doi")))
                url = clean_text(
                    primary_location.get("landing_page_url")
                    or open_access.get("oa_url")
                    or ids.get("openalex")
                )
                authors = "; ".join(
                    clean_text(authorship.get("author", {}).get("display_name"))
                    for authorship in item.get("authorships", [])
                    if authorship.get("author", {}).get("display_name")
                )
                source_id = clean_text(item.get("id"))
                records.append(
                    Record(
                        title=clean_text(item.get("display_name")),
                        abstract=reconstruct_openalex_abstract(item.get("abstract_inverted_index")),
                        authors=authors,
                        year=clean_text(item.get("publication_year")),
                        publication_date=clean_text(item.get("publication_date")),
                        venue=clean_text(source.get("display_name")),
                        doi=doi,
                        arxiv_id=extract_arxiv_id(
                            " ".join(
                                [
                                    clean_text(item.get("display_name")),
                                    url,
                                    clean_text(ids.get("mag")),
                                ]
                            )
                        ),
                        url=url,
                        record_type=clean_text(item.get("type")),
                        source_ids=[source_id] if source_id else [],
                        sources=["openalex"],
                        query_labels=[query],
                        source_status=(
                            "open-access" if open_access.get("is_oa") else "indexed"
                        ),
                    )
                )
            retrieved += len(batch)
            next_cursor = payload.get("meta", {}).get("next_cursor")
            if not next_cursor or not batch or retrieved >= reported_count:
                break
            cursor = next_cursor
            if retrieved >= 1000:
                break
            time.sleep(1.0)
        logs.append(
            {
                "query": query,
                "reported_count": reported_count,
                "retrieved_count": retrieved,
            }
        )
        time.sleep(0.25)
    return records, {"queries": logs, "retrieved_count": len(records)}


def search_crossref(client: SearchClient, cutoff: str) -> tuple[list[Record], dict[str, Any]]:
    records: list[Record] = []
    logs: list[dict[str, Any]] = []
    for query in DISCOVERY_QUERIES:
        payload = client.get_json(
            "https://api.crossref.org/works",
            params={
                "query.bibliographic": query,
                "filter": f"from-pub-date:{START_DATE},until-pub-date:{cutoff}",
                "rows": 250,
                "select": (
                    "DOI,title,abstract,author,published,container-title,URL,type,"
                    "publisher"
                ),
            },
        )
        message = payload.get("message", {})
        items = message.get("items", [])
        for item in items:
            title_values = item.get("title") or []
            title = clean_text(title_values[0] if title_values else "")
            authors = "; ".join(
                " ".join(
                    part
                    for part in (
                        clean_text(author.get("given")),
                        clean_text(author.get("family")),
                    )
                    if part
                )
                for author in item.get("author", [])
            )
            date_parts = (
                item.get("published", {}).get("date-parts")
                or item.get("issued", {}).get("date-parts")
                or []
            )
            year = str(date_parts[0][0]) if date_parts and date_parts[0] else ""
            containers = item.get("container-title") or []
            venue = clean_text(containers[0] if containers else item.get("publisher"))
            source_id = normalize_doi(clean_text(item.get("DOI")))
            records.append(
                Record(
                    title=title,
                    abstract=clean_text(item.get("abstract")),
                    authors=authors,
                    year=year,
                    publication_date=year,
                    venue=venue,
                    doi=source_id,
                    arxiv_id=extract_arxiv_id(
                        " ".join([title, clean_text(item.get("URL")), clean_text(item.get("abstract"))])
                    ),
                    url=clean_text(item.get("URL")),
                    record_type=clean_text(item.get("type")),
                    source_ids=[source_id] if source_id else [],
                    sources=["crossref"],
                    query_labels=[query],
                    source_status="registered",
                )
            )
        logs.append(
            {
                "query": query,
                "reported_count": int(message.get("total-results", 0)),
                "retrieved_count": len(items),
            }
        )
        time.sleep(0.25)
    return records, {"queries": logs, "retrieved_count": len(records)}


def parse_arxiv(xml_text: str, query_label: str) -> list[Record]:
    root = ET.fromstring(xml_text)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    records: list[Record] = []
    for entry in root.findall("atom:entry", ns):
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        abstract = clean_text(entry.findtext("atom:summary", default="", namespaces=ns))
        entry_id = clean_text(entry.findtext("atom:id", default="", namespaces=ns))
        arxiv_id = extract_arxiv_id(entry_id)
        authors = "; ".join(
            clean_text(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        )
        published = clean_text(entry.findtext("atom:published", default="", namespaces=ns))
        categories = ", ".join(
            category.attrib.get("term", "")
            for category in entry.findall("atom:category", ns)
            if category.attrib.get("term")
        )
        doi = clean_text(entry.findtext("arxiv:doi", default="", namespaces=ns))
        records.append(
            Record(
                title=title,
                abstract=abstract,
                authors=authors,
                year=published[:4],
                publication_date=published[:10],
                venue=categories,
                doi=normalize_doi(doi),
                arxiv_id=arxiv_id,
                url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else entry_id,
                record_type="preprint",
                source_ids=[arxiv_id] if arxiv_id else [],
                sources=["arxiv"],
                query_labels=[query_label],
                source_status="preprint",
            )
        )
    return records


def search_arxiv_html(
    client: SearchClient,
    cutoff: str,
    *,
    api_error: str,
) -> tuple[list[Record], dict[str, Any]]:
    query = '"world model" AND (medical OR clinical OR surgical OR patient)'
    html_text = client.get_text(
        "https://arxiv.org/search/",
        params={
            "query": query,
            "searchtype": "all",
            "abstracts": "show",
            "order": "-announced_date_first",
            "size": 200,
        },
    )
    soup = BeautifulSoup(html_text, "html.parser")
    records: list[Record] = []
    for item in soup.select("li.arxiv-result"):
        identifier_node = item.select_one("p.list-title a")
        title_node = item.select_one("p.title")
        abstract_node = item.select_one("span.abstract-full")
        date_node = item.select_one("p.is-size-7")
        if identifier_node is None or title_node is None:
            continue
        arxiv_id = clean_text(identifier_node.get_text(" ", strip=True)).removeprefix(
            "arXiv:"
        )
        title = clean_text(title_node.get_text(" ", strip=True))
        abstract = clean_text(
            abstract_node.get_text(" ", strip=True) if abstract_node else ""
        ).removesuffix("△ Less")
        authors_node = item.select_one("p.authors")
        authors = "; ".join(
            clean_text(author.get_text(" ", strip=True))
            for author in authors_node.select("a")
        ) if authors_node else ""
        date_text = clean_text(date_node.get_text(" ", strip=True) if date_node else "")
        submitted_match = re.search(
            r"Submitted\s+(\d{1,2}\s+[A-Za-z]+,\s+\d{4})", date_text
        )
        publication_date = ""
        if submitted_match:
            publication_date = datetime.strptime(
                submitted_match.group(1), "%d %B, %Y"
            ).date().isoformat()
        if publication_date and not (START_DATE <= publication_date <= cutoff):
            continue
        categories = ", ".join(
            clean_text(tag.get_text(" ", strip=True))
            for tag in item.select("div.tags span.tag")
        )
        records.append(
            Record(
                title=title,
                abstract=abstract,
                authors=authors,
                year=publication_date[:4],
                publication_date=publication_date,
                venue=categories,
                doi=f"10.48550/arxiv.{arxiv_id}" if arxiv_id else "",
                arxiv_id=arxiv_id,
                url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
                record_type="preprint",
                source_ids=[arxiv_id] if arxiv_id else [],
                sources=["arxiv"],
                query_labels=["arxiv_html_fallback"],
                source_status="preprint",
            )
        )
    return records, {
        "retrieval_mode": "html_fallback",
        "query": query,
        "reported_count": len(soup.select("li.arxiv-result")),
        "retrieved_count": len(records),
        "api_error": api_error,
    }


def search_arxiv(client: SearchClient, cutoff: str) -> tuple[list[Record], dict[str, Any]]:
    query = (
        'all:"world model" AND (all:medical OR all:clinical OR all:patient '
        "OR all:healthcare OR all:health OR all:surgical OR all:surgery "
        "OR all:echocardiography OR all:ultrasound OR all:physiology "
        "OR all:treatment OR all:intervention OR all:EHR)"
    )
    all_records: list[Record] = []
    start = 0
    batch_size = 100
    total_results = 0
    try:
        while True:
            xml_text = client.get_text(
                "https://export.arxiv.org/api/query",
                params={
                    "search_query": query,
                    "start": start,
                    "max_results": batch_size,
                    "sortBy": "submittedDate",
                    "sortOrder": "descending",
                },
            )
            root = ET.fromstring(xml_text)
            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
            }
            if start == 0:
                total_results = int(
                    root.findtext(
                        "opensearch:totalResults", default="0", namespaces=ns
                    )
                )
            batch = parse_arxiv(xml_text, "arxiv_core")
            for record in batch:
                if record.publication_date and record.publication_date < START_DATE:
                    continue
                if record.publication_date and record.publication_date > cutoff:
                    continue
                all_records.append(record)
            if len(batch) < batch_size or start + batch_size >= total_results:
                break
            start += batch_size
            if start >= 1000:
                break
            time.sleep(3.1)
    except (requests.RequestException, ET.ParseError) as exc:
        return search_arxiv_html(
            client,
            cutoff,
            api_error=f"{type(exc).__name__}: {exc}",
        )
    return all_records, {
        "retrieval_mode": "api",
        "query": query,
        "reported_count": total_results,
        "retrieved_count": len(all_records),
    }


def merge_records(records: Iterable[Record]) -> list[Record]:
    by_key: dict[str, Record] = {}
    aliases: dict[str, str] = {}

    def keys_for(record: Record) -> list[str]:
        keys: list[str] = []
        if record.doi:
            keys.append(f"doi:{normalize_doi(record.doi)}")
        if record.arxiv_id:
            keys.append(f"arxiv:{record.arxiv_id}")
        normalized = normalize_title(record.title)
        if normalized:
            keys.append(f"title:{normalized}")
        return keys

    for record in records:
        record.title = clean_text(record.title)
        record.abstract = clean_text(record.abstract)
        record.doi = normalize_doi(record.doi)
        eligible, reason = is_core_candidate(record)
        record.policy_excluded = not eligible and "policy-excluded" in reason
        record.exclusion_reason = reason
        record_keys = keys_for(record)
        canonical_key = next((aliases[key] for key in record_keys if key in aliases), "")
        if not canonical_key:
            canonical_key = record_keys[0] if record_keys else f"record:{len(by_key)}"
            by_key[canonical_key] = record
        else:
            current = by_key[canonical_key]
            for field_name in (
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
                "source_status",
            ):
                old = getattr(current, field_name)
                new = getattr(record, field_name)
                if not old or (field_name == "abstract" and len(new) > len(old)):
                    setattr(current, field_name, new)
            current.source_ids = sorted(set(current.source_ids + record.source_ids))
            current.sources = sorted(set(current.sources + record.sources))
            current.query_labels = sorted(set(current.query_labels + record.query_labels))
            current.policy_excluded = current.policy_excluded or record.policy_excluded
            if not current.exclusion_reason or (
                current.exclusion_reason.startswith("world-model")
                and not record.exclusion_reason
            ):
                current.exclusion_reason = record.exclusion_reason
        for key in record_keys:
            aliases[key] = canonical_key

    merged = list(by_key.values())
    merged.sort(
        key=lambda item: (
            item.exclusion_reason != "",
            -(int(item.year) if item.year.isdigit() else 0),
            item.title.lower(),
        )
    )
    return merged


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[Record]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[Record]:
    records: list[Record] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(Record(**json.loads(line)))
    return records


def candidate_identity_keys(record: Record) -> list[str]:
    keys: list[str] = []
    if record.doi:
        keys.append(f"doi:{normalize_doi(record.doi)}")
    if record.arxiv_id:
        keys.append(f"arxiv:{record.arxiv_id}")
    normalized = normalize_title(record.title)
    if normalized:
        keys.append(f"title:{normalized}")
    return keys


def load_existing_candidate_ids(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    mapping: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            record = Record(
                title=row.get("title", ""),
                doi=row.get("doi", ""),
                arxiv_id=row.get("arxiv_id", ""),
            )
            for key in candidate_identity_keys(record):
                mapping[key] = row["candidate_id"]
    return mapping


def write_csv(
    path: Path,
    records: Iterable[Record],
    *,
    existing_ids: dict[str, str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_ids = existing_ids or {}
    used_ids: set[str] = set()
    numeric_ids = [
        int(match.group(1))
        for candidate_id in existing_ids.values()
        if (match := re.fullmatch(r"MWM-(\d{4})", candidate_id))
    ]
    next_id = max(numeric_ids, default=0) + 1

    def stable_candidate_id(record: Record) -> str:
        nonlocal next_id
        candidate_id = next(
            (
                existing_ids[key]
                for key in candidate_identity_keys(record)
                if key in existing_ids and existing_ids[key] not in used_ids
            ),
            "",
        )
        if not candidate_id:
            while f"MWM-{next_id:04d}" in used_ids:
                next_id += 1
            candidate_id = f"MWM-{next_id:04d}"
            next_id += 1
        used_ids.add(candidate_id)
        return candidate_id

    fieldnames = [
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
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "candidate_id": stable_candidate_id(record),
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
                    "sources": ";".join(record.sources),
                    "query_labels": ";".join(record.query_labels),
                    "source_status": record.source_status,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Stable screening output directory.",
    )
    parser.add_argument("--cutoff", default=DEFAULT_CUTOFF)
    parser.add_argument(
        "--sources",
        default="all",
        help="Comma-separated source names to query, or 'all'.",
    )
    parser.add_argument(
        "--reuse-cache",
        action="store_true",
        help="Reuse cached records and prior source logs for unselected sources.",
    )
    args = parser.parse_args()

    cutoff_date = date.fromisoformat(args.cutoff)
    if cutoff_date > date(2026, 9, 12):
        raise SystemExit("Cutoff cannot be later than the current review date 2026-09-12.")

    output_dir = args.output_dir.resolve()
    cache_dir = output_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    client = SearchClient()

    source_functions = [
        ("pubmed", search_pubmed),
        ("europe_pmc", search_europe_pmc),
        ("openalex", search_openalex),
        ("crossref", search_crossref),
        ("arxiv", search_arxiv),
    ]
    available_sources = {name for name, _ in source_functions}
    selected_sources = (
        available_sources
        if args.sources == "all"
        else {name.strip() for name in args.sources.split(",") if name.strip()}
    )
    unknown_sources = selected_sources - available_sources
    if unknown_sources:
        raise SystemExit(f"Unknown sources: {sorted(unknown_sources)}")
    previous_log: dict[str, Any] = {}
    previous_log_path = output_dir / "search-log.json"
    if args.reuse_cache and previous_log_path.exists():
        previous_log = json.loads(previous_log_path.read_text(encoding="utf-8"))

    all_records: list[Record] = []
    source_logs: dict[str, Any] = {}
    failures: dict[str, str] = {}
    source_counts: dict[str, int] = {}
    source_modes: dict[str, str] = {}

    for source_name, search_function in source_functions:
        cache_path = cache_dir / f"{source_name}.jsonl"
        if source_name in selected_sources:
            try:
                records, log = search_function(client, args.cutoff)
                all_records.extend(records)
                source_logs[source_name] = log
                source_counts[source_name] = len(records)
                source_modes[source_name] = "queried"
                write_jsonl(cache_path, records)
            except Exception as exc:  # keep successful sources usable
                failures[source_name] = f"{type(exc).__name__}: {exc}"
        elif args.reuse_cache:
            if not cache_path.exists():
                failures[source_name] = f"Missing required cache: {cache_path}"
                continue
            records = read_jsonl(cache_path)
            all_records.extend(records)
            source_counts[source_name] = len(records)
            source_modes[source_name] = "reused_cache"
            source_logs[source_name] = previous_log.get("source_logs", {}).get(
                source_name
            ) or {
                "retrieval_mode": "reused_cache",
                "retrieved_count": len(records),
            }

    merged = merge_records(all_records)
    excluded = [record for record in merged if record.exclusion_reason]
    candidates = [record for record in merged if not record.exclusion_reason]

    candidate_csv_path = output_dir / "candidates.csv"
    existing_candidate_ids = load_existing_candidate_ids(candidate_csv_path)
    write_jsonl(output_dir / "all-deduplicated.jsonl", merged)
    write_jsonl(output_dir / "excluded-discovery.jsonl", excluded)
    write_jsonl(output_dir / "candidates.jsonl", candidates)
    write_csv(
        candidate_csv_path,
        candidates,
        existing_ids=existing_candidate_ids,
    )

    log = {
        "run_date": "2026-09-12",
        "start_date": START_DATE,
        "cutoff": args.cutoff,
        "user_agent": USER_AGENT,
        "source_logs": source_logs,
        "source_modes": source_modes,
        "source_failures": failures,
        "raw_record_count": len(all_records),
        "raw_source_counts": dict(sorted(source_counts.items())),
        "deduplicated_count": len(merged),
        "candidate_count": len(candidates),
        "discovery_exclusion_count": len(excluded),
        "discovery_exclusion_reasons": dict(
            sorted(
                (
                    reason,
                    sum(1 for record in excluded if record.exclusion_reason == reason),
                )
                for reason in sorted({record.exclusion_reason for record in excluded})
            )
        ),
        "notes": [
            "Discovery exclusions require both a world-model phrase and a medical-domain term in title or abstract.",
            "No publisher or venue is excluded at discovery; source quality is assessed after eligibility.",
            "Candidate inclusion still requires independent title/abstract and full-text screening.",
            "Scopus and Web of Science are not queried because authenticated subscriptions are unavailable in this environment.",
        ],
    }
    write_json(output_dir / "search-log.json", log)

    print(json.dumps(log, ensure_ascii=False, indent=2))
    return 1 if failures and not candidates else 0


if __name__ == "__main__":
    raise SystemExit(main())
