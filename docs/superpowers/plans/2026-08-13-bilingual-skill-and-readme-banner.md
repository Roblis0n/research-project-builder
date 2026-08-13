# Research Project Builder Bilingual Skill and README Banner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show the existing Research Project Builder banner in both GitHub README languages and ship a complete Simplified Chinese skill companion in release `v0.2.1`.

**Architecture:** Keep root `SKILL.md` as the sole Codex runtime entry. Add frontmatter-free Chinese human documentation, package it through the existing Git-index root-file allowlist, and verify image/link/package behavior without changing the three-stage research workflow.

**Tech stack:** Markdown, TOML, JSON, Python standard library/unittest, deterministic Git-index plugin builder, GitHub Actions and Releases.

## Global constraints

- Preserve every command, path, filename, authorization phrase, artifact name, and stage boundary verbatim in the Chinese skill.
- Do not add YAML frontmatter to `SKILL.zh-CN.md`.
- Reuse `assets/social-preview.png`; do not regenerate brand assets.
- Release version is exactly `0.2.1` / tag `v0.2.1`.
- Run all work in `F:\Skill\Codex\.worktrees\research-bilingual-docs`.

---

### Task 1: Add failing bilingual package and README contracts

**Files:**
- Modify: `tests/test_plugin_package.py`
- Modify: `tests/test_skill_contract.py`

**Interfaces:**
- Consumes: the current builder, repository READMEs, manifests, and packaged Stage 0 flow.
- Produces: regression coverage for a visible local banner, a complete package projection, resolved local links, and version `0.2.1`.

- [ ] Add `SKILL.zh-CN.md` to the synthetic Git-index fixture and require it in the packaged root-byte comparison.
- [ ] Extend the real-package link test to require the Chinese skill.
- [ ] Add a repository entrypoint test that parses both README image targets and requires the existing local banner plus README/skill cross-links.
- [ ] Update version/changelog assertions to `0.2.1` while retaining the `0.2.0` history assertion.
- [ ] Run `python -X utf8 -B -m unittest tests.test_plugin_package tests.test_skill_contract -v` and confirm failures are caused only by the missing banner/Chinese skill/package/version.

### Task 2: Add the Chinese skill and release projection

**Files:**
- Create: `SKILL.zh-CN.md`
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `scripts/build_plugin_package.py`
- Modify: `.codex-plugin/plugin.json`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: canonical `SKILL.md`, existing bilingual READMEs, brand asset, and `SKILL_ROOT_FILES` packaging contract.
- Produces: two banner-bearing README pages, a complete Chinese skill companion, and packaged `skills/research-project-builder/SKILL.zh-CN.md`.

- [ ] Add README/skill language links and the local banner immediately after badges in both README files.
- [ ] Translate the complete skill body into Simplified Chinese, prepend the canonical-English notice, and omit frontmatter.
- [ ] Add `SKILL.zh-CN.md` to `SKILL_ROOT_FILES` so the builder copies exact Git-index bytes.
- [ ] Set project/plugin version `0.2.1` and add the dated changelog entry.
- [ ] Stage all intended files because the builder reads Git-index blobs.
- [ ] Run the focused tests again and confirm they pass.

### Task 3: Verify, publish, and release

**Files:**
- Verify: all tracked repository files and built artifacts.

**Interfaces:**
- Consumes: the staged/committed bilingual release candidate.
- Produces: merged `main`, tag `v0.2.1`, and packaged release artifact.

- [ ] Compile all scripts and run `python -X utf8 -B -m unittest discover -s tests -v`.
- [ ] Build two fresh plugin directories, compare file bytes/modes/mtimes, and run packaged Stage 0 plus official skill/plugin validators.
- [ ] Check UTF-8, all Markdown links, banner dimensions, `git diff --check`, and clean status.
- [ ] Commit, push, open a PR, wait for both GitHub Actions jobs, merge into `main`, and verify the remote tree.
- [ ] Build a clean post-merge package, archive it deterministically, create tag/release `v0.2.1`, upload the artifact, and verify README/release URLs over HTTPS.
