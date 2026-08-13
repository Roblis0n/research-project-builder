# Changelog

## 0.2.0 - Unreleased

- Added complete English and Simplified Chinese onboarding, exact installation commands, explicit invocation examples, and offline proof artifacts.
- Preserved the strategy-first gate while adding Chinese workflow authorizations and portable installed-skill command guidance.
- Expanded CI to Python 3.12 on Ubuntu and Windows and added project-specific community health templates.
- Added Codex plugin packaging, supported skill UI metadata, explicit-invocation policy, and the idea-gate-evidence-route brand family.
- Added a release packager that projects only explicit, Git-tracked runtime files into the standard `skills/research-project-builder/` plugin layout without duplicating the source tree.
- Hardened plugin releases against untracked-file leakage, symbolic links, path escape, recursive in-repository output, stale targets, partial builds, and nondeterministic file metadata.
- Added packaged Stage 0 execution and official validator coverage, including the required `README.md` and `AGENTS.md` runtime context.

## 0.1.0

- Initial public repository packaging.
- Added README, AGENTS guide, license, security policy, contributing guide, examples, tests, and CI workflow.
- Standardized standalone repository script paths to `scripts/...`.
- Added validation support for standalone repository layout.
- Added timeout/retry/failure controls for structured literature search.
- Improved topic extraction from the Stage 2 expansion pack.
- Improved route inference so evidence-map topics are not misclassified as mechanism studies.
- Added lightweight CJK n-gram support for similarity scoring without mandatory third-party dependencies.
