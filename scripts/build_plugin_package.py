#!/usr/bin/env python3
"""Build an installable Codex plugin from Git-tracked canonical skill files."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "research-project-builder"
DETERMINISTIC_MTIME_NS = 315_532_800_000_000_000  # 1980-01-01 UTC

PLUGIN_FILES = {
    ".codex-plugin/plugin.json": ".codex-plugin/plugin.json",
    "assets/icon-small.png": "assets/icon-small.png",
    "assets/icon-large.png": "assets/icon-large.png",
    "assets/social-preview.png": "assets/social-preview.png",
}
SKILL_ROOT_FILES = {
    "SKILL.md",
    "SKILL.zh-CN.md",
    "README.md",
    "README.zh-CN.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
}
SKILL_PREFIXES = (
    "agents/",
    "assets/",
    "references/",
    "scripts/",
    "examples/",
    "tests/fixtures/topic_output/",
)
SOURCE_ONLY_FILES = {"scripts/build_plugin_package.py"}
REQUIRED_TRACKED_FILES = set(PLUGIN_FILES) | SKILL_ROOT_FILES | {"agents/openai.yaml"}
ALLOWED_GIT_MODES = {"100644", "100755"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Fresh package path outside the source root; basename must be research-project-builder",
    )
    return parser.parse_args()


def git_tracked_entries(source_root: Path) -> list[tuple[str, str, str]]:
    completed = subprocess.run(
        ["git", "-C", str(source_root), "ls-files", "--stage", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    entries: list[tuple[str, str, str]] = []
    for record in completed.stdout.split(b"\0"):
        if not record:
            continue
        header, raw_path = record.split(b"\t", 1)
        raw_mode, raw_object_id, raw_stage = header.split(b" ", 2)
        if raw_stage != b"0":
            raise ValueError("Git index contains an unresolved merge entry")
        entries.append(
            (
                raw_path.decode("utf-8"),
                raw_mode.decode("ascii"),
                raw_object_id.decode("ascii"),
            )
        )
    return entries


def _is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if is_junction is not None and is_junction():
        return True
    try:
        attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def validate_source_file(source_root: Path, relative_path: str, git_mode: str) -> Path:
    source_root = source_root.resolve()
    candidate = PurePosixPath(relative_path)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"tracked paths must stay inside the source root: {relative_path}")
    if git_mode == "120000":
        raise ValueError(f"tracked symbolic links are not allowed in plugin packages: {relative_path}")
    if git_mode not in ALLOWED_GIT_MODES:
        raise ValueError(f"unsupported Git mode {git_mode} for packaged file: {relative_path}")

    source_path = source_root.joinpath(*candidate.parts)
    current = source_root
    for part in candidate.parts:
        current /= part
        if _is_link_like(current):
            raise ValueError(f"symbolic links and junctions are not allowed: {relative_path}")
    if source_path.exists():
        resolved_source = source_path.resolve(strict=True)
        if not resolved_source.is_relative_to(source_root):
            raise ValueError(f"tracked paths must stay inside the source root: {relative_path}")
        if not source_path.is_file():
            raise ValueError(f"packaged Git entry is not a regular file: {relative_path}")
    return source_path


def package_targets(relative_path: str) -> list[str]:
    targets: list[str] = []
    plugin_target = PLUGIN_FILES.get(relative_path)
    if plugin_target is not None:
        targets.append(plugin_target)
    if relative_path in SKILL_ROOT_FILES or (
        relative_path.startswith(SKILL_PREFIXES) and relative_path not in SOURCE_ONLY_FILES
    ):
        targets.append(f"skills/{SKILL_NAME}/{relative_path}")
    return targets


def build_copy_plan(source_root: Path) -> list[tuple[str, str, str]]:
    tracked_entries = git_tracked_entries(source_root)
    tracked_paths = {relative_path for relative_path, _mode, _object_id in tracked_entries}
    missing = sorted(REQUIRED_TRACKED_FILES - tracked_paths)
    if missing:
        raise ValueError(f"required package files are not Git tracked: {', '.join(missing)}")

    plan: list[tuple[str, str, str]] = []
    for relative_path, git_mode, object_id in tracked_entries:
        targets = package_targets(relative_path)
        if not targets:
            continue
        validate_source_file(source_root, relative_path, git_mode)
        for target in targets:
            plan.append((object_id, target, git_mode))
    return sorted(plan, key=lambda item: item[1])


def _copy_blob(source_root: Path, object_id: str, destination: Path, git_mode: str) -> None:
    completed = subprocess.run(
        ["git", "-C", str(source_root), "cat-file", "blob", object_id],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(completed.stdout)
    destination.chmod(0o755 if git_mode == "100755" else 0o644)
    os.utime(destination, ns=(DETERMINISTIC_MTIME_NS, DETERMINISTIC_MTIME_NS))


def _normalize_directory_metadata(root: Path) -> None:
    directories = [path for path in root.rglob("*") if path.is_dir()]
    directories.append(root)
    for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        directory.chmod(0o755)
        os.utime(directory, ns=(DETERMINISTIC_MTIME_NS, DETERMINISTIC_MTIME_NS))


def build_plugin(output: Path, *, source_root: Path = ROOT) -> Path:
    source_root = source_root.expanduser().resolve()
    output = output.expanduser().resolve()
    if output.name != SKILL_NAME:
        raise ValueError(f"output basename must be {SKILL_NAME}")
    if output == source_root or output.is_relative_to(source_root):
        raise ValueError("output must be outside the source root to prevent recursive packaging")
    if output.exists() or output.is_symlink():
        raise ValueError(f"output already exists: {output}")

    copy_plan = build_copy_plan(source_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{SKILL_NAME}.tmp-", dir=output.parent))
    try:
        for object_id, target, git_mode in copy_plan:
            _copy_blob(source_root, object_id, staging.joinpath(*PurePosixPath(target).parts), git_mode)
        _normalize_directory_metadata(staging)
        if output.exists() or output.is_symlink():
            raise ValueError(f"output already exists: {output}")
        staging.rename(output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def main() -> None:
    args = parse_args()
    try:
        plugin_root = build_plugin(args.output)
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError) as error:
        raise SystemExit(f"Plugin package build failed: {error}") from error
    print(f"Plugin package built: {plugin_root}")


if __name__ == "__main__":
    main()
