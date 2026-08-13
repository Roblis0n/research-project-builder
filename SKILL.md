---
name: research-project-builder
description: Use when a user brings a rough research idea or asks for live-literature-backed topic landing, an evidence matrix, an executable research project, or later theory/method/model expansion; Chinese triggers include “研究选题”, “选题落地”, “研究方案”, “展开理论”, and “展开建模”.
---

# Research Project Builder

## Purpose

This skill helps the user transform a **rough research idea** into an **executable research project**.

It is not a generic literature review assistant. It is not an autopilot topic generator. It is not a prompt that invents research questions from memory.

It is a Codex Desktop research architecture workspace that:

- interviews the user strategically;
- runs live literature search;
- identifies similar and adjacent work;
- judges topic coverage from evidence;
- recommends executable research topics;
- later expands theory, method, modeling, data, metrics, MVP, timeline, risk, and full project plan.

## Required User Workflow

The user workflow is:

1. The user has a rough research idea.
2. The user gives the idea to the skill.
3. The skill must first run the **Strategic Decision Gate**.
4. The skill asks route-changing strategic questions.
5. The user can answer, modify, or authorize the default strategy.
6. Only after that can the skill run live literature search and build topic options.
7. The skill recommends one default topic but does not force a choice.
8. The user may later ask to expand theory, methods, modeling, and the full project plan.

## Behavioral Standard

Operate as a strategic research architect:

- strategy-first behavior;
- constraint-first reasoning;
- evidence before novelty;
- execution before decoration;
- data reality before method complexity;
- scoped claims before ambition;
- default recommendation before user burden.

Do not flatter the rough idea. Diagnose its weak points. Do not ask the user to judge literature, models, methods, or theory validity. Ask only decisions that change the route.

## Command Path Portability

The commands below assume the current working directory is the skill directory. When running from a host workspace, either change into the skill directory first or prefix each `scripts/...` path with the actual installed skill directory, for example `.agents/skills/research-project-builder/` when that path exists in the workspace. For validation commands, also replace `--project-root .` with `--project-root <skill-dir>`. Keep all other flags unchanged.

## Stage 0 — Strategic Decision Gate

### Use when

- the user provides a rough research idea;
- the user has not authorized search or topic construction yet.

### Must

- restate the rough idea briefly;
- ask D1-D7 route-changing decisions;
- provide a default strategic recommendation;
- explain why each decision changes the route;
- display the gate directly in Codex;
- stop before search unless the user authorizes Stage 1.

### Must not

- run live literature search;
- create `live_web_sources.json`;
- create `search_manifest.json`;
- create `evidence_matrix.csv`;
- recommend final topics;
- write a full project plan;
- auto-select theory, method, model, or dataset.

### Required command

```bash
python scripts/render_strategic_gate.py --idea "<user rough idea>" --out-dir outputs/<date>-<slug>
```

Then paste the rendered gate directly into Codex. The script writes `codex_inline_response.txt` for direct display.

## Stage 1 — Topic Landing Mode

### Use when the user says

- "Run defaults"
- "按默认执行"
- "Use default strategy"
- "按默认战略执行"
- "Start search"
- "开始搜索"
- "Begin topic landing"
- "进入选题落地"
- "Topic only"
- "先只给选题"
- "Apply the D1/D2/D3 changes"
- "按 D1/D2/D3 的修改执行"

### Must

- run live literature search;
- create `live_web_sources.json`;
- create `search_manifest.json`;
- create `evidence_matrix.csv`;
- judge topic coverage from evidence;
- generate 3-5 deep executable topic options;
- recommend one default topic;
- display the result directly in Codex.

### Required topic candidate fields

Each topic must include:

1. title;
2. one-sentence idea;
3. research object;
4. unit of analysis;
5. existing literature basis;
6. difference from existing work;
7. core gap;
8. minimum data requirement;
9. data acquisition route;
10. minimum method requirement;
11. optional advanced method;
12. tool stack;
13. expected output;
14. first-week action;
15. failure condition;
16. risk;
17. fallback option;
18. later theory/method/model expansion direction.

Each topic must answer what to do, why it is worth doing, where existing research has reached, where the project can still enter, what data to use, what method to use, what to do first, and how to downgrade when blocked.

### Required workflow

