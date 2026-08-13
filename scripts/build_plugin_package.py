#!/usr/bin/env python3
"""Build an installable Codex plugin from the canonical root skill."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "research-project-builder"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New plugin package directory")
    return parser.parse_args()


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "build_plugin_package.py"),
    )


def build_plugin(output: Path) -> Path:
    output = output.expanduser().resolve()
    if output == ROOT or output.exists():
        raise ValueError(f"output must be a new directory distinct from the source root: {output}")

    packaged_skill = output / "skills" / SKILL_NAME
    packaged_skill.mkdir(parents=True)

    copy_tree(ROOT / ".codex-plugin", output / ".codex-plugin")
    copy_tree(ROOT / "assets", output / "assets")
    shutil.copy2(ROOT / "SKILL.md", packaged_skill / "SKILL.md")
    for directory in ("agents", "assets", "references", "scripts"):
        copy_tree(ROOT / directory, packaged_skill / directory)

    return output


def main() -> None:
    args = parse_args()
    try:
        plugin_root = build_plugin(args.output)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(f"Plugin package built: {plugin_root}")


if __name__ == "__main__":
    main()
