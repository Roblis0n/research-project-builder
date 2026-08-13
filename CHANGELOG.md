# Changelog

## 0.2.1 - 2026-08-13

- Added a complete Simplified Chinese `SKILL.zh-CN.md` companion while keeping
  `SKILL.md` as the only Codex runtime entry point.
- Displayed the existing approved social-preview banner directly in both
  README languages and added direct README/skill language navigation.
- Included exact indexed Chinese-skill bytes in deterministic plugin builds
  and extended package/link contracts to cover the bilingual release.

## 0.2.0 - 2026-08-13

- Added complete English and Simplified Chinese onboarding, exact installation commands, explicit invocation examples, and offline proof artifacts.
- Preserved the strategy-first gate while adding Chinese workflow authorizations and portable installed-skill command guidance.
- Expanded CI to Python 3.12 on Ubuntu and Windows and added project-specific community health templates.
- Added Codex plugin packaging, supported skill UI metadata, explicit-invocation policy, and the idea-gate-evidence-route brand family.
- Added a release packager that projects only explicit, Git-tracked runtime files into the standard `skills/research-project-builder/` plugin layout without duplicating the source tree.
- Hardened plugin releases against untracked-file leakage, symbolic links, path escape, recursive in-repository output, stale targets, partial builds, and nondeterministic file metadata.
- Added packaged Stage 0 execution and official validator coverage, including the required `README.md` and `AGENTS.md` runtime context.
- Changed release builds to read exact Git index blobs, preserving executable modes while excluding unstaged working-tree drafts.
- Closed the packaged documentation and proof chain by shipping the bilingual README, changelog, contribution and license files, examples, and Stage 0 fixtures referenced by the runtime documentation.
- Added behavioral coverage for index/worktree divergence, all packaged Markdown links, and cleanup after an injected post-staging write failure.

## 0.1.0

- Initial public repository packaging.
- Added README, AGENTS guide, license, security policy, contributing guide, examples, tests, and CI workflow.
- Standardized standalone repository script paths to `scripts/...`.
- Added validation support for standalone repository layout.
- Added timeout/retry/failure controls for structured literature search.
- Improved topic extraction from the Stage 2 expansion pack.
- Improved route inference so evidence-map topics are not misclassified as mechanism studies.
- Added lightweight CJK n-gram support for similarity scoring without mandatory third-party dependencies.
