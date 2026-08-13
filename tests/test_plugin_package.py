from __future__ import annotations

import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SKILL_NAME = "research-project-builder"
sys.path.insert(0, str(SCRIPTS))

import build_plugin_package as package_builder  # noqa: E402


def run_git(source: Path, *args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(source), *args],
        input=input_bytes,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_file(root: Path, relative_path: str, content: bytes) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def make_source(parent: Path) -> Path:
    source = parent / "source"
    source.mkdir()
    tracked_files = {
        ".codex-plugin/plugin.json": b'{"name":"research-project-builder"}\n',
        "SKILL.md": b"---\nname: research-project-builder\ndescription: Test skill.\n---\n",
        "README.md": b"# Test skill\n",
        "AGENTS.md": b"# Test agent contract\n",
        "agents/openai.yaml": b'interface:\n  display_name: "Test"\n',
        "assets/icon-small.png": b"small-icon",
        "assets/icon-large.png": b"large-icon",
        "assets/social-preview.png": b"social-preview",
        "assets/templates/runtime.txt": b"runtime-template",
        "references/runtime.md": b"runtime-reference",
        "scripts/runtime.py": b"print('runtime')\n",
        "scripts/build_plugin_package.py": b"raise SystemExit('source-only')\n",
    }
    for relative_path, content in tracked_files.items():
        write_file(source, relative_path, content)
    run_git(source, "init", "--quiet")
    run_git(source, "add", "--all")
    return source


def tree_fingerprint(root: Path) -> list[tuple[str, str, int, int]]:
    fingerprint: list[tuple[str, str, int, int]] = []
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        fingerprint.append(
            (
                path.relative_to(root).as_posix(),
                hashlib.sha256(path.read_bytes()).hexdigest(),
                stat.S_IMODE(path.stat().st_mode),
                path.stat().st_mtime_ns,
            )
        )
    return fingerprint


class PluginPackageTests(unittest.TestCase):
    def test_package_uses_tracked_whitelist_and_contains_stage0_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source = make_source(temp_root)
            write_file(source, "assets/private-notes.txt", b"must never ship")
            output = temp_root / "release" / SKILL_NAME

            package_builder.build_plugin(output, source_root=source)

            packaged_skill = output / "skills" / SKILL_NAME
            for relative_path in ("SKILL.md", "README.md", "AGENTS.md"):
                self.assertEqual(
                    (packaged_skill / relative_path).read_bytes(),
                    (source / relative_path).read_bytes(),
                )
            self.assertFalse((packaged_skill / "assets" / "private-notes.txt").exists())
            self.assertFalse((output / "assets" / "private-notes.txt").exists())
            self.assertFalse((packaged_skill / "scripts" / "build_plugin_package.py").exists())

    def test_output_inside_source_root_is_rejected_without_creating_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = make_source(Path(tmp))
            output = source / "release" / SKILL_NAME

            with self.assertRaisesRegex(ValueError, "outside the source root"):
                package_builder.build_plugin(output, source_root=source)

            self.assertFalse(output.exists())

    def test_existing_target_is_rejected_and_left_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source = make_source(temp_root)
            output = temp_root / "release" / SKILL_NAME
            output.mkdir(parents=True)
            marker = output / "keep.txt"
            marker.write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "already exists"):
                package_builder.build_plugin(output, source_root=source)

            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_copy_failure_leaves_no_target_or_staging_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source = make_source(temp_root)
            (source / "README.md").unlink()
            release_parent = temp_root / "release"
            output = release_parent / SKILL_NAME

            with self.assertRaisesRegex(ValueError, "tracked file is missing"):
                package_builder.build_plugin(output, source_root=source)

            self.assertFalse(output.exists())
            self.assertEqual(list(release_parent.glob(f".{SKILL_NAME}.tmp-*")), [])

    def test_two_fresh_builds_are_byte_and_metadata_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source = make_source(temp_root)
            first = temp_root / "release-a" / SKILL_NAME
            second = temp_root / "release-b" / SKILL_NAME

            package_builder.build_plugin(first, source_root=source)
            package_builder.build_plugin(second, source_root=source)

            self.assertEqual(tree_fingerprint(first), tree_fingerprint(second))

    def test_out_of_tree_source_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source = make_source(temp_root)
            write_file(temp_root, "private.txt", b"private")

            with self.assertRaisesRegex(ValueError, "stay inside the source root"):
                package_builder.validate_source_file(source, "../private.txt", "100644")

    def test_git_symlink_entry_is_rejected_even_on_windows_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source = make_source(temp_root)
            blob = run_git(source, "hash-object", "-w", "--stdin", input_bytes=b"../private.txt").stdout.strip()
            run_git(
                source,
                "update-index",
                "--add",
                "--cacheinfo",
                f"120000,{blob.decode('ascii')},assets/linked-private.txt",
            )
            output = temp_root / "release" / SKILL_NAME

            with self.assertRaisesRegex(ValueError, "symbolic link"):
                package_builder.build_plugin(output, source_root=source)

            self.assertFalse(output.exists())

    def test_real_package_passes_stage0_and_available_official_validators(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            plugin_root = temp_root / "release" / SKILL_NAME
            package_builder.build_plugin(plugin_root, source_root=ROOT)
            packaged_skill = plugin_root / "skills" / SKILL_NAME
            stage0_output = temp_root / "stage0"

            subprocess.run(
                [
                    sys.executable,
                    "scripts/render_strategic_gate.py",
                    "--idea",
                    "generative AI and graduate student research productivity",
                    "--out-dir",
                    str(stage0_output),
                ],
                cwd=packaged_skill,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_output.py",
                    "--out-dir",
                    str(stage0_output),
                    "--mode",
                    "stage0",
                    "--user-input",
                    "generative AI and graduate student research productivity",
                    "--project-root",
                    ".",
                ],
                cwd=packaged_skill,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )

            skill_validator = Path(
                os.environ.get(
                    "CODEX_SKILL_VALIDATOR",
                    r"D:\Codex work\.codex\skills\.system\skill-creator\scripts\quick_validate.py",
                )
            )
            plugin_validator = Path(
                os.environ.get(
                    "CODEX_PLUGIN_VALIDATOR",
                    r"D:\Codex work\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py",
                )
            )
            if skill_validator.is_file() and plugin_validator.is_file():
                subprocess.run(
                    [sys.executable, "-X", "utf8", str(skill_validator), str(packaged_skill)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=30,
                )
                subprocess.run(
                    [sys.executable, "-X", "utf8", str(plugin_validator), str(plugin_root)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=30,
                )


if __name__ == "__main__":
    unittest.main()
