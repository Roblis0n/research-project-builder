#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from typing import Any

from _common import clamp, dump_jsonl, extract_idea, load_jsonl, output_dir_from_args, overlap_score, read_text, similarity_class, title_key, tokenize

METHOD_MARKERS = [
    "machine learning",
    "prediction",
    "regression",
    "survey",
    "interview",
    "experiment",
    "causal",
    "qualitative",
    "mixed methods",
    "systematic review",
    "scoping review",
]

MODEL_MARKERS = [
    "random forest",
    "xgboost",
    "lightgbm",
    "transformer",
    "neural network",
    "logistic regression",
    "survival",
    "structural equation",
    "topic model",
]

DATA_MARKERS = [
    "dataset",
    "cohort",
    "survey",
    "interview",
    "electronic health record",
    "claims",
    "registry",
    "benchmark",
    "administrative",
    "public data",
]

THEORY_MARKERS = [
    "theory",
    "framework",
    "self-efficacy",
    "social cognitive",
    "academic identity",
    "technology acceptance",
    "cognitive load",
    "stakeholder theory",
    "institutional theory",
    "planned behavior",
    "affordance",
]


def marker_score(text: str, markers: list[str]) -> float:
    lower = text.lower()
    hits = sum(1 for marker in markers if marker in lower)
    return clamp(hits / 3)


def recency_score(year: Any) -> float:
    try:
        year_int = int(str(year)[:4])
    except Exception:
        return 0.2
    age = date.today().year - year_int
    if age <= 3:
        return 1.0
    if age <= 7:
        return 0.7
    if age <= 15:
        return 0.4
    return 0.2


def review_or_method_value(text: str, publication_type: str) -> float:
    lower = f"{text} {publication_type}".lower()
    markers = ["review", "systematic", "scoping", "meta-analysis", "method", "protocol", "guideline"]
    return 1.0 if any(marker in lower for marker in markers) else 0.2


def score_record(record: dict[str, Any], idea: str, search_terms: str) -> dict[str, float]:
    text = " ".join(
        str(record.get(key, ""))
        for key in ["title", "abstract", "keywords", "venue", "publication_type"]
    )
    topic_similarity = max(overlap_score(idea, text), overlap_score(search_terms, text) * 0.7)
    population_context_similarity = overlap_score(idea, f"{record.get('title', '')} {record.get('abstract', '')}")
    method_similarity = marker_score(text, METHOD_MARKERS)
    model_similarity = marker_score(text, MODEL_MARKERS)
    outcome_similarity = overlap_score(record.get("title", ""), idea)
    data_similarity = marker_score(text, DATA_MARKERS)
    theory_relevance = marker_score(text, THEORY_MARKERS)
    recency_signal = recency_score(record.get("year"))
    review_value = review_or_method_value(text, record.get("publication_type", ""))
    total = (
        0.25 * topic_similarity
        + 0.15 * population_context_similarity
        + 0.12 * method_similarity
        + 0.15 * model_similarity
        + 0.10 * outcome_similarity
        + 0.10 * data_similarity
        + 0.03 * theory_relevance
        + 0.05 * recency_signal
        + 0.05 * review_value
    )
    return {
        "topic_similarity": round(clamp(topic_similarity), 3),
        "population_context_similarity": round(clamp(population_context_similarity), 3),
        "method_similarity": round(clamp(method_similarity), 3),
        "model_similarity": round(clamp(model_similarity), 3),
        "outcome_similarity": round(clamp(outcome_similarity), 3),
        "data_similarity": round(clamp(data_similarity), 3),
        "theory_relevance": round(clamp(theory_relevance), 3),
        "recency_signal": round(clamp(recency_signal), 3),
        "review_or_method_value": round(clamp(review_value), 3),
        "total_score": round(clamp(total), 3),
    }


def dedupe_key(record: dict[str, Any]) -> str:
    doi = str(record.get("doi") or "").lower().strip()
    if doi:
        return "doi:" + doi
    semantic = str(record.get("semantic_scholar_id") or "").lower().strip()
    if semantic:
        return "s2:" + semantic
    openalex = str(record.get("openalex_id") or "").lower().strip()
    if openalex:
        return "oa:" + openalex
    pmid = str(record.get("pmid") or "").lower().strip()
    if pmid:
        return "pmid:" + pmid
    arxiv_id = str(record.get("arxiv_id") or "").lower().strip()
    if arxiv_id:
        return "arxiv:" + arxiv_id
    return "title:" + title_key(str(record.get("title") or ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Dedupe normalized records and compute screening similarity scores.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--idea", default="", help="Optional idea override.")
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    idea = args.idea or extract_idea(out_dir)
    search_terms = read_text(out_dir / "search_terms.md")
    records = load_jsonl(out_dir / "normalized_sources.jsonl")

    best: dict[str, dict[str, Any]] = {}
    for record in records:
        components = score_record(record, idea, search_terms)
        scored = dict(record)
        scored.update(components)
        scored["similarity_score"] = components["total_score"]
        scored["similarity_class"] = similarity_class(components["total_score"])
        key = dedupe_key(scored)
        if key not in best or scored["similarity_score"] > best[key].get("similarity_score", 0):
            best[key] = scored

    scored_rows = sorted(best.values(), key=lambda row: row.get("similarity_score", 0), reverse=True)
    dump_jsonl(out_dir / "scored_sources.jsonl", scored_rows)
    print(f"Scored {len(scored_rows)} deduplicated records from {len(records)} normalized records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
