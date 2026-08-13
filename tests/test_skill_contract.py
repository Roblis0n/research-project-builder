from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    def test_reconciliation_keeps_gate_and_evidence_contracts(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
