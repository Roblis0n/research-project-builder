#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import dump_json, load_json, now_iso, output_dir_from_args, read_text

REQUIRED_SOURCE_FIELDS = ["query", "title", "url", "source_type", "why_it_matters", "retrieved_at"]


def normalize_source(raw: dict[str, Any]) -> dict[str, Any]:
    source = {
        "query": str(raw.get("query") or "").strip(),
        "title": str(raw.get("title") or "").strip(),
        "url": str(raw.get("url") or "").strip(),
        "source_type": str(raw.get("source_type") or raw.get("type") or "live-web").strip(),
        "why_it_matters": str(raw.get("why_it_matters") or raw.get("why") or "").strip(),
        "retrieved_at": str(raw.get("retrieved_at") or now_iso()).strip(),
    }
    source["notes"] = str(raw.get("notes") or "").strip()
    return source


def validate_sources(sources: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not sources:
        errors.append("live_web_sources.json must contain at least one source recorded from live web search.")
        return errors
    for i, source in enumerate(sources, start=1):
        for field in REQUIRED_SOURCE_FIELDS:
            if not str(source.get(field) or "").strip():
                errors.append(f"Live web source {i} missing required field: {field}")
        url = str(source.get("url") or "")
        if url and not (url.startswith("http://") or url.startswith("https://")):
            errors.append(f"Live web source {i} has non-http URL: {url}")
    return errors


def load_from_json(path: Path) -> list[dict[str, Any]]:
    value = load_json(path, default=[])
    if isinstance(value, dict) and isinstance(value.get("sources"), list):
        value = value["sources"]
    if not isinstance(value, list):
        raise SystemExit("Input JSON must be a list or an object with a 'sources' list.")
    return [normalize_source(row) for row in value if isinstance(row, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record live web-search sources used by Codex for the current research run.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--from-json", help="JSON file containing a source list or {sources: [...]}.")
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--title", action="append", default=[])
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--source-type", action="append", default=[])
    parser.add_argument("--why", action="append", default=[])
    parser.add_argument("--notes", action="append", default=[])
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    target = out_dir / "live_web_sources.json"

    if args.validate_only:
        payload = load_json(target, default={})
        sources = payload.get("sources", []) if isinstance(payload, dict) else []
        errors = validate_sources(sources)
        if errors:
            for error in errors:
                print(error)
            return 1
        print(f"Live web sources valid: {len(sources)}")
        return 0

    sources: list[dict[str, Any]] = []
    if args.from_json:
        sources.extend(load_from_json(Path(args.from_json)))
    elif args.url or args.title or args.query:
        count = max(len(args.query), len(args.title), len(args.url), len(args.source_type), len(args.why), len(args.notes))
        for i in range(count):
            sources.append(
                normalize_source(
                    {
                        "query": args.query[i] if i < len(args.query) else (args.query[-1] if args.query else "live web search"),
                        "title": args.title[i] if i < len(args.title) else "Untitled live web source",
                        "url": args.url[i] if i < len(args.url) else "",
                        "source_type": args.source_type[i] if i < len(args.source_type) else "live-web",
                        "why_it_matters": args.why[i] if i < len(args.why) else "Current source discovery, triangulation, or grey-literature check.",
                        "notes": args.notes[i] if i < len(args.notes) else "",
                    }
                )
            )
    else:
        existing = load_json(target, default={})
        if isinstance(existing, dict) and isinstance(existing.get("sources"), list):
            sources = existing["sources"]

    sources = [normalize_source(source) for source in sources]
    errors = validate_sources(sources)
    if errors:
        for error in errors:
            print(error)
        return 1

    payload = {
        "created_at": now_iso(),
        "purpose": "Audit record of live Codex web_search sources used before topic/gap/method claims.",
        "sources": sources,
    }
    dump_json(target, payload)
    print(f"Recorded {len(sources)} live web sources in {target}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
