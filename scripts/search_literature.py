#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import xml.etree.ElementTree as ET
from typing import Any, Callable

from _common import (
    dump_json,
    dump_jsonl,
    extract_idea,
    fetch_json,
    fetch_text,
    now_iso,
    output_dir_from_args,
    parse_query_families,
    read_text,
    slugify,
    url_with_query,
)

Searcher = Callable[[str, int, int], list[dict[str, Any]]]


def with_retries(fn: Callable[[], list[dict[str, Any]]], retries: int) -> list[dict[str, Any]]:
    last_exc: Exception | None = None
    attempts = max(1, retries + 1)
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # Source failures are reported in search_manifest.json.
            last_exc = exc
            if attempt < attempts:
                time.sleep(min(2.0, 0.5 * attempt))
    assert last_exc is not None
    raise last_exc


def search_openalex(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    url = url_with_query(
        "https://api.openalex.org/works",
        {
            "search": query,
            "per-page": max(1, min(limit, 50)),
            "sort": "cited_by_count:desc",
        },
    )
    return fetch_json(url, timeout=timeout).get("results", [])


def search_semantic_scholar(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    url = url_with_query(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        {
            "query": query,
            "limit": max(1, min(limit, 100)),
            "fields": "title,authors,year,venue,externalIds,url,abstract,citationCount,publicationTypes,isOpenAccess,fieldsOfStudy",
        },
    )
    return fetch_json(url, timeout=timeout).get("data", [])


def search_crossref(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    url = url_with_query(
        "https://api.crossref.org/works",
        {
            "query.bibliographic": query,
            "rows": max(1, min(limit, 50)),
        },
    )
    return fetch_json(url, timeout=timeout).get("message", {}).get("items", [])


def search_pubmed(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    search_url = url_with_query(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max(1, min(limit, 100)),
        },
    )
    ids = fetch_json(search_url, timeout=timeout).get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    summary_url = url_with_query(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
        {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
        },
    )
    result = fetch_json(summary_url, timeout=timeout).get("result", {})
    return [result[pmid] for pmid in ids if isinstance(result.get(pmid), dict)]


def search_arxiv(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    url = url_with_query(
        "https://export.arxiv.org/api/query",
        {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max(1, min(limit, 50)),
            "sortBy": "relevance",
        },
    )
    text = fetch_text(url, timeout=timeout)
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    records: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        doi = entry.findtext("arxiv:doi", default="", namespaces=ns)
        records.append(
            {
                "id": entry.findtext("atom:id", default="", namespaces=ns),
                "title": entry.findtext("atom:title", default="", namespaces=ns),
                "summary": entry.findtext("atom:summary", default="", namespaces=ns),
                "published": entry.findtext("atom:published", default="", namespaces=ns),
                "updated": entry.findtext("atom:updated", default="", namespaces=ns),
                "doi": doi,
                "authors": [
                    author.findtext("atom:name", default="", namespaces=ns)
                    for author in entry.findall("atom:author", ns)
                ],
                "categories": [
                    category.attrib.get("term", "")
                    for category in entry.findall("atom:category", ns)
                ],
            }
        )
    return records


def search_eric(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    url = url_with_query(
        "https://api.ies.ed.gov/eric/",
        {
            "search": query,
            "format": "json",
            "rows": max(1, min(limit, 50)),
        },
    )
    data = fetch_json(url, timeout=timeout)
    return data.get("response", {}).get("docs", []) or data.get("docs", [])


def search_clinicaltrials(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    url = url_with_query(
        "https://clinicaltrials.gov/api/v2/studies",
        {
            "query.term": query,
            "pageSize": max(1, min(limit, 100)),
        },
    )
    return fetch_json(url, timeout=timeout).get("studies", [])


def search_papers_with_code(query: str, limit: int, timeout: int) -> list[dict[str, Any]]:
    url = url_with_query(
        "https://paperswithcode.com/api/v1/papers/",
        {
            "q": query,
            "page_size": max(1, min(limit, 50)),
        },
    )
    return fetch_json(url, timeout=timeout).get("results", [])


CORE_SOURCES: dict[str, Searcher] = {
    "OpenAlex": search_openalex,
    "Semantic Scholar": search_semantic_scholar,
    "Crossref": search_crossref,
}

CONDITIONAL_SOURCES: dict[str, Searcher] = {
    "PubMed / NCBI E-utilities": search_pubmed,
    "arXiv": search_arxiv,
    "ERIC": search_eric,
    "ClinicalTrials.gov": search_clinicaltrials,
    "Papers with Code": search_papers_with_code,
}

DOMAIN_TO_SOURCES = {
    "pubmed": ["PubMed / NCBI E-utilities"],
    "biomedical": ["PubMed / NCBI E-utilities", "ClinicalTrials.gov"],
    "health": ["PubMed / NCBI E-utilities", "ClinicalTrials.gov"],
    "clinical": ["PubMed / NCBI E-utilities", "ClinicalTrials.gov"],
    "psychology": ["PubMed / NCBI E-utilities"],
    "arxiv": ["arXiv"],
    "ai": ["arXiv", "Papers with Code"],
    "cs": ["arXiv", "Papers with Code"],
    "computer-science": ["arXiv", "Papers with Code"],
    "education": ["ERIC"],
    "eric": ["ERIC"],
    "clinicaltrials": ["ClinicalTrials.gov"],
    "paperswithcode": ["Papers with Code"],
    "benchmark": ["Papers with Code"],
}


def infer_conditional_sources(text: str) -> list[str]:
    lower = text.lower()
    selected: list[str] = []
    domain_markers = {
        "biomedical": ["biomedical", "clinical", "patient", "hospital", "diabetes", "health"],
        "ai": ["artificial intelligence", "generative ai", "machine learning", "deep learning", "llm", "benchmark"],
        "education": ["education", "student", "graduate", "doctoral", "learning", "school"],
    }
    for domain, markers in domain_markers.items():
        if any(marker in lower for marker in markers):
            selected.extend(DOMAIN_TO_SOURCES[domain])
    return sorted(set(selected), key=selected.index)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run scholarly API search and write raw search artifacts.")
    parser.add_argument("--out-dir", required=True, help="Output directory containing search_terms.md.")
    parser.add_argument("--query", action="append", default=[], help="Additional query to run.")
    parser.add_argument("--limit", type=int, default=20, help="Per-query per-source limit.")
    parser.add_argument("--mode", default="topic_landing")
    parser.add_argument("--domain", action="append", default=[], help="Optional domain/source selector.")
    parser.add_argument("--source", action="append", default=[], help="Exact source name to include.")
    parser.add_argument("--all-conditional", action="store_true", help="Run every conditional structured source.")
    parser.add_argument("--allow-empty", action="store_true", help="Do not fail when no API returns results.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds per request.")
    parser.add_argument("--retries", type=int, default=1, help="Retry count per query/source after the first failed attempt.")
    parser.add_argument("--max-failures", type=int, default=0, help="Abort after this many source/query failures; 0 means never abort early.")
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    search_terms = read_text(out_dir / "search_terms.md")
    queries = parse_query_families(search_terms)
    for index, query in enumerate(args.query, start=1):
        queries.append({"name": f"manual-{index}", "query": query})

    if not queries:
        idea = extract_idea(out_dir)
        if idea:
            queries = [{"name": "precise", "query": idea}]
    if not queries:
        raise SystemExit("No queries found. Run expand_keywords.py first or pass --query.")

    raw_rows: list[dict[str, Any]] = []
    manifest_queries: list[dict[str, Any]] = []
    failed_sources: list[dict[str, str]] = []
    selected_sources: dict[str, Searcher] = dict(CORE_SOURCES)
    conditional_names: list[str] = []
    if args.all_conditional:
        conditional_names.extend(CONDITIONAL_SOURCES)
    else:
        conditional_names.extend(infer_conditional_sources(f"{extract_idea(out_dir)}\n{search_terms}"))
    for domain in args.domain:
        for source_name in DOMAIN_TO_SOURCES.get(domain.lower().strip(), []):
            conditional_names.append(source_name)
    for source_name in args.source:
        if source_name in CONDITIONAL_SOURCES:
            conditional_names.append(source_name)
    for source_name in dict.fromkeys(conditional_names):
        selected_sources[source_name] = CONDITIONAL_SOURCES[source_name]

    abort_early = False
    for family in queries:
        if abort_early:
            break
        query = family["query"]
        for source_name, searcher in selected_sources.items():
            try:
                results = with_retries(lambda: searcher(query, args.limit, args.timeout), args.retries)
                for rank, raw in enumerate(results, start=1):
                    raw_rows.append(
                        {
                            "retrieved_at": now_iso(),
                            "source_database": source_name,
                            "query_family": family["name"],
                            "query": query,
                            "rank": rank,
                            "raw": raw,
                        }
                    )
                manifest_queries.append(
                    {
                        "name": family["name"],
                        "query": query,
                        "source": source_name,
                        "limit": args.limit,
                        "results_count": len(results),
                    }
                )
            except Exception as exc:
                failed_sources.append(
                    {
                        "source": source_name,
                        "query_family": family["name"],
                        "query": query,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                manifest_queries.append(
                    {
                        "name": family["name"],
                        "query": query,
                        "source": source_name,
                        "limit": args.limit,
                        "results_count": 0,
                    }
                )
                if args.max_failures and len(failed_sources) >= args.max_failures:
                    abort_early = True
                    break

    idea = extract_idea(out_dir)
    manifest = {
        "run_date": now_iso(),
        "topic_slug": slugify(idea or queries[0]["query"]),
        "mode": args.mode,
        "databases": list(selected_sources) + ["Live Web via Codex web_search"],
        "live_web_evidence_file": "live_web_sources.json",
        "live_web_requirement": "Codex must record live web_search sources in live_web_sources.json before final topic/gap/method claims.",
        "query_families": manifest_queries,
        "inclusion_criteria": [
            "Directly related to the idea, population/context, method, model, outcome, dataset, theory, or adjacent research area.",
            "Has traceable bibliographic metadata such as DOI, URL, OpenAlex ID, Semantic Scholar ID, PMID, or arXiv ID.",
        ],
        "exclusion_criteria": [
            "Pure opinion pieces without research, method, data, theory, or practice value.",
            "Records with no usable title or traceable source identifier.",
        ],
        "failed_sources": failed_sources,
        "timeout_seconds": args.timeout,
        "retries": args.retries,
        "aborted_early": abort_early,
        "notes": [
            "This script searches scholarly APIs. The Codex agent must also run live web search for fresh webpages, datasets, guidelines, and grey literature, then record the sources in live_web_sources.json before making current-state claims.",
        ],
    }

    dump_jsonl(out_dir / "raw_results.jsonl", raw_rows)
    dump_json(out_dir / "search_manifest.json", manifest)

    if not raw_rows and not args.allow_empty:
        print("No records retrieved. See search_manifest.json for source failures.")
        return 2
    print(f"Retrieved {len(raw_rows)} raw records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
