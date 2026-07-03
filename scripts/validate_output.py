#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _common import (
    FORBIDDEN_PHRASES,
    MATRIX_FIELDS,
    has_stage1_authorization,
    has_stage2_trigger,
    load_json,
    output_dir_from_args,
    project_root,
    read_csv_dicts,
    read_text,
)

BACKGROUND_FILE_CANDIDATES = [
    ["README.md"],
    ["AGENTS.md"],
    ["SKILL.md", ".agents/skills/research-project-builder/SKILL.md"],
    ["references/user_workflow_and_purpose.md", ".agents/skills/research-project-builder/references/user_workflow_and_purpose.md"],
]

BACKGROUND_KEYWORDS = [
    "rough research idea",
    "executable research project",
    "Strategic Decision Gate",
    "user workflow",
    "not an autopilot topic generator",
    "live literature search",
    "theory/method/model expansion",
    "strategic research architect",
]

STAGE0_REQUIRED_TERMS = [
    "Strategic Decision Gate",
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "D6",
    "D7",
    "Run defaults",
    "Use default strategy",
    "Why this changes the route",
]

AUTOPILOT_ARTIFACTS = [
    "search_manifest.json",
    "evidence_matrix.csv",
    "topic_recommendation.md",
    "project_plan.md",
]

LIVE_EVIDENCE_FILES = [
    "live_web_sources.json",
    "search_manifest.json",
    "evidence_matrix.csv",
]

BEHAVIOR_REQUIRED_TERMS = [
    "Default recommendation",
    "Choice consequence",
    "Risk judgment",
    "Data reality judgment",
    "Next execution action",
    "Non-negotiable core",
    "Method complexity",
    "Time window",
]

PSEUDO_STYLE_FORBIDDEN = [
    "as an " + "IN" + "TJ",
    "I will act like an " + "IN" + "TJ",
    "coldly rational",
    "personality type",
    "MB" + "TI",
]


TOPIC_DEPTH_TERMS = [
    "Research object",
    "Unit of analysis",
    "Existing literature basis",
    "Difference from existing work",
    "Core gap",
    "Minimum data",
    "Data acquisition route",
    "Minimum method",
    "Optional advanced method",
    "Tool stack",
    "Expected output",
    "First-week action",
    "Failure condition",
    "Risk",
    "Fallback option",
    "Later expansion direction",
]

TOPIC_REQUIRED_SECTIONS = [
    "Live Search Scope",
    "Closest Existing Research",
    "Coverage Judgment",
    "Executable Topic Candidates",
    "Default Recommendation",
    "Execution Route for the Default Recommendation",
    "Strategic Decision State",
    "Strategic Decision Questions",
    "Later Expansion Path",
]

CLOSEST_RESEARCH_BUCKETS = ["Highly similar", "Adjacent research", "Method/theory borrowing candidates"]

EXPANSION_REQUIRED_TERMS = [
    "Selected Topic",
    "Theory Candidate Table",
    "Recommended Main Theory",
    "Why Not Use Other Theories",
    "Conceptual Model",
    "Constructs/Variables",
    "Hypotheses or Propositions",
    "Data Plan",
    "Method Route",
    "Statistical Model / Machine Learning Model / Simulation Model",
    "baseline",
    "candidate models",
    "evaluation metrics",
    "robustness checks",
    "Tool Stack",
    "MVP",
    "12-Week Execution Plan",
    "Risks and Fallback Routes",
    "Writing Structure",
]

REQUIRED_TOPIC_FILES = [
    "preflight_report.md",
    "live_web_sources.json",
    "intake_brief.md",
    "search_terms.md",
    "search_manifest.json",
    "evidence_matrix.csv",
    "topic_options.md",
    "topic_recommendation.md",
    "codex_inline_response.txt",
]

REQUIRED_EXPANSION_FILES = [
    "theory_method_model_pack.md",
    "project_plan.md",
    "risk_register.md",
    "codex_inline_response.txt",
]


def add_missing_terms(name: str, text: str, terms: list[str], errors: list[str], *, min_count: int | None = None) -> None:
    missing = [term for term in terms if term.lower() not in text.lower()]
    if min_count is None:
        if missing:
            errors.append(f"{name} missing required terms: {', '.join(missing)}")
    else:
        found = len(terms) - len(missing)
        if found < min_count:
            errors.append(f"{name} has only {found}/{len(terms)} background terms; missing: {', '.join(missing)}")


def check_project_background(root: Path, errors: list[str]) -> None:
    for candidates in BACKGROUND_FILE_CANDIDATES:
        path = next((root / rel for rel in candidates if (root / rel).exists()), None)
        if path is None:
            errors.append(f"Missing background file: one of {', '.join(candidates)}")
            continue
        text = read_text(path)
        add_missing_terms(str(path.relative_to(root)), text, BACKGROUND_KEYWORDS, errors, min_count=7)


def check_required_files(out_dir: Path, names: list[str], errors: list[str]) -> None:
    for name in names:
        path = out_dir / name
        if not path.exists():
            errors.append(f"Missing required file: {name}")
        elif path.stat().st_size == 0:
            errors.append(f"Required file is empty: {name}")


