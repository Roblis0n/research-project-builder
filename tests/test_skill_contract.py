from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TOPIC_FIXTURE = ROOT / "tests" / "fixtures" / "topic_output"
sys.path.insert(0, str(SCRIPTS))

from _common import has_stage1_authorization, has_stage2_trigger  # noqa: E402


class SkillContractTests(unittest.TestCase):
    def test_chinese_triggers_and_portable_script_paths_are_documented(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for phrase in ("研究选题", "按默认执行", "按默认战略执行", "展开理论", "展开建模"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

        self.assertIn("python scripts/render_strategic_gate.py", text)
        self.assertIn(".agents/skills/research-project-builder/", text)
        self.assertIn("--project-root <skill-dir>", text)
        self.assertIn("Keep all other flags unchanged", text)

    def test_reconciliation_and_plugin_package_keep_contracts(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for required_contract in (
            "stop before search unless the user authorizes Stage 1",
            "No live web evidence, no topic/gap/novelty judgment",
            "live_web_sources.json",
            "search_manifest.json",
            "evidence_matrix.csv",
            "--timeout 20 --retries 1",
            '--project-root .',
        ):
            with self.subTest(required_contract=required_contract):
                self.assertIn(required_contract, text)

        with tempfile.TemporaryDirectory() as tmp:
            plugin_root = Path(tmp) / "research-project-builder"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "build_plugin_package.py"),
                    "--output",
                    str(plugin_root),
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            packaged_skill = plugin_root / "skills" / "research-project-builder"
            self.assertTrue((plugin_root / ".codex-plugin" / "plugin.json").is_file())
            self.assertTrue((plugin_root / "assets" / "social-preview.png").is_file())
            self.assertTrue((packaged_skill / "SKILL.md").is_file())
            self.assertTrue((packaged_skill / "agents" / "openai.yaml").is_file())
            self.assertTrue((packaged_skill / "scripts" / "render_strategic_gate.py").is_file())

    def test_documented_chinese_stage1_phrases_authorize_runtime(self) -> None:
        phrases = (
            "按默认执行",
            "按默认战略执行",
            "开始搜索",
            "进入选题落地",
            "先只给选题",
            "按 D1/D2/D3 的修改执行",
        )

        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertTrue(has_stage1_authorization(phrase))

    def test_documented_chinese_stage2_phrases_authorize_runtime(self) -> None:
        phrases = (
            "展开理论",
            "展开建模",
            "给完整项目方案",
            "继续默认推荐选题",
            "把 Topic X 做成项目方案",
        )

        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertTrue(has_stage2_trigger(phrase))

    def test_validator_accepts_chinese_stage1_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "topic"
            shutil.copytree(TOPIC_FIXTURE, out_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_output.py"),
                    "--out-dir",
                    str(out_dir),
                    "--mode",
                    "topic",
                    "--user-input",
                    "按默认战略执行",
                    "--project-root",
                    str(ROOT),
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )

    def test_validator_accepts_chinese_stage2_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "stage0"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "render_strategic_gate.py"),
                    "--idea",
                    "生成式 AI 与青年政治表达",
                    "--out-dir",
                    str(out_dir),
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            (out_dir / "project_plan.md").write_text("Stage 2 requested.\n", encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_output.py"),
                    "--out-dir",
                    str(out_dir),
                    "--mode",
                    "stage0",
                    "--user-input",
                    "展开理论",
                    "--project-root",
                    str(ROOT),
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )


if __name__ == "__main__":
    unittest.main()
