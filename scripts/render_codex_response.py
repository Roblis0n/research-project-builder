#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _common import load_json, output_dir_from_args, read_csv_dicts, read_text, write_text
from render_strategic_gate import strategic_gate_text


def live_web_summary(out_dir: Path) -> str:
    payload = load_json(out_dir / "live_web_sources.json", default={})
    sources = payload.get("sources", []) if isinstance(payload, dict) else []
    if not sources:
        return "- Live web source log is missing or empty; validation should fail before final delivery."
    lines = []
    for i, src in enumerate(sources[:8], start=1):
        title = src.get("title", "Untitled")
        url = src.get("url", "")
        why = src.get("why_it_matters", "")
        query = src.get("query", "")
        lines.append(f"- L{i}: {title} — {why} Query: {query}. URL: {url}")
    return "\n".join(lines)


def matrix_summary(out_dir: Path) -> str:
    rows = read_csv_dicts(out_dir / "evidence_matrix.csv")
    if not rows:
        return "- No evidence matrix rows available."
    nearest = sorted(rows, key=lambda r: float(r.get("similarity_score") or 0), reverse=True)[:8]
    lines = []
    for row in nearest:
        ident = row.get("doi") or row.get("url") or row.get("pmid") or row.get("arxiv_id") or row.get("openalex_id") or row.get("semantic_scholar_id") or "no-id"
        lines.append(
            f"- {row.get('id')}: {row.get('title')} ({row.get('year')}, {row.get('source_database')}) "
            f"— {row.get('similarity_class')}, score {row.get('similarity_score')}; ID: {ident}"
        )
    return "\n".join(lines)


def strategic_state_block() -> str:
    return """## Strategic Decision State

- Default recommendation: use the currently strongest Topic by evidence support, data feasibility, method fit, and first-week executability.
- Choice consequence: the default route prioritizes completion and defensibility; replacing it requires rechecking data, method, and literature crowding.
- Risk judgment: the largest risks usually come from unavailable data, unmeasurable variables, crowded adjacent research, or method complexity beyond the time window.
- Data reality judgment: without committed private data, use public data, small pilot collection, literature evidence matrices, or auditable documents.
- Next execution action: expand the default Topic into theory, constructs, data dictionary, baseline, evaluation metrics, and MVP.
- Non-negotiable core: preserve the research object and core problem by default; allow method, data source, theory, and context to be adjusted.
- Method complexity: start with the minimum defensible method, then upgrade only when data quality supports statistics, causal inference, machine learning, interviews, simulation, or system design.
- Time window: organize around 8-12 weeks by default; week one must produce checkable evidence or data pilot work.
"""


def stage0_response(out_dir: Path, idea: str = "") -> str:
    existing = read_text(out_dir / "codex_inline_response.txt")
    if "Strategic Decision Gate" in existing and "D1" in existing and "D7" in existing:
        return existing
    idea = idea or "You provided a rough research idea that needs strategic routing before search."
    return strategic_gate_text(idea)


def topic_response(out_dir: Path) -> str:
    recommendation = read_text(out_dir / "topic_recommendation.md")
    if not recommendation:
        recommendation = "# Topic Recommendation\n\nNo topic recommendation was generated."
    return f"""# Codex Direct Research Output

This is the direct-display version. Files remain as audit artifacts, but the user does not need to open `.md` files to understand the result.

## Live Web Sources Used

{live_web_summary(out_dir)}

## Evidence Matrix Snapshot

{matrix_summary(out_dir)}

{strategic_state_block()}

{recommendation}

## Operational Note

I will continue with the default recommendation unless the user later corrects a constraint. The next high-value step is not to generate more shallow topics; it is to expand the default Topic into theory, variables, data, method, modeling, and MVP.
"""


def expansion_response(out_dir: Path) -> str:
    pack = read_text(out_dir / "theory_method_model_pack.md") or "# Theory / Method / Model Pack\n\nNo expansion pack was generated."
    project = read_text(out_dir / "project_plan.md")
    risks = read_text(out_dir / "risk_register.md")
    return f"""# Codex Direct Research Expansion

This is the direct-display version. Files remain as audit artifacts, but the user does not need to open `.md` files to understand the result.

## Live Web Sources Used

{live_web_summary(out_dir)}

## Evidence Matrix Snapshot

{matrix_summary(out_dir)}

{strategic_state_block()}

{pack}

# Project Execution Plan

{project}

# Risk Register

{risks}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the user-facing Codex response from generated artifacts.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--mode", choices=["stage0", "topic", "expansion"], default="topic")
    parser.add_argument("--idea", default="", help="Optional rough idea for Stage 0 rendering.")
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    if args.mode == "stage0":
        text = stage0_response(out_dir, args.idea)
    elif args.mode == "topic":
        text = topic_response(out_dir)
    else:
        text = expansion_response(out_dir)
    write_text(out_dir / "codex_inline_response.txt", text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
