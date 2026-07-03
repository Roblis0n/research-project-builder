# Research Project Builder

Research Project Builder is a Codex Desktop skill for turning a **rough research idea** into an **executable research project**.

It is **not an autopilot topic generator** and not a generic literature-review prompt. It forces a strategy-first workflow: Strategic Decision Gate first, live literature search second, evidence matrix third, topic landing fourth, and theory/method/model expansion only after the project route is evidence-backed.

The user workflow is deliberately narrow: the skill receives a rough research idea, acts as a strategic research architect, and turns the idea into an executable research project only after route decisions and live evidence are recorded.

## What it does

The skill helps a user move from an early, imprecise research idea to a scoped project with:

- route-changing strategic decisions;
- live web and scholarly source records;
- structured evidence matrix;
- closest/adjacent literature buckets;
- executable topic candidates;
- one default recommendation;
- theory/method/model expansion;
- baseline, candidate models, metrics, robustness checks, MVP, risks, and writing structure.

## What it does not do

It does not:

- invent novelty or literature gaps from memory;
- claim that nobody has studied a topic;
- guarantee publication;
- force the user to choose papers, theories, models, or methods;
- write a full project plan before the Strategic Decision Gate and live evidence collection.

## Repository layout

```text
research-project-builder/
  SKILL.md                         # skill instructions
  AGENTS.md                        # contributor/agent operating rules
  assets/templates/                # artifact templates
  references/                      # workflow and quality-control references
  scripts/                         # executable helper scripts
  examples/                        # sample artifacts and demo inputs
  tests/                           # offline smoke tests
  .github/workflows/smoke-test.yml # CI smoke test
```

## Installation

This repository is the skill source directory.

For normal repository development, run commands from this repository root:

```bash
python scripts/render_strategic_gate.py --idea "generative AI and graduate student research productivity" --out-dir outputs/stage0-demo
```

For a Codex workspace that expects skills under `.agents/skills/`, copy or symlink this directory to:

```text
.agents/skills/research-project-builder/
```

When installed that way, either run scripts from inside the skill directory or adapt the command path to your workspace layout.

## Workflow

### Stage 0: Strategic Decision Gate

Use when the user provides a rough research idea and has not authorized search.

```bash
python scripts/render_strategic_gate.py \
  --idea "generative AI and graduate student research productivity" \
  --out-dir outputs/stage0-demo

python scripts/validate_output.py \
  --out-dir outputs/stage0-demo \
  --mode stage0 \
  --user-input "rough idea only" \
  --project-root .
```

The output is written to `codex_inline_response.txt` and should be displayed directly to the user.

### Stage 1: Topic landing

Use only after the user authorizes the default route, for example with `run default strategy`.

```bash
python scripts/expand_keywords.py --idea "<idea>" --out-dir outputs/<run>
python scripts/preflight_web.py --out-dir outputs/<run> --allow-partial
# The Codex agent must run live web search and record it before final claims:
python scripts/record_live_web_sources.py --out-dir outputs/<run> --from-json <live_sources.json>
python scripts/search_literature.py --out-dir outputs/<run> --allow-empty --timeout 30 --retries 1
python scripts/normalize_sources.py --out-dir outputs/<run>
python scripts/dedupe_score.py --out-dir outputs/<run>
python scripts/build_evidence_matrix.py --out-dir outputs/<run>
python scripts/judge_topic_fit.py --out-dir outputs/<run>
python scripts/recommend_topics.py --out-dir outputs/<run>
python scripts/render_codex_response.py --out-dir outputs/<run> --mode topic
python scripts/validate_output.py --out-dir outputs/<run> --mode topic --user-input "run default strategy" --project-root .
```

### Stage 2: Theory / method / model expansion

Use after a topic has been provisionally selected.

```bash
python scripts/recommend_theory_method_model.py --out-dir outputs/<run>
python scripts/write_project_plan.py --out-dir outputs/<run>
python scripts/render_codex_response.py --out-dir outputs/<run> --mode expansion
python scripts/validate_output.py --out-dir outputs/<run> --mode expansion --user-input "build the full project plan" --project-root .
```

## Live evidence requirement

`search_literature.py` searches structured scholarly APIs. It does **not** replace Codex live web search.

Before making current-state claims about similar work, novelty, gaps, datasets, benchmarks, tools, methods, or reporting norms, the agent must run live web search and record sources in `live_web_sources.json` using:

```bash
python scripts/record_live_web_sources.py --out-dir outputs/<run> --from-json <live_sources.json>
```

No `live_web_sources.json`, no final topic/gap/novelty judgment.

## User-Agent configuration

Structured scholarly APIs work best with an identifiable user agent. Set one when possible:

```bash
export RPB_USER_AGENT="research-project-builder/0.1 (mailto:you@example.com)"
```

If not set, the scripts use `research-project-builder/0.1`.

## Validation

Run offline checks:

```bash
python -m py_compile scripts/*.py
python -m unittest discover -s tests
```

The tests avoid network calls. Stage 1 live evidence is tested with fixtures.

## Limitations

- API metadata can omit methods, samples, theory, and limitations.
- Live web search quality depends on query breadth and source selection.
- Novelty and gap statements must be scoped to the recorded search.
- Structured APIs do not replace full-text reading for the final literature review.
- Generated plans are execution scaffolds, not publication guarantees.

## License

MIT License. See [LICENSE](LICENSE).
