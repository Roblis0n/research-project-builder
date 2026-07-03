#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from _common import output_dir_from_args, slugify, today, tokenize, write_text


AI_TERMS = [
    "artificial intelligence",
    "generative AI",
    "large language model",
    "ChatGPT",
    "AI-assisted research",
    "cognitive offloading",
]

EDUCATION_TERMS = [
    "graduate students",
    "doctoral students",
    "research ability",
    "academic self-efficacy",
    "academic identity",
    "research anxiety",
]

HEALTH_TERMS = [
    "prediction model",
    "clinical risk prediction",
    "readmission",
    "external validation",
    "calibration",
    "decision curve analysis",
]

SOCIAL_TERMS = [
    "mechanism",
    "mediation",
    "moderation",
    "mixed methods",
    "survey",
    "interview",
]

METHOD_TERMS = [
    "systematic review",
    "scoping review",
    "bibliometric analysis",
    "causal inference",
    "machine learning",
    "qualitative study",
    "mixed methods",
]


def read_idea(args: argparse.Namespace) -> str:
    if args.idea:
        return args.idea.strip()
    if args.idea_file:
        return Path(args.idea_file).read_text(encoding="utf-8", errors="replace").strip()
    raise SystemExit("--idea or --idea-file is required")


def infer_terms(idea: str) -> dict[str, list[str]]:
    lower = idea.lower()
    english: list[str] = []
    source_language: list[str] = []
    adjacent: list[str] = []
    theory: list[str] = []
    method: list[str] = list(METHOD_TERMS)
    model: list[str] = []
    dataset: list[str] = ["public dataset", "benchmark", "survey data", "administrative data"]
    older: list[str] = []
    emerging: list[str] = []

    if any(term in lower for term in ["ai", "chatgpt", "llm", "generative"]):
        english.extend(AI_TERMS)
        adjacent.extend(["human-AI collaboration", "automation anxiety", "digital literacy"])
        theory.extend(["technology acceptance model", "self-efficacy theory", "cognitive load theory"])
        model.extend(["transformer", "embedding model", "topic model"])
        older.extend(["computer-assisted instruction", "intelligent tutoring system", "educational technology"])
        emerging.extend(["generative AI", "large language model", "agentic AI", "AI copilot"])

    if any(term in lower for term in ["graduate", "doctoral", "education", "student"]):
        english.extend(EDUCATION_TERMS)
        adjacent.extend(["academic motivation", "research training", "supervisor support"])
        theory.extend(["social cognitive theory", "academic identity theory"])
        dataset.extend(["student survey", "interview corpus", "learning analytics"])
        older.extend(["postgraduate education", "research training", "academic development"])
        emerging.extend(["AI literacy", "AI-assisted research workflow", "doctoral AI use"])

    if any(term in lower for term in ["diabetes", "readmission", "clinical", "health", "patient"]):
        english.extend(HEALTH_TERMS)
        method.extend(["TRIPOD", "PROBAST", "survival analysis"])
        model.extend(["logistic regression", "random forest", "gradient boosting", "survival model"])
        dataset.extend(["electronic health records", "claims data", "registry data"])
        older.extend(["risk score", "clinical decision rule", "prognostic model"])
        emerging.extend(["TRIPOD+AI", "fairness-aware prediction", "decision curve analysis"])

    if any(term in lower for term in ["enterprise", "firm", "emission", "carbon", "esg"]):
        english.extend(["carbon emissions", "corporate ESG", "emission disclosure", "scope 1 emissions"])
        adjacent.extend(["green innovation", "environmental disclosure", "carbon accounting"])
        theory.extend(["stakeholder theory", "institutional theory"])
        dataset.extend(["ESG database", "annual reports", "city-level proxy data", "industry statistics"])
        older.extend(["environmental disclosure", "corporate social responsibility", "pollution accounting"])
        emerging.extend(["scope 3 emissions", "ESG rating", "carbon neutrality", "climate risk disclosure"])

    if not english:
        english.extend(sorted(tokenize(idea))[:8])
    return {
        "source_language": unique(source_language),
        "english": unique(english),
        "synonyms": unique(english + source_language),
        "adjacent": unique(adjacent + SOCIAL_TERMS),
        "theory": unique(theory),
        "method": unique(method),
        "model": unique(model),
        "dataset": unique(dataset),
        "older": unique(older),
        "emerging": unique(emerging),
    }


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        key = item.lower()
        if item and key not in seen:
            output.append(item)
            seen.add(key)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand an initial research idea into searchable terms.")
    parser.add_argument("--idea", help="Initial research idea.")
    parser.add_argument("--idea-file", help="Text file containing the initial idea.")
    parser.add_argument("--field", default="", help="Optional field hint.")
    parser.add_argument("--target-output", default="research topic package", help="Expected user-facing output.")
    parser.add_argument("--constraints", default="", help="Known constraints.")
    parser.add_argument("--out-dir", help="Output directory.")
    args = parser.parse_args()

    idea = read_idea(args)
    out_dir = output_dir_from_args(args.out_dir, idea)
    terms = infer_terms(idea)

    precise = " ".join((terms["english"][:4] + terms["source_language"][:2]) or [idea])
    broad = " ".join(unique(terms["adjacent"][:5] + terms["english"][:2]))
    review = f"{precise} systematic review scoping review bibliometric"
    method = f"{precise} {' '.join(terms['method'][:4])}"
    theory = f"{precise} {' '.join(terms['theory'][:4])}"
    dataset = f"{precise} {' '.join(terms['dataset'][:4])}"

    intake = f"""# Intake Brief

## Original Idea
{idea}

## Field
{args.field or "Provisional: infer from the idea and retrieved literature."}

## Target Output
{args.target_output}

## Available Resources
Provisional: no private data, budget, software, or publication target has been supplied.

## Constraints
{args.constraints or "Provisional: use public literature and public or realistically collectable data first."}

## Provisional Assumptions
- I will not require the user to choose a direction before proceeding.
- I will treat the initial idea as editable and search around both direct and adjacent terms.
- I will separate topic generation from later theory, method, and modeling expansion.

## Run Metadata
- Created: {today()}
- Topic slug: {slugify(idea)}
"""

    search_terms = f"""# Search Terms

## Core source-language terms
{bullet(terms["source_language"])}

## Core English expansion terms
{bullet(terms["english"])}

## Synonyms
{bullet(terms["synonyms"])}

## Adjacent terms
{bullet(terms["adjacent"])}

## Older terminology
{bullet(terms["older"])}

## Emerging terminology
{bullet(terms["emerging"])}

## Theory terms
{bullet(terms["theory"])}

## Method terms
{bullet(terms["method"])}

## Model terms
{bullet(terms["model"])}

## Dataset / benchmark terms
{bullet(terms["dataset"])}

## Negative keywords
- unrelated clinical trials unless the topic is clinical
- purely technical benchmark papers unless the topic is model building
- opinion pieces without empirical or theoretical value

## Query families

### 1. Precise query
{precise}

### 2. Broad adjacent query
{broad}

### 3. Review query
{review}

### 4. Method query
{method}

### 5. Theory query
{theory}

### 6. Dataset/model query
{dataset}
"""

    write_text(out_dir / "intake_brief.md", intake)
    write_text(out_dir / "search_terms.md", search_terms)
    print(out_dir)
    return 0


def bullet(items: list[str]) -> str:
    if not items:
        return "- Provisional: no reliable term inferred yet."
    return "\n".join(f"- {item}" for item in items)


if __name__ == "__main__":
    raise SystemExit(main())