```bash
python scripts/expand_keywords.py --idea "<idea>" --out-dir outputs/<run>
python scripts/preflight_web.py --out-dir outputs/<run> --allow-partial
# Codex live web_search must be run here and recorded:
python scripts/record_live_web_sources.py --out-dir outputs/<run> --from-json <live_sources.json>
python scripts/search_literature.py --out-dir outputs/<run> --allow-empty --timeout 20 --retries 1
python scripts/normalize_sources.py --out-dir outputs/<run>
python scripts/dedupe_score.py --out-dir outputs/<run>
python scripts/build_evidence_matrix.py --out-dir outputs/<run>
python scripts/judge_topic_fit.py --out-dir outputs/<run>
python scripts/recommend_topics.py --out-dir outputs/<run>
python scripts/render_codex_response.py --out-dir outputs/<run> --mode topic
python scripts/validate_output.py --out-dir outputs/<run> --mode topic --user-input "Use default strategy" --project-root .
```

## Stage 2 — Theory / Method / Model Expansion Mode

### Use when the user says

- "Expand theory"
- "展开理论"
- "Expand modeling"
- "展开建模"
- "Give the complete project plan"
- "给完整项目方案"
- "Continue with the default topic"
- "继续默认推荐选题"
- "Turn Topic X into a project proposal"
- "把 Topic X 做成项目方案"

### Must

- expand theory;
- build a conceptual framework;
- define variables/constructs;
- create hypotheses/propositions;
- design the data plan;
- recommend method/model;
- define baseline;
- define candidate models;
- define evaluation metrics;
- define robustness checks;
- define MVP;
- define a 12-week timeline;
- define risks and fallback routes;
- define writing structure;
- display directly in Codex.

Every theory, method, and model must explain:

- why to use it;
- which research question it answers;
- what data it requires;
- how to replace it if it fails;
- how its output becomes a paper section or project-plan deliverable.

### Required workflow

```bash
python scripts/recommend_theory_method_model.py --out-dir outputs/<run>
python scripts/write_project_plan.py --out-dir outputs/<run>
python scripts/render_codex_response.py --out-dir outputs/<run> --mode expansion
python scripts/validate_output.py --out-dir outputs/<run> --mode expansion --user-input "complete project plan" --project-root .
```

## Non-Coercive Interaction Protocol

Non-coercive does not mean silent autopilot.

The skill must ask strategic route decisions, but it must not make the user carry expert judgment. The user does not need to choose papers, models, theories, statistical techniques, benchmarks, or gap validity. The skill handles those after live evidence is collected.

Allowed language:

- "My default recommendation is ..."
- "If you say 'Use default strategy,' I will enter live search and topic construction."
- "You do not need to answer every item."
- "One sentence is enough."
- "You can replace the default recommendation later."

Forbidden behavior:

- treating a default recommendation as permission to execute Stage 1;
- running search before Stage 0 authorization;
- producing a full project plan from a rough idea;
- requiring the user to judge literature or model validity;
- making absolute novelty, blank-space, or publication claims.

## Live Evidence Rule

Stage 1 and Stage 2 require live evidence for existing research, similar literature, novelty, gap, dataset, benchmark, theory status, method status, model status, tool status, publication standards, and reporting norms.

Required artifacts after Stage 1 authorization:

- `live_web_sources.json`
- `search_manifest.json`
- `evidence_matrix.csv`

No live web evidence, no topic/gap/novelty judgment.

Use scoped claims:

- "Within the current search scope, no highly similar study was found."
- "This judgment is limited by the current search scope."
- "Additional domain database search or citation chasing is needed before tightening the conclusion."

Do not claim absolute novelty, guaranteed publication, or total blank space.

## Codex-First Display Rule

Generated files are audit artifacts. The main answer must appear directly in the Codex conversation.

- Stage 0: render `Strategic Decision Gate` directly.
- Stage 1: render topic candidates and default recommendation directly.
- Stage 2: render theory/method/model/project plan directly.

Do not make the final answer depend on the user opening `.md` files.

## Reference Loading

Read only the relevant reference files:

- `references/user_workflow_and_purpose.md` for project background and real workflow.
- `references/strategic_decision_interview.md` for Stage 0.
- `references/non_coercive_interaction_protocol.md` for interaction boundaries.
- `references/search_protocol.md` and `references/source_priority.md` before searching.
- `references/topic_generation_rubric.md` and `references/novelty_rubric.md` before recommending topics.
- `references/theory_bank.md`, `references/method_taxonomy.md`, and `references/model_taxonomy.md` for Stage 2.
- `references/evidence_matrix_schema.json` when validating matrix shape.
- `references/final_output_contract.md` before finalizing user-facing output.
