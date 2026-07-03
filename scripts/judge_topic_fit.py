#!/usr/bin/env python3
from __future__ import annotations

import argparse

from _common import extract_idea, output_dir_from_args, read_csv_dicts, write_text


def classify(rows: list[dict[str, str]], idea: str) -> tuple[str, list[str]]:
    if not rows:
        return "Sparse evidence", [
            "No usable evidence-matrix rows were produced.",
            "Expand queries, check API access, and run live web search before judging novelty.",
        ]

    high = sum(row.get("similarity_class") == "highly similar" for row in rows)
    close = sum(row.get("similarity_class") == "close adjacent" for row in rows)
    adjacent = sum(row.get("similarity_class") == "adjacent" for row in rows)
    max_score = max(float(row.get("similarity_score") or 0) for row in rows)
    idea_lower = idea.lower()
    data_risk = any(marker in idea_lower for marker in ["all enterprises", "future three years", "entire population", "all organizations"])

    if data_risk:
        return "Needs data-first redesign", [
            "The idea implies broad or future-looking data that may not be directly observable.",
            "Start with a smaller public-data MVP before committing to complex modeling.",
        ]
    if high >= 3 or max_score >= 0.88:
        return "Highly covered", [
            "Several records are highly similar to the initial formulation.",
            "Do not recommend the original version unchanged; differentiate by context, data, validation, mechanism, or method.",
        ]
    if high >= 1 or close >= 4:
        return "Partially covered", [
            "The broad question is covered, but there is room for a gap-driven redesign.",
            "Look for differences in context, population, data, theory, model, evaluation, or time period.",
        ]
    if close >= 1 or adjacent >= 4:
        return "Adjacent but not direct", [
            "Adjacent literature is available, but direct overlap is limited in this search run.",
            "Novelty should be described provisionally and anchored in the exact combination of context, data, and method.",
        ]
    return "Sparse evidence", [
        "Few direct or close-adjacent records were found in the structured API search.",
        "Use broader keywords, citation chasing, grey literature, and domain-specific sources before making strong claims.",
    ]


def nearest_rows(rows: list[dict[str, str]], n: int = 8) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: float(row.get("similarity_score") or 0), reverse=True)[:n]


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge topic coverage and feasibility from evidence_matrix.csv.")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    rows = read_csv_dicts(out_dir / "evidence_matrix.csv")
    idea = extract_idea(out_dir)
    category, reasons = classify(rows, idea)

    lines = [
        "# Topic Fit Report",
        "",
        "## Search Scope",
        "Structured scholarly sources are recorded in `search_manifest.json`. The Codex agent must add live web-search observations before presenting current-state claims.",
        "",
        "## Original Idea",
        idea or "Not available.",
        "",
        "## Closest Existing Research",
    ]
    for row in nearest_rows(rows):
        lines.append(
            f"- {row.get('id')}: {row.get('title')} ({row.get('year')}, {row.get('source_database')}) "
            f"[score {row.get('similarity_score')}, {row.get('similarity_class')}]"
        )
    if not rows:
        lines.append("- No records available.")

    lines.extend(
        [
            "",
            "## Coverage Judgment",
            f"Within the current search scope, the original idea is classified as: **{category}**.",
            "",
            "## Reasons",
        ]
    )
    lines.extend(f"- {reason}" for reason in reasons)
    lines.extend(
        [
            "",
            "## Executability Diagnosis",
            "- If the topic is highly covered, change context, data, validation target, mechanism, or method.",
            "- If the topic is sparse, expand search and avoid absolute novelty claims.",
            "- If data is risky, build a smaller MVP with public or collectable data first.",
        ]
    )

    write_text(out_dir / "topic_fit_report.md", "\n".join(lines) + "\n")
    print(category)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
