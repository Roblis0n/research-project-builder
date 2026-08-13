# Research Project Builder GitHub Productization Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan.

**Goal:** Ship a canonical, bilingual, demonstrable, plugin-compatible Research
Project Builder and make the user's installed copy track it without drift.

**Architecture:** Preserve the gated offline-testable workflow, expose its
proof earlier, keep the repository as the source of truth, and install it by a
reversible directory junction after release.

**Tech stack:** Markdown, YAML, JSON, TOML, Python standard library/unittest,
GitHub Actions, Codex skill/plugin manifests, PNG/SVG assets, Windows junction.

### Task 1: Reconcile source and installed skill

**Files:**
- Compare: `C:\Users\Dr.J\.agents\skills\research-project-builder\SKILL.md`
- Modify if warranted: `SKILL.md`
- Modify if warranted: portability references and commands

1. Produce a semantic diff of the installed and repository skill.
2. Preserve only useful Chinese triggers and path-portability guidance that do
   not weaken the Strategic Gate or evidence requirements.
3. If `SKILL.md` changes, forward-test the affected trigger/path scenarios.
4. Run the skill validator before public documentation work.

### Task 2: Put proof and invocation first

**Files:**
- Modify: `README.md`
- Create: `README.zh-CN.md`
- Modify/create: files under `examples/`

1. Add CI/license/version badges and a compact input-to-output demonstration.
2. Add exact user-level and repository-level installation commands.
3. Put an exact `$research-project-builder` prompt before shell commands.
4. Surface the existing Stage 0 and fixture examples and verify every command.
5. Translate the complete entry path and safety/evidence limits into Chinese.

### Task 3: Upgrade CI and community health

**Files:**
- Modify: `.github/workflows/smoke-test.yml`
- Create: `.github/CODE_OF_CONDUCT.md`
- Create: `.github/SUPPORT.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/pull_request_template.md`

1. Run compilation, seven unit tests, and Stage 0 validation on Ubuntu and
   Windows with Python UTF-8 enabled.
2. Upgrade to `actions/checkout@v6` and `actions/setup-python@v6`.
3. Add project-specific conduct, support, issue, and PR guidance while keeping
   the existing contribution and security files.

### Task 4: Package and brand the skill

**Files:**
- Modify: `agents/openai.yaml`
- Create: `.codex-plugin/plugin.json`
- Create: `assets/icon-small.png`
- Create: `assets/icon-large.png`
- Create: `assets/social-preview.png`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`

1. Generate and inspect the idea-gate-evidence-route visual family.
2. Reduce UI metadata to supported fields, preserve explicit invocation, and
   add brand assets.
3. Set project/plugin version `0.2.0` and document the full release.
4. Validate skill and plugin structures.

### Task 5: Verify, publish, and install canonically

1. Run compile, unit, Stage 0, example, link, skill, and plugin checks.
2. Commit, push, open a PR, wait for both OS jobs, and merge.
3. Set description, Topics, Discussions, custom social preview, tag, and
   release `v0.2.0`.
4. Clone/pull the merged main branch into the permanent F: skill path.
5. Verify the exact C: source and backup targets, move the old install to a
   dated backup, create a junction to the canonical checkout, and rerun tests
   through the installed path.