def check_stage0_gate(out_dir: Path, errors: list[str]) -> None:
    text = read_text(out_dir / "codex_inline_response.txt")
    if not text.strip():
        errors.append("Stage 0 requires codex_inline_response.txt with Strategic Decision Gate.")
        return
    add_missing_terms("Stage 0 codex_inline_response.txt", text, STAGE0_REQUIRED_TERMS, errors)
    add_missing_terms("Stage 0 behavior", text, BEHAVIOR_REQUIRED_TERMS, errors)


def check_no_autopilot_without_authorization(out_dir: Path, user_input: str, errors: list[str]) -> None:
    authorized = has_stage1_authorization(user_input) or has_stage2_trigger(user_input)
    if authorized:
        return
    for artifact in AUTOPILOT_ARTIFACTS:
        if (out_dir / artifact).exists():
            errors.append(f"Autopilot violation: {artifact} exists without user authorization.")


def check_stage2_only_after_trigger(out_dir: Path, user_input: str, errors: list[str]) -> None:
    if has_stage2_trigger(user_input):
        return
    for artifact in ["theory_method_model_pack.md", "project_plan.md", "risk_register.md"]:
        if (out_dir / artifact).exists():
            errors.append(f"Stage 2 violation: {artifact} exists without Stage 2 trigger.")


def check_forbidden_text(out_dir: Path, errors: list[str]) -> None:
    for path in out_dir.glob("*"):
        if path.suffix.lower() not in {".md", ".csv", ".json", ".jsonl", ".txt"}:
            continue
        text = read_text(path)
        lowered = text.lower()
        for phrase in FORBIDDEN_PHRASES + PSEUDO_STYLE_FORBIDDEN:
            if phrase.lower() in lowered:
                errors.append(f"Forbidden phrase in {path.name}: {phrase}")


def check_inline_response(out_dir: Path, mode: str, errors: list[str]) -> None:
    path = out_dir / "codex_inline_response.txt"
    if not path.exists() or path.stat().st_size == 0:
        errors.append("codex_inline_response.txt is required for direct Codex display.")
        return
    text = read_text(path)
    if len(text.strip()) < 300:
        errors.append("codex_inline_response.txt is too short to be the main direct-display result.")
    lowered = text.lower()
    if "open topic_recommendation.md" in lowered or "open project_plan.md" in lowered or "see the markdown file" in lowered:
        errors.append("codex_inline_response.txt must not rely on opening generated markdown files.")
    if mode == "stage0" and "Strategic Decision Gate" not in text:
        errors.append("Stage 0 inline response must contain Strategic Decision Gate.")
    if mode == "topic" and "Codex Direct Research Output" not in text:
        errors.append("Topic inline response must contain Codex Direct Research Output.")
    if mode == "expansion" and "Codex Direct Research Expansion" not in text:
        errors.append("Expansion inline response must contain Codex Direct Research Expansion.")


def check_behavior_terms(out_dir: Path, errors: list[str]) -> None:
    text = read_text(out_dir / "codex_inline_response.txt")
    add_missing_terms("codex_inline_response.txt behavior", text, BEHAVIOR_REQUIRED_TERMS, errors)


def check_live_web_sources(out_dir: Path, errors: list[str]) -> None:
    path = out_dir / "live_web_sources.json"
    if not path.exists():
        errors.append("Missing required live evidence file: live_web_sources.json")
        return
    payload = load_json(path, default=None)
    if isinstance(payload, list):
        if not payload:
            errors.append("live_web_sources.json must not be an empty array.")
            return
        sources = payload
    elif isinstance(payload, dict):
        sources = payload.get("sources")
    else:
        errors.append("live_web_sources.json must be a JSON object with sources or a non-empty source array.")
        return
    if not isinstance(sources, list) or not sources:
        errors.append("live_web_sources.json must contain at least one source.")
        return
    for i, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"live_web_sources.json source {i} is not an object.")
            continue
        for field in ["query", "title", "url", "source_type", "why_it_matters", "retrieved_at"]:
            if not str(source.get(field) or "").strip():
                errors.append(f"live_web_sources.json source {i} missing field: {field}")
        url = str(source.get("url") or "")
        if url and not (url.startswith("https://") or url.startswith("http://")):
            errors.append(f"live_web_sources.json source {i} has invalid URL: {url}")


def check_manifest(out_dir: Path, errors: list[str]) -> None:
    path = out_dir / "search_manifest.json"
    if not path.exists():
        errors.append("Missing required live evidence file: search_manifest.json")
        return
    try:
        manifest = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid search_manifest.json: {exc}")
        return
    if not manifest.get("query_families"):
        errors.append("search_manifest.json has no query_families.")
    databases = set(manifest.get("databases") or [])
    for required in ["OpenAlex", "Semantic Scholar", "Crossref"]:
        if required not in databases:
            errors.append(f"search_manifest.json missing required database: {required}")
    if not any("Live Web" in str(source) for source in databases):
        errors.append("search_manifest.json must record Live Web search as a required source.")
    if manifest.get("live_web_evidence_file") != "live_web_sources.json":
        errors.append("search_manifest.json must identify live_web_sources.json as the live web evidence file.")


