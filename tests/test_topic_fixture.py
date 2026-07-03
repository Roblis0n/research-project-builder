from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPIC_FIXTURE = ROOT / "tests" / "fixtures" / "topic_output"


class TopicFixtureTests(unittest.TestCase):
    def test_network_free_topic_fixture_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "topic"
            shutil.copytree(TOPIC_FIXTURE, out_dir)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_output.py"),
                    "--out-dir",
                    str(out_dir),
                    "--mode",
                    "topic",
                    "--user-input",
                    "Use default strategy",
                    "--project-root",
                    str(ROOT),
                ],
                check=True,
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=30,
            )

    def test_topic_fixture_contains_direct_response(self) -> None:
        text = (TOPIC_FIXTURE / "codex_inline_response.txt").read_text(encoding="utf-8")
        self.assertIn("Codex Direct Research Output", text)
        self.assertIn("My default recommendation is", text)
        self.assertIn("not a demand that the user choose now", text)


if __name__ == "__main__":
    unittest.main()
