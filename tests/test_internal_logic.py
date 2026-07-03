from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from record_live_web_sources import validate_sources  # noqa: E402
from recommend_theory_method_model import infer_route  # noqa: E402
from write_project_plan import extract_topic  # noqa: E402


class InternalLogicTests(unittest.TestCase):
    def test_extract_topic_accepts_selected_topic_heading(self) -> None:
        pack = """# Theory / Method / Model Pack

## 1. Selected Topic

Evidence-map and gap-driven topic refinement for generative AI.

## 2. Theory Candidate Table
"""
        self.assertEqual(extract_topic(pack), "Evidence-map and gap-driven topic refinement for generative AI.")

    def test_evidence_map_route_takes_priority(self) -> None:
        route = infer_route("Evidence-map and gap-driven topic refinement for generative AI impacts")
        self.assertEqual(route["route_name"], "Evidence synthesis route")

    def test_generic_impact_does_not_force_mechanism_route(self) -> None:
        route = infer_route("Impact of generative AI on graduate student learning efficiency")
        self.assertNotEqual(route["route_name"], "Mechanism explanation route")

    def test_live_source_shape_validates(self) -> None:
        source = {
            "query": "example query",
            "title": "Example source",
            "url": "https://example.org/source",
            "source_type": "live-web",
            "why_it_matters": "It demonstrates source logging shape.",
            "retrieved_at": "2026-07-03T00:00:00+00:00",
        }
        self.assertEqual(validate_sources([source]), [])


if __name__ == "__main__":
    unittest.main()
