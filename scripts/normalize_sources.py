#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from typing import Any

from _common import abstract_from_inverted_index, dump_jsonl, load_jsonl, normalize_space, output_dir_from_args


def strip_doi(value: str) -> str:
    value = normalize_space(value)
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
    return value


def normalize_openalex(raw: dict[str, Any]) -> dict[str, Any]:
    authorships = raw.get("authorships") or []
    authors = [
        item.get("author", {}).get("display_name", "")
        for item in authorships
        if isinstance(item, dict)
    ]
    primary = raw.get("primary_location") or {}
    source = primary.get("source") or {}
    concepts = raw.get("concepts") or []
    keywords = [item.get("display_name", "") for item in concepts if isinstance(item, dict)]
    url = raw.get("id") or raw.get("doi") or (primary.get("landing_page_url") if isinstance(primary, dict) else "")
    return {
        "title": normalize_space(raw.get("display_name") or raw.get("title")),
        "authors": "; ".join(author for author in authors if author),
        "year": raw.get("publication_year") or "",
        "venue": normalize_space(source.get("display_name") or raw.get("host_venue", {}).get("display_name")),
        "doi": strip_doi(raw.get("doi") or ""),
        "url": normalize_space(url),
        "abstract": normalize_space(abstract_from_inverted_index(raw.get("abstract_inverted_index"))),
        "source_database": "OpenAlex",
        "citation_count": raw.get("cited_by_count") or 0,
        "publication_type": normalize_space(raw.get("type")),
        "open_access_status": normalize_space((raw.get("open_access") or {}).get("oa_status")),
        "keywords": "; ".join(keyword for keyword in keywords if keyword),
        "openalex_id": raw.get("id") or "",
        "semantic_scholar_id": "",
        "pmid": "",
        "arxiv_id": "",
    }


def normalize_semantic(raw: dict[str, Any]) -> dict[str, Any]:
    authors = [item.get("name", "") for item in raw.get("authors") or [] if isinstance(item, dict)]
    external = raw.get("externalIds") or {}
    doi = strip_doi(external.get("DOI") or "")
    arxiv_id = normalize_space(external.get("ArXiv") or "")
    pmid = normalize_space(external.get("PubMed") or "")
    url = raw.get("url") or ""
    if not url and doi:
        url = f"https://doi.org/{doi}"
    if not url and arxiv_id:
        url = f"https://arxiv.org/abs/{arxiv_id}"
    return {
        "title": normalize_space(raw.get("title")),
        "authors": "; ".join(author for author in authors if author),
        "year": raw.get("year") or "",
        "venue": normalize_space(raw.get("venue")),
        "doi": doi,
        "url": normalize_space(url),
        "abstract": normalize_space(raw.get("abstract")),
        "source_database": "Semantic Scholar",
        "citation_count": raw.get("citationCount") or 0,
        "publication_type": normalize_space(raw.get("publicationTypes") or []),
        "open_access_status": "open" if raw.get("isOpenAccess") else "",
        "keywords": normalize_space(raw.get("fieldsOfStudy") or []),
        "openalex_id": "",
        "semantic_scholar_id": normalize_space(raw.get("paperId") or external.get("CorpusId") or ""),
        "pmid": pmid,
        "arxiv_id": arxiv_id,
    }


