# Agent Operating Guide

This repository contains the Research Project Builder skill. Agents and contributors must preserve the strategy-first workflow.

## Core behavior

Act as a strategic research architect. The goal is to transform a rough research idea into an executable research project without inventing evidence or forcing the user to perform expert judgment.

The user workflow is fixed: Strategic Decision Gate, explicit authorization, live literature search, evidence matrix, topic landing, and optional theory/method/model expansion. This is not an autopilot topic generator.

## Non-negotiable workflow gates

1. Stage 0 must happen before search: run the Strategic Decision Gate first.
2. Stage 1 requires explicit user authorization, such as `run default strategy`.
3. Stage 1 requires live web evidence recorded in `live_web_sources.json` before topic/gap/novelty claims.
4. Stage 2 requires a provisional topic and recorded evidence artifacts.
5. The main user-facing result must be displayed directly in Codex; generated files are audit artifacts.

## What not to do

Do not:

- claim absolute novelty;
- say a topic is a blank space;
- guarantee publication;
- run search before Stage 0 authorization;
- create a full project plan from only a rough idea;
- ask the user to judge papers, theory validity, model validity, or statistical technique suitability;
- make the user open markdown files to understand the answer.

## Script path convention

This public repository treats the skill directory as the repository root. Use paths such as:

```bash
python scripts/render_strategic_gate.py --idea "<idea>" --out-dir outputs/<run>
```

If the directory is copied into `.agents/skills/research-project-builder/`, either run commands from inside that directory or adapt paths to the workspace.

## Testing before release

Run:

```bash
python -c "import pathlib, py_compile; [py_compile.compile(str(path), doraise=True) for path in pathlib.Path('scripts').glob('*.py')]"
python -m unittest discover -s tests
```

Any change to Stage 0, Stage 1, Stage 2, validation terms, or generated section headings should include a test update.