def check_matrix(out_dir: Path, errors: list[str]) -> None:
    path = out_dir / "evidence_matrix.csv"
    if not path.exists():
        errors.append("Missing required live evidence file: evidence_matrix.csv")
        return
    rows = read_csv_dicts(path)
    if not rows:
        errors.append("evidence_matrix.csv has no evidence rows.")
        return
    missing_columns = [field for field in MATRIX_FIELDS if field not in rows[0]]
    if missing_columns:
        errors.append(f"evidence_matrix.csv missing columns: {', '.join(missing_columns)}")
    for row in rows[:20]:
        identifiers = [
            row.get("doi", "").strip(),
            row.get("url", "").strip(),
            row.get("pmid", "").strip(),
            row.get("arxiv_id", "").strip(),
            row.get("semantic_scholar_id", "").strip(),
            row.get("openalex_id", "").strip(),
        ]
        if not any(identifiers):
            errors.append(f"Evidence row {row.get('id', '?')} lacks DOI, URL, PMID, arXiv ID, Semantic Scholar ID, or OpenAlex ID.")
            break


def check_live_evidence_pack(out_dir: Path, errors: list[str]) -> None:
    for name in LIVE_EVIDENCE_FILES:
        if not (out_dir / name).exists():
            errors.append(f"Stage 1/2 requires {name}.")
    check_live_web_sources(out_dir, errors)
    check_manifest(out_dir, errors)
    check_matrix(out_dir, errors)


def split_topic_blocks(text: str) -> list[str]:
    parts = re.split(r"(?=^##\s+Topic\s+\d+\b)", text, flags=re.MULTILINE)
    return [part for part in parts if re.match(r"^##\s+Topic\s+\d+\b", part.strip())]


def check_topic_depth(out_dir: Path, errors: list[str]) -> None:
    recommendation = read_text(out_dir / "topic_recommendation.md")
    inline = read_text(out_dir / "codex_inline_response.txt")
    combined = recommendation + "\n" + inline
    for section in TOPIC_REQUIRED_SECTIONS:
        if section not in combined:
            errors.append(f"Topic output missing section: {section}")
    for bucket in CLOSEST_RESEARCH_BUCKETS:
        if bucket not in combined:
            errors.append(f"Topic output missing closest-research bucket: {bucket}")
    blocks = split_topic_blocks(combined)
    if len(blocks) < 3:
        errors.append("Topic output must contain at least 3 Topic blocks.")
        return
    for i, block in enumerate(blocks[:5], start=1):
        missing = [term for term in TOPIC_DEPTH_TERMS if term.lower() not in block.lower()]
        if missing:
            errors.append(f"Topic {i} missing depth terms: {', '.join(missing)}")
    if "My default recommendation is" not in combined:
        errors.append("Topic output must contain explicit default recommendation: My default recommendation is.")
    if "not a demand that the user choose now" not in combined and "not required to choose" not in combined:
        errors.append("Topic output must explicitly avoid forcing the user to choose.")


def check_expansion_depth(out_dir: Path, errors: list[str]) -> None:
    text = read_text(out_dir / "theory_method_model_pack.md") + "\n" + read_text(out_dir / "codex_inline_response.txt")
    add_missing_terms("Stage 2 expansion", text, EXPANSION_REQUIRED_TERMS, errors)
    for term in [
        "Why to use it",
        "Which research question it answers",
        "What data it requires",
        "How to replace it if it fails",
        "How its output becomes a paper section or project-plan deliverable",
    ]:
        if term.lower() not in text.lower():
            errors.append(f"Stage 2 method/model explanation missing: {term}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate research-project-builder output directory and workflow gates.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--mode", choices=["stage0", "topic", "expansion", "all"], default="topic")
    parser.add_argument("--user-input", default="", help="User message that triggered this output.")
    parser.add_argument("--project-root", default="", help="Override project root for background checks.")
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    root = Path(args.project_root).resolve() if args.project_root else project_root()
    errors: list[str] = []

    check_project_background(root, errors)
    check_no_autopilot_without_authorization(out_dir, args.user_input, errors)
    check_stage2_only_after_trigger(out_dir, args.user_input, errors)
    check_forbidden_text(out_dir, errors)

    if args.mode in {"stage0", "all"}:
        check_stage0_gate(out_dir, errors)
        check_inline_response(out_dir, "stage0", errors)

    if args.mode in {"topic", "all"}:
        check_required_files(out_dir, REQUIRED_TOPIC_FILES, errors)
        check_live_evidence_pack(out_dir, errors)
        check_topic_depth(out_dir, errors)
        check_inline_response(out_dir, "topic", errors)
        check_behavior_terms(out_dir, errors)

    if args.mode in {"expansion", "all"}:
        check_required_files(out_dir, REQUIRED_EXPANSION_FILES, errors)
        check_live_evidence_pack(out_dir, errors)
        check_expansion_depth(out_dir, errors)
        check_inline_response(out_dir, "expansion", errors)
        check_behavior_terms(out_dir, errors)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
