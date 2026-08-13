# Research Project Builder

[![CI](https://github.com/Roblis0n/research-project-builder/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/Roblis0n/research-project-builder/actions/workflows/smoke-test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version: 0.2.1](https://img.shields.io/badge/version-0.2.1-blue.svg)](CHANGELOG.md)

[English](README.md) · [简体中文](README.zh-CN.md) · [English Skill](SKILL.md) · [中文 Skill](SKILL.zh-CN.md)

![Research Project Builder：从粗略想法到可执行研究](assets/social-preview.png)

Turn a rough research idea into an executable, evidence-backed project without pretending that a remembered gap is a real gap.

```text
ROUGH IDEA                    STRATEGIC GATE              LIVE EVIDENCE                  EXECUTABLE TOPIC
"Generative AI and      ->    D1-D7 route decisions  ->  web sources + evidence    ->   3-5 scoped options,
graduate productivity"        explicit authorization     matrix                           one default route
```

The user workflow is deliberately gated: the Strategic Decision Gate comes first, and live literature search starts only after you authorize a route. Topic, gap, and novelty judgments require recorded live web evidence. Theory, method, and model expansion comes only after a provisional topic exists.

## Install

Requires Git, Python 3.10+, and Codex Desktop, Codex CLI, or the Codex IDE extension. Choose one scope; do not install both copies with the same skill name.

### User-level: available in every repository

macOS/Linux:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Roblis0n/research-project-builder.git "$HOME/.agents/skills/research-project-builder"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
git clone https://github.com/Roblis0n/research-project-builder.git "$HOME\.agents\skills\research-project-builder"
```

### Repository-level: available only in one repository

Run from that repository root.

macOS/Linux:

```bash
mkdir -p .agents/skills
git clone https://github.com/Roblis0n/research-project-builder.git .agents/skills/research-project-builder
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force ".agents\skills" | Out-Null
git clone https://github.com/Roblis0n/research-project-builder.git ".agents\skills\research-project-builder"
```

Codex detects skill changes automatically; restart it if the skill does not appear. These locations follow the [official Codex skill-loading scopes](https://developers.openai.com/codex/skills#where-codex-loads-local-skills).

### Build the standalone Codex plugin

The repository root is the canonical directly installable **skill**, not an
installable plugin directory. Its `.codex-plugin/plugin.json` is build input;
the standard `skills/research-project-builder/` plugin layout exists only in a
fresh release artifact.

Build that artifact into a new sibling directory outside this repository:

```text
python scripts/build_plugin_package.py --output ../research-project-builder-release/research-project-builder
```

Use the resulting `../research-project-builder-release/research-project-builder/`
directory for plugin validation, archiving, or installation. The builder
refuses repository-internal outputs and existing targets, builds through a
same-filesystem temporary sibling, and publishes by atomic rename. Start every
release from a new target; do not reuse `dist/` or any stale package directory.
Package bytes come from Git index blobs, never from unstaged working-tree
drafts. Stage every intended release change before running the builder.
The package includes the canonical `SKILL.md` runtime entry and the
human-readable `SKILL.zh-CN.md` companion.

## Invoke it explicitly

Implicit invocation is disabled by design. Start a Codex task with this exact prompt:

```text
$research-project-builder Turn this rough idea into an executable research project: generative AI and graduate student research productivity. Begin with the Strategic Decision Gate. Do not search until I explicitly authorize the default or a modified strategy.
```

The skill first displays the seven-decision gate in Codex and stops. To authorize Stage 1, reply with an explicit instruction such as:

```text
Use default strategy.
```

That reply authorizes live search and topic landing. It does not authorize Stage 2. Generated files are audit artifacts; the main result must remain visible directly in Codex.

## What you get

- **Stage 0 — Strategic Decision Gate:** target output, non-negotiable core, data reality, method ceiling, innovation/feasibility balance, time window, and current stage.
- **Stage 1 — Evidence-backed topic landing:** recorded live sources, structured-source manifest, evidence matrix, closest and adjacent work, 3-5 executable topics, and one non-coercive default recommendation.
- **Stage 2 — Optional expansion:** theory, constructs, hypotheses/propositions, data plan, baseline, candidate models, metrics, robustness checks, MVP, 12-week plan, risks, fallbacks, and writing structure.

Research Project Builder is a strategic research architect, not an autopilot topic generator. It asks only route-changing user decisions; it does not make the user judge papers, theories, models, or statistical techniques.

## Reproducible examples

The [examples guide](examples/README.md) connects each stage to a committed example or offline fixture:

- [rough Stage 0 input](examples/stage0_input.md);
- [sample live-web source record](examples/live_web_sources.sample.json);
- [Stage 1 output shape](examples/stage1_mock_output.md);
- [Stage 2 output shape](examples/stage2_mock_output.md);
- [offline Stage 1 fixture](tests/fixtures/topic_output/) with a direct response, source log, evidence matrix, and topic recommendation.

### Render and validate Stage 0

Run from this repository root:

```bash
python scripts/render_strategic_gate.py --idea "generative AI and graduate student research productivity" --out-dir outputs/stage0-demo
python scripts/validate_output.py --out-dir outputs/stage0-demo --mode stage0 --user-input "rough idea only" --project-root .
```

Open `outputs/stage0-demo/codex_inline_response.txt` to inspect the rendered artifact. In an actual Codex task, display that content directly and stop before search. A valid Stage 0 run does not create `live_web_sources.json`, `search_manifest.json`, or `evidence_matrix.csv`.

### Validate the offline Stage 1 fixture

This checks the evidence and authorization contract without claiming that fixture records are a current literature search:

```bash
python scripts/record_live_web_sources.py --out-dir tests/fixtures/topic_output --validate-only
python scripts/validate_output.py --out-dir tests/fixtures/topic_output --mode topic --user-input "Use default strategy" --project-root .
```

The fixture is deterministic and network-free. It proves the artifact contract, not current novelty or gap status.

## Workflow and command reference

Commands below assume the current directory is the installed skill directory. From a host workspace, prefix `scripts/` with the installed path, such as `.agents/skills/research-project-builder/scripts/`, and set `--project-root` to that skill directory.

### Stage 0: gate before search

Use the verified Stage 0 commands above. Then paste `codex_inline_response.txt` directly into Codex. Do not search or construct topics until the user explicitly authorizes Stage 1.

### Stage 1: live evidence before topic claims

After explicit authorization, Codex performs the following ordered workflow:

1. Expand the rough idea into auditable search terms with `expand_keywords.py`.
2. Run the web preflight with `preflight_web.py`.
3. Perform a real, current Codex web search.
4. Record those results with `record_live_web_sources.py` before making topic, gap, or novelty claims.
5. Search structured scholarly APIs with `search_literature.py`; this supplements rather than replaces live web search.
6. Normalize, deduplicate, score, and build `evidence_matrix.csv`.
7. Judge topic fit, generate 3-5 candidates, render the direct Codex response, and validate the output.

Required Stage 1 artifacts are `live_web_sources.json`, `search_manifest.json`, and `evidence_matrix.csv`. The exact source-record shape is in [examples/live_web_sources.sample.json](examples/live_web_sources.sample.json). Replace its demonstration URL and metadata with sources actually retrieved for the run.

### Stage 2: expand only after topic landing

Stage 2 requires a provisional topic and recorded Stage 1 evidence. An explicit request such as `Expand the default topic into a complete project plan` authorizes theory/method/model expansion. The workflow then uses `recommend_theory_method_model.py`, `write_project_plan.py`, `render_codex_response.py --mode expansion`, and `validate_output.py --mode expansion` against the same run directory.

## Evidence and safety boundaries

- Stage 0 always precedes search.
- A default recommendation is not authorization; Stage 1 requires an explicit user reply.
- No `live_web_sources.json`, no final topic, gap, novelty, dataset, benchmark, theory-status, method-status, model-status, or reporting-norm claim.
- Structured API metadata does not replace Codex live web search or full-text reading.
- All novelty and gap language is scoped to the recorded search. Never claim an absolute blank space.
- The skill does not guarantee publication.
- The skill does not write a full project plan from only a rough idea.
- The user-facing result is shown directly in Codex; files preserve the audit trail.

A defensible claim sounds like: “Within the current search scope, no highly similar study was found; additional domain-database search or citation chasing is needed before tightening the conclusion.”

## User-Agent configuration

Structured scholarly APIs work best with an identifiable user agent. Configure one before a live run when possible:

macOS/Linux:

```bash
export RPB_USER_AGENT="research-project-builder/0.2.1 (mailto:you@example.com)"
```

Windows PowerShell:

```powershell
$env:RPB_USER_AGENT = "research-project-builder/0.2.1 (mailto:you@example.com)"
```

If unset, the scripts use their built-in fallback user agent.

## Development checks

```bash
python -c "import pathlib, py_compile; [py_compile.compile(str(path), doraise=True) for path in pathlib.Path('scripts').glob('*.py')]"
python -m unittest discover -s tests
```

Tests are offline. Stage 1 evidence behavior is exercised with committed fixtures rather than network calls.

## Repository layout

```text
research-project-builder/
  SKILL.md                         # workflow instructions and gates
  AGENTS.md                        # contributor operating rules
  agents/openai.yaml               # Codex UI and invocation policy
  assets/templates/                # audit-artifact templates
  references/                      # workflow and quality-control references
  scripts/                         # executable helper scripts
  examples/                        # guided demonstrations
  tests/fixtures/topic_output/     # deterministic Stage 1 fixture
  tests/                           # offline unit and contract tests
  .github/workflows/smoke-test.yml # CI
```

## Limitations

- API metadata can omit methods, samples, theory, and limitations.
- Live search quality depends on query breadth, source selection, access, and retrieval date.
- Structured APIs do not replace full-text review for a final literature synthesis.
- Evidence-backed topic options can still fail because of unavailable data, ethics constraints, weak measures, or an unrealistic time window.
- Generated plans are execution scaffolds, not publication guarantees.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) for the strategy-first contribution contract and [LICENSE](LICENSE) for the MIT License.