def crossref_year(raw: dict[str, Any]) -> str:
    for key in ["published-print", "published-online", "issued", "created"]:
        parts = ((raw.get(key) or {}).get("date-parts") or [])
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def normalize_crossref(raw: dict[str, Any]) -> dict[str, Any]:
    title = raw.get("title") or []
    authors = []
    for author in raw.get("author") or []:
        given = author.get("given", "")
        family = author.get("family", "")
        authors.append(normalize_space(f"{given} {family}"))
    abstract = re.sub(r"<[^>]+>", " ", raw.get("abstract") or "")
    doi = strip_doi(raw.get("DOI") or "")
    url = raw.get("URL") or (f"https://doi.org/{doi}" if doi else "")
    return {
        "title": normalize_space(title[0] if title else ""),
        "authors": "; ".join(author for author in authors if author),
        "year": crossref_year(raw),
        "venue": normalize_space((raw.get("container-title") or [""])[0]),
        "doi": doi,
        "url": normalize_space(url),
        "abstract": normalize_space(abstract),
        "source_database": "Crossref",
        "citation_count": raw.get("is-referenced-by-count") or 0,
        "publication_type": normalize_space(raw.get("type")),
        "open_access_status": "",
        "keywords": normalize_space(raw.get("subject") or []),
        "openalex_id": "",
        "semantic_scholar_id": "",
        "pmid": "",
        "arxiv_id": "",
    }


def normalize_pubmed(raw: dict[str, Any]) -> dict[str, Any]:
    article_ids = raw.get("articleids") or []
    doi = ""
    for item in article_ids:
        if isinstance(item, dict) and item.get("idtype", "").lower() == "doi":
            doi = strip_doi(item.get("value", ""))
            break
    authors = [
        item.get("name", "")
        for item in raw.get("authors") or []
        if isinstance(item, dict)
    ]
    pmid = normalize_space(raw.get("uid") or raw.get("pmid") or "")
    pubdate = normalize_space(raw.get("pubdate") or raw.get("epubdate") or "")
    return {
        "title": normalize_space(raw.get("title")),
        "authors": "; ".join(author for author in authors if author),
        "year": pubdate[:4],
        "venue": normalize_space(raw.get("fulljournalname") or raw.get("source")),
        "doi": doi,
        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else (f"https://doi.org/{doi}" if doi else ""),
        "abstract": "",
        "source_database": "PubMed / NCBI E-utilities",
        "citation_count": 0,
        "publication_type": normalize_space(raw.get("pubtype") or []),
        "open_access_status": normalize_space(raw.get("attributes") or []),
        "keywords": "",
        "openalex_id": "",
        "semantic_scholar_id": "",
        "pmid": pmid,
        "arxiv_id": "",
    }


def normalize_arxiv(raw: dict[str, Any]) -> dict[str, Any]:
    arxiv_url = normalize_space(raw.get("id"))
    arxiv_id = arxiv_url.rstrip("/").split("/")[-1] if arxiv_url else ""
    published = normalize_space(raw.get("published"))
    return {
        "title": normalize_space(raw.get("title")),
        "authors": normalize_space(raw.get("authors") or []),
        "year": published[:4],
        "venue": "arXiv",
        "doi": strip_doi(raw.get("doi") or ""),
        "url": arxiv_url,
        "abstract": normalize_space(raw.get("summary")),
        "source_database": "arXiv",
        "citation_count": 0,
        "publication_type": "preprint",
        "open_access_status": "open",
        "keywords": normalize_space(raw.get("categories") or []),
        "openalex_id": "",
        "semantic_scholar_id": "",
        "pmid": "",
        "arxiv_id": arxiv_id,
    }


def normalize_eric(raw: dict[str, Any]) -> dict[str, Any]:
    eric_id = normalize_space(raw.get("id") or raw.get("ericNumber") or raw.get("accessionNumber"))
    authors = raw.get("author") or raw.get("authors") or []
    year = raw.get("publicationdateyear") or raw.get("publicationdate") or raw.get("year") or ""
    url = raw.get("url") or raw.get("recordUrl") or (f"https://eric.ed.gov/?id={eric_id}" if eric_id else "")
    return {
        "title": normalize_space(raw.get("title")),
        "authors": normalize_space(authors),
        "year": normalize_space(year)[:4],
        "venue": normalize_space(raw.get("source") or raw.get("journal") or "ERIC"),
        "doi": strip_doi(raw.get("doi") or ""),
        "url": normalize_space(url),
        "abstract": normalize_space(raw.get("description") or raw.get("abstract")),
        "source_database": "ERIC",
        "citation_count": 0,
        "publication_type": normalize_space(raw.get("publicationtype") or raw.get("publicationType")),
        "open_access_status": normalize_space(raw.get("peerreviewed") or ""),
        "keywords": normalize_space(raw.get("subject") or raw.get("subjects") or []),
        "openalex_id": "",
        "semantic_scholar_id": "",
        "pmid": "",
        "arxiv_id": "",
    }


