#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re

from _common import output_dir_from_args, read_text, today, write_text


def extract_topic(pack: str) -> str:
    patterns = [
        r"##\s*1\.\s*(?:Selected topic|Topic)\s*\n+(.+?)(?:\n##|\Z)",
        r"Recommended framework for topic:\s*(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, pack, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return " ".join(match.group(1).strip().split())
    return "Provisionally selected research topic"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write project_plan.md, risk_register.md, and decision_log.md.")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = output_dir_from_args(args.out_dir)
    pack = read_text(out_dir / "theory_method_model_pack.md")
    topic = extract_topic(pack)

    project_plan = f"""# Project Plan

## 1. Topic

{topic}

## 2. Research Objective

Turn the provisional topic into a feasible, evidence-backed study with transparent data, method, evaluation, and risk controls.

## 3. Execution Logic

This plan is written for execution, not brainstorming.

- What to do first: lock the research question, unit of analysis, and minimal data path.
- How to do it: work from the evidence matrix, build a data dictionary, run a baseline, then test robustness.
- What to use: Zotero/evidence matrix for literature; Python or R for data; spreadsheet/codebook for measurement; simple baseline before advanced models.
- What not to do: do not start with a complex model or decorative theory before the outcome and data are measurable.

## 4. Work Packages

### WP1: Evidence and scope lock
- Re-read the top evidence-matrix records.
- Add field-specific supplemental search if needed.
- Freeze the research question, unit of analysis, and inclusion/exclusion criteria.

### WP2: Data readiness
- Identify data sources.
- Create a data dictionary.
- Record missingness, access constraints, and proxy limitations.
- Decide whether the project is explanatory, predictive, qualitative, mixed-methods, or review/synthesis.

### WP3: Minimal analysis
- Build the descriptive baseline.
- Fit the simplest method that answers the question.
- Compare against at least one alternative operationalization or baseline.

### WP4: Robustness and interpretation
- Check subgroup, proxy, missingness, and specification sensitivity.
- Interpret against the evidence matrix.
- Avoid absolute novelty claims.

### WP5: Writing
- Introduction: problem, evidence gap, contribution.
- Literature: closest and adjacent work.
- Method: data, variables, model, robustness.
- Results: main findings, sensitivity checks, limitations.
- Discussion: contribution, boundaries, future work.

## 5. Timeline

| Week | Deliverable |
|---|---|
| 1 | Evidence matrix cleaned and topic scope locked |
| 2 | Data source confirmed and data dictionary drafted |
| 3 | Baseline analysis completed |
| 4 | Main model or synthesis completed |
| 5 | Robustness checks and error analysis completed |
| 6 | Draft manuscript/proposal completed |

## 6. Completion Criteria

- The search manifest and evidence matrix are traceable.
- The selected topic has a clear data source, method, and MVP.
- Claims about novelty are limited to the current search scope.
- The final output passes `validate_output.py`.
"""

    risk_register = """# Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Search misses field-specific literature | Medium | High | Add domain database search and citation chasing |
| Data unavailable or too broad | Medium | High | Use a public-data MVP, smaller sample, or proxy design |
| Topic is already highly covered | Medium | Medium | Shift to validation, mechanism, context, or data contribution |
| Measures are weak or noisy | Medium | High | Use validated scales, triangulation, or sensitivity checks |
| Model overclaims beyond data | Medium | High | Keep baseline transparent and report uncertainty |
| User constraints change | Low | Medium | Preserve decision log and make assumptions editable |
"""

    decision_log = f"""# Decision Log

| Date | Decision | Rationale | Reversible? |
|---|---|---|---|
| {today()} | Use the current topic as provisional | Allows progress without forcing the user to choose | Yes |
| {today()} | Require live search before novelty/gap claims | Prevents memory-based claims | No |
| {today()} | Start from an MVP | Controls data and method risk | Yes |
"""

    write_text(out_dir / "project_plan.md", project_plan)
    write_text(out_dir / "risk_register.md", risk_register)
    write_text(out_dir / "decision_log.md", decision_log)
    print("Wrote project_plan.md, risk_register.md, and decision_log.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
