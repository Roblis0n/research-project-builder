#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Any

from _common import MATRIX_FIELDS, load_jsonl, normalize_space, output_dir_from_args, write_csv_dicts


METHOD_HINTS = {
    "machine learning": ["machine learning", "prediction", "random forest", "xgboost", "neural network"],
    "survey": ["survey", "questionnaire", "cross-sectional"],
    "qualitative": ["interview", "qualitative", "thematic analysis", "grounded theory"],
    "review": ["systematic review", "scoping review", "meta-analysis", "bibliometric"],
    "causal inference": ["causal", "difference-in-differences", "instrumental variable", "propensity"],
    "experiment": ["experiment", "randomized", "trial", "intervention"],
}

MODEL_HINTS = {
    "regression": ["regression", "logistic"],
    "tree ensemble": ["random forest", "xgboost", "lightgbm", "gradient boosting"],
    "neural/transformer": ["neural", "deep learning", "transformer", "bert", "large language model"],
    "survival model": ["survival", "cox"],
    "SEM": ["structural equation", "sem", "mediation", "moderation"],
}

THEORY_HINTS = [
    "self-efficacy",
    "technology acceptance",
    "social cognitive",
    "academic identity",
    "institutional theory",
    "stakeholder theory",
    "cognitive load",
]


def find_hint(text: str, hints: dict[str, list[str]], default: str = "Not clear from metadata") -> str:
    lower = text.lower()
    found = [label for label, markers in hints.items() if any(marker in lower for marker in markers)]
    return "; ".join(found) if found else default


def find_theory(text: str) -> str:
    lower = text.lower()
    hits = [hint for hint in THEORY_HINTS if hint in lower]
    return "; ".join(hits) if hits else "Not explicit in metadata"


def make_row(index: int, record: dict[str, Any]) -> dict[str, Any]:
    title = normalize_space(record.get("title"))
    abstract = normalize_space(record.get("abstract"))
    combined = f"{title}. {abstract}"
    url = record.get("url") or ""
    if not url and record.get("doi"):
        url = f"https://doi.org/{record['doi']}"

    similarity_class = record.get("similarity_class", "")
    score = float(record.get("similarity_score") or 0)
    if score >= 0.80:
        usable_gap = "Original version may be highly covered; recommend modification."
    elif score >= 0.60:
        usable_gap = "Use as close adjacent baseline and differentiate by context, data, or method."
    elif score >= 0.40:
        usable_gap = "Adjacent work can support a gap-driven project."
    else:
        usable_gap = "Background evidence; expand search before strong novelty claims."

    return {
        "id": f"S{index:03d}",
        "title": title,
        "authors": normalize_space(record.get("authors")),
        "year": normalize_space(record.get("year")),
        "venue": normalize_space(record.get("venue")),
        "doi": normalize_space(record.get("doi")),
        "url": normalize_space(url),
        "openalex_id": normalize_space(record.get("openalex_id")),
        "semantic_scholar_id": normalize_space(record.get("semantic_scholar_id")),
        "pmid": normalize_space(record.get("pmid")),
        "arxiv_id": normalize_space(record.get("arxiv_id")),
        "source_database": normalize_space(record.get("source_database")),
        "abstract": abstract[:1200],
        "research_question": title or "Not available from metadata",
        "population_or_context": infer_context(combined),
        "data_or_sample": infer_data(combined),
        "method": find_hint(combined, METHOD_HINTS),
        "model": find_hint(combined, MODEL_HINTS),
        "theory": find_theory(combined),
        "outcome": infer_outcome(title),
        "key_finding": "Metadata-only extraction; inspect full text before treating as a finding.",
        "similarity_score": record.get("similarity_score", ""),
        "similarity_class": similarity_class,
        "usable_gap": usable_gap,
        "limitations": "API metadata may omit methods, sample, results, and theory; verify key records manually.",
        "why_it_matters_for_user_topic": why_it_matters(similarity_class),
    }


def infer_context(text: str) -> str:
    lower = text.lower()
    mapping = [
        ("graduate/doctoral students", ["graduate", "doctoral", "student"]),
        ("clinical or patient context", ["patient", "clinical", "hospital", "diabetes", "readmission"]),
        ("enterprise/ESG context", ["firm", "enterprise", "carbon", "emission", "esg"]),
        ("AI or digital technology context", ["artificial intelligence", "generative ai", "chatgpt", "llm"]),
    ]
    found = [label for label, markers in mapping if any(marker in lower for marker in markers)]
    return "; ".join(found) if found else "Not clear from metadata"


def infer_data(text: str) -> str:
    lower = text.lower()
    mapping = [
        ("survey data", ["survey", "questionnaire"]),
        ("interview or qualitative corpus", ["interview", "qualitative"]),
        ("EHR/claims/registry", ["electronic health", "claims", "registry", "cohort"]),
        ("public benchmark or dataset", ["benchmark", "dataset", "corpus"]),
        ("document/report data", ["annual report", "disclosure", "filing"]),
    ]
    found = [label for label, markers in mapping if any(marker in lower for marker in markers)]
    return "; ".join(found) if found else "Not clear from metadata"


def infer_outcome(title: str) -> str:
    title = title.strip()
    if not title:
        return "Not available from metadata"
    return f"Likely outcome/phenomenon from title: {title[:180]}"


def why_it_matters(similarity_class: str) -> str:
    if similarity_class == "highly similar":
        return "Potential direct overlap; use to avoid duplicating an already crowded question."
    if similarity_class == "close adjacent":
        return "Close enough to shape differentiation and feasibility decisions."
    if similarity_class == "adjacent":
        return "Useful for theory, method, construct, or data borrowing."
    return "Useful as background only; do not infer novelty from this alone."


def main() -> int:
    parser = argparse.ArgumentParser(description="Build evidence_matrix.csv from scored records.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--limit", type=int, default=80)
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    scored = load_jsonl(out_dir / "scored_sources.jsonl")
    rows = [make_row(index, record) for index, record in enumerate(scored[: args.limit], start=1)]
    write_csv_dicts(out_dir / "evidence_matrix.csv", MATRIX_FIELDS, rows)
    print(f"Wrote evidence matrix with {len(rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
