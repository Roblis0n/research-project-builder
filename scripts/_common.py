#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

USER_AGENT = os.environ.get(
    "RPB_USER_AGENT",
    "research-project-builder/0.1 (set RPB_USER_AGENT for contact info)",
)

MATRIX_FIELDS = [
    "id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "openalex_id",
    "semantic_scholar_id",
    "pmid",
    "arxiv_id",
    "source_database",
    "abstract",
    "research_question",
    "population_or_context",
    "data_or_sample",
    "method",
    "model",
    "theory",
    "outcome",
    "key_finding",
    "similarity_score",
    "similarity_class",
    "usable_gap",
    "limitations",
    "why_it_matters_for_user_topic",
]

FORBIDDEN_PHRASES = [
    "you must choose",
    "please confirm before i proceed",
    "i cannot continue unless",
    "please choose one",
    "nobody has studied",
    "no one has studied",
    "this is the first",
    "clear blank",
    "guaranteed to publish",
    "definitely novel",
    "absolutely novel",
    "total blank space",
    "as an " + "IN" + "TJ",
    "i will act like an " + "IN" + "TJ",
    "coldly rational",
    "personality type",
    "MB" + "TI",
    "see the markdown file",
    "open the markdown file",
    "open topic_recommendation.md",
    "open project_plan.md",
]


AUTHORIZATION_TRIGGERS = [
    "run defaults",
    "run default strategy",
    "run the default strategy",
    "use default strategy",
    "use the default strategy",
    "start search",
    "start the search",
    "begin search",
    "start topic landing",
    "topic landing",
    "topics only",
    "topic only",
    "continue",
    "revise d1",
    "revise d2",
    "revise d3",
]


STAGE2_TRIGGERS = [
    "expand theory",
    "expand methods",
    "expand modeling",
    "full plan",
    "complete plan",
    "complete project plan",
    "build the full project plan",
    "continue with default topic",
    "continue with the default topic",
    "turn topic",
    "project plan",
]


def contains_any(text: str, triggers: list[str]) -> bool:
    compact = (text or "").lower()
    return any(trigger.lower() in compact for trigger in triggers)


def has_stage1_authorization(text: str) -> bool:
    return contains_any(text, AUTHORIZATION_TRIGGERS)


def has_stage2_trigger(text: str) -> bool:
    return contains_any(text, STAGE2_TRIGGERS)


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def project_root() -> Path:
    """Return the repository/skill root for standalone validation.

    Earlier versions assumed the skill lived under `.agents/skills/...` and
    walked up to the Codex workspace root. This public repository treats the
    skill directory itself as the repository root, so background files such as
    README.md, AGENTS.md, and SKILL.md are validated from `skill_root()`.
    """
    return skill_root()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def today() -> str:
    return date.today().isoformat()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8", errors="replace")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def dump_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def dump_json(path: Path, value: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def slugify(value: str, fallback: str = "research-topic") -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    value = re.sub(r"-{2,}", "-", value)
    return (value or fallback)[:72].strip("-") or fallback


def output_dir_from_args(out_dir: str | None, idea: str | None = None) -> Path:
    if out_dir:
        return ensure_dir(Path(out_dir))
    slug = slugify(idea or "research-topic")
    return ensure_dir(Path("outputs") / f"{today()}-{slug}")


def tokenize(text: str) -> set[str]:
    """Tokenize English terms and CJK text for lightweight similarity scoring.

    The project intentionally avoids mandatory third-party dependencies. For
    Chinese/Japanese/Korean text, this function adds character n-grams so that
    mixed English/CJK titles can still receive a useful rough-overlap score.
    """
    text = text.lower()
    english_tokens = re.findall(r"[a-z][a-z0-9\-]{2,}", text)
    cjk_spans = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    cjk_tokens: list[str] = []
    for span in cjk_spans:
        cjk_tokens.append(span)
        for n in (2, 3):
            if len(span) >= n:
                cjk_tokens.extend(span[i : i + n] for i in range(len(span) - n + 1))
    stop = {
        "and",
        "the",
        "for",
        "with",
        "from",
        "this",
        "that",
        "using",
        "effect",
        "impact",
        "study",
        "research",
        "analysis",
    }
    tokens = english_tokens + cjk_tokens
    return {t.strip("-") for t in tokens if t.strip("-") and t not in stop}


def overlap_score(a: str, b: str) -> float:
    left = tokenize(a)
    right = tokenize(b)
    if not left or not right:
        return 0.0
    return len(left & right) / max(1, min(len(left), len(right)))


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def similarity_class(score: float) -> str:
    if score >= 0.80:
        return "highly similar"
    if score >= 0.60:
        return "close adjacent"
    if score >= 0.40:
        return "adjacent"
    if score >= 0.20:
        return "background"
    return "weak relevance"


def fetch_json(url: str, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
    return json.loads(body.decode("utf-8", errors="replace"))


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
    return body.decode("utf-8", errors="replace")


def url_with_query(base: str, params: dict[str, Any]) -> str:
    return base + "?" + urllib.parse.urlencode(params, doseq=True)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_dicts(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def extract_idea(out_dir: Path) -> str:
    intake = read_text(out_dir / "intake_brief.md")
    patterns = [
        r"## Original Idea\s*\n+(.+?)(?:\n##|\Z)",
        r"Original idea:\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, intake, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return " ".join(match.group(1).strip().split())
    terms = read_text(out_dir / "search_terms.md")
    match = re.search(r"### 1\. Precise query\s*\n+(.+?)(?:\n###|\Z)", terms, flags=re.DOTALL)
    if match:
        return " ".join(match.group(1).strip().split())
    return ""


def parse_query_families(search_terms: str) -> list[dict[str, str]]:
    families: list[dict[str, str]] = []
    pattern = re.compile(r"###\s*(?:\d+\.\s*)?(.+?)\s*\n+(.+?)(?=\n###|\Z)", re.DOTALL)
    for match in pattern.finditer(search_terms):
        name = re.sub(r"\s+", " ", match.group(1)).strip().lower()
        body = " ".join(line.strip("- ").strip() for line in match.group(2).splitlines() if line.strip())
        if body:
            families.append({"name": slugify(name, "query"), "query": body})
    if families:
        return families
    compact = " ".join(search_terms.split())
    return [{"name": "precise", "query": compact[:300]}] if compact else []


def abstract_from_inverted_index(index: Any) -> str:
    if not isinstance(index, dict):
        return ""
    positions: dict[int, str] = {}
    for word, indexes in index.items():
        if isinstance(indexes, list):
            for pos in indexes:
                if isinstance(pos, int):
                    positions[pos] = word
    return " ".join(positions[pos] for pos in sorted(positions))


def normalize_space(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = "; ".join(str(item) for item in value if item is not None)
    return re.sub(r"\s+", " ", str(value)).strip()


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", title.lower())[:160]


def print_error(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