def normalize_clinicaltrials(raw: dict[str, Any]) -> dict[str, Any]:
    protocol = raw.get("protocolSection") or {}
    identification = protocol.get("identificationModule") or {}
    status = protocol.get("statusModule") or {}
    description = protocol.get("descriptionModule") or {}
    conditions = protocol.get("conditionsModule") or {}
    design = protocol.get("designModule") or {}
    nct_id = normalize_space(identification.get("nctId"))
    title = normalize_space(identification.get("briefTitle") or identification.get("officialTitle"))
    return {
        "title": title,
        "authors": normalize_space((protocol.get("sponsorCollaboratorsModule") or {}).get("leadSponsor", {}).get("name")),
        "year": normalize_space(status.get("startDateStruct", {}).get("date") or "")[:4],
        "venue": "ClinicalTrials.gov",
        "doi": "",
        "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "",
        "abstract": normalize_space(description.get("briefSummary") or description.get("detailedDescription")),
        "source_database": "ClinicalTrials.gov",
        "citation_count": 0,
        "publication_type": normalize_space(design.get("studyType") or "clinical trial registry record"),
        "open_access_status": "registry",
        "keywords": normalize_space(conditions.get("conditions") or []),
        "openalex_id": "",
        "semantic_scholar_id": "",
        "pmid": "",
        "arxiv_id": "",
    }


def normalize_papers_with_code(raw: dict[str, Any]) -> dict[str, Any]:
    url = raw.get("url_abs") or raw.get("paper_url") or raw.get("url") or ""
    published = normalize_space(raw.get("published") or raw.get("date") or "")
    return {
        "title": normalize_space(raw.get("title")),
        "authors": normalize_space(raw.get("authors") or []),
        "year": published[:4],
        "venue": "Papers with Code",
        "doi": strip_doi(raw.get("doi") or ""),
        "url": normalize_space(url),
        "abstract": normalize_space(raw.get("abstract")),
        "source_database": "Papers with Code",
        "citation_count": 0,
        "publication_type": "paper/model benchmark record",
        "open_access_status": "",
        "keywords": normalize_space(raw.get("tasks") or raw.get("methods") or []),
        "openalex_id": "",
        "semantic_scholar_id": "",
        "pmid": "",
        "arxiv_id": "",
    }


NORMALIZERS = {
    "OpenAlex": normalize_openalex,
    "Semantic Scholar": normalize_semantic,
    "Crossref": normalize_crossref,
    "PubMed / NCBI E-utilities": normalize_pubmed,
    "arXiv": normalize_arxiv,
    "ERIC": normalize_eric,
    "ClinicalTrials.gov": normalize_clinicaltrials,
    "Papers with Code": normalize_papers_with_code,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize raw API records into a shared schema.")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    raw_rows = load_jsonl(out_dir / "raw_results.jsonl")
    normalized: list[dict[str, Any]] = []
    for row in raw_rows:
        source = row.get("source_database", "")
        raw = row.get("raw") or {}
        normalizer = NORMALIZERS.get(source)
        if not normalizer:
            continue
        item = normalizer(raw)
        item["query_family"] = row.get("query_family", "")
        item["query"] = row.get("query", "")
        item["rank"] = row.get("rank", "")
        if item.get("title") and (
            item.get("url")
            or item.get("doi")
            or item.get("openalex_id")
            or item.get("semantic_scholar_id")
            or item.get("pmid")
            or item.get("arxiv_id")
        ):
            normalized.append(item)

    dump_jsonl(out_dir / "normalized_sources.jsonl", normalized)
    print(f"Normalized {len(normalized)} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
