#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import urllib.error
from pathlib import Path

from _common import dump_json, fetch_json, now_iso, output_dir_from_args, write_text


CORE_ENDPOINTS = [
    {
        "name": "OpenAlex",
        "url": "https://api.openalex.org/works?search=test&per-page=1",
    },
    {
        "name": "Semantic Scholar",
        "url": "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1&fields=title",
    },
    {
        "name": "Crossref",
        "url": "https://api.crossref.org/works?query=test&rows=1",
    },
]

OPTIONAL_ENDPOINTS = {
    "pubmed": {
        "name": "PubMed / NCBI E-utilities",
        "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test&retmode=json&retmax=1",
    },
    "arxiv": {
        "name": "arXiv",
        "url": "https://export.arxiv.org/api/query?search_query=all:test&start=0&max_results=1",
    },
    "eric": {
        "name": "ERIC",
        "url": "https://api.ies.ed.gov/eric/?search=test&format=json&rows=1",
    },
    "clinicaltrials": {
        "name": "ClinicalTrials.gov",
        "url": "https://clinicaltrials.gov/api/v2/studies?query.term=test&pageSize=1",
    },
    "paperswithcode": {
        "name": "Papers with Code",
        "url": "https://paperswithcode.com/api/v1/papers/?q=test&page_size=1",
    },
}

LIVE_WEB_CHECK = {
    "name": "Live Web via Codex web_search",
    "url": "codex://web_search",
    "status": "AGENT_REQUIRED",
    "note": "The Codex agent must run live web search for current webpages, grey literature, datasets, guidelines, benchmarks, and source discovery before making current-state claims.",
}


def check_endpoint(endpoint: dict[str, str], timeout: int) -> dict[str, str | int | bool]:
    started = time.monotonic()
    try:
        if endpoint["name"] == "arXiv":
            from _common import fetch_text

            text = fetch_text(endpoint["url"], timeout=timeout)
            ok = "<feed" in text.lower()
        else:
            fetch_json(endpoint["url"], timeout=timeout)
            ok = True
        elapsed = int((time.monotonic() - started) * 1000)
        return {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "ok": ok,
            "elapsed_ms": elapsed,
            "error": "",
        }
    except Exception as exc:  # network diagnostics should report all failures
        elapsed = int((time.monotonic() - started) * 1000)
        return {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "ok": False,
            "elapsed_ms": elapsed,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether core scholarly APIs are reachable.")
    parser.add_argument("--out-dir", required=True, help="Output directory for the current run.")
    parser.add_argument(
        "--domain",
        action="append",
        default=[],
        help="Optional domain: pubmed, arxiv, eric, clinicaltrials, paperswithcode.",
    )
    parser.add_argument("--all-optional", action="store_true", help="Check all optional structured sources.")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--allow-partial", action="store_true", help="Write report without failing when a source is down.")
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    endpoints = list(CORE_ENDPOINTS)
    domains = list(OPTIONAL_ENDPOINTS) if args.all_optional else args.domain
    for domain in domains:
        key = domain.lower().strip()
        if key in OPTIONAL_ENDPOINTS:
            endpoints.append(OPTIONAL_ENDPOINTS[key])

    results = [check_endpoint(endpoint, args.timeout) for endpoint in endpoints]
    failed_core = [row for row in results[: len(CORE_ENDPOINTS)] if not row["ok"]]

    report_lines = [
        "# Preflight Web Report",
        "",
        f"- Checked at: {now_iso()}",
        f"- Required core sources: {', '.join(row['name'] for row in CORE_ENDPOINTS)}",
        "",
        "| Source | Status | Latency | Endpoint | Error |",
        "|---|---:|---:|---|---|",
    ]
    for row in results:
        status = "OK" if row["ok"] else "FAILED"
        report_lines.append(
            f"| {row['name']} | {status} | {row['elapsed_ms']} ms | {row['url']} | {row['error']} |"
        )
    report_lines.extend(
        [
            "",
            "## Codex Live Web Search",
            f"- Source: {LIVE_WEB_CHECK['name']}",
            f"- Status: {LIVE_WEB_CHECK['status']}",
            f"- Requirement: {LIVE_WEB_CHECK['note']}",
        ]
    )

    write_text(out_dir / "preflight_report.md", "\n".join(report_lines) + "\n")
    dump_json(out_dir / "preflight_status.json", {"checked_at": now_iso(), "results": results, "live_web_check": LIVE_WEB_CHECK})

    if failed_core and not args.allow_partial:
        print("Core source preflight failed. See preflight_report.md.")
        return 2
    print("Preflight complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
