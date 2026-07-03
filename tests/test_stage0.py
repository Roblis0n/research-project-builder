from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Stage0Tests(unittest.TestCase):
    def test_stage0_renders_and_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "stage0"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "render_strategic_gate.py"),
                    "--idea",
                    "generative AI and graduate student research productivity",
                    "--out-dir",
                    str(out_dir),
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                timeout=30,
            )
            text = (out_dir / "codex_inline_response.txt").read_text(encoding="utf-8")
            self.assertIn("Strategic Decision Gate", text)
            self.assertIn("Why this changes the route", text)
            self.assertFalse((out_dir / "search_manifest.json").exists())
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_output.py"),
                    "--out-dir",
                    str(out_dir),
                    "--mode",
                    "stage0",
                    "--user-input",
                    "rough idea only",
                    "--project-root",
                    str(ROOT),
                ],
                check=True,
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                timeout=30,
            )


if __name__ == "__main__":
    unittest.main()
