# Research Project Builder Bilingual Skill and README Banner Design

## Objective

Make the existing brand image visible on the GitHub repository homepage and
provide a complete Simplified Chinese companion to the canonical English skill
without creating a second Codex runtime entry point.

## Chosen approach

Reuse the approved `assets/social-preview.png` in both existing README
languages and add `SKILL.zh-CN.md` as a human-readable mirror of `SKILL.md`.
The English `SKILL.md` remains the only canonical runtime file. The Chinese
companion carries no skill frontmatter, states that the English file governs
on disagreement, and preserves commands, paths, field names, authorization
phrases, and filenames exactly.

The alternatives were rejected because they do not solve the shown problem:

- configuring only GitHub's social preview would not display an image inside
  the README;
- generating a new banner would replace an already approved and packaged
  asset without adding value;
- creating a second frontmatter-bearing skill would risk duplicate discovery
  and contract drift.

## Repository and package changes

- Add links to the English and Chinese skill documents next to the existing
  README language links.
- Render `assets/social-preview.png` immediately after the badges so it is
  visible in the first GitHub screen in both languages.
- Translate the complete skill instructions into Simplified Chinese while
  leaving executable literals unchanged.
- Add `SKILL.zh-CN.md` to `SKILL_ROOT_FILES` so Git-index packaging projects it
  to `skills/research-project-builder/SKILL.zh-CN.md`.
- Keep `SKILL.md` as the only destination named `SKILL.md`.
- Bump project/plugin/release version from `0.2.0` to `0.2.1` and record the
  bilingual documentation/package change in the changelog.

## Verification

- A test must fail before implementation because the Chinese skill and banner
  links do not yet exist.
- The real package must contain byte-identical indexed `SKILL.zh-CN.md` and no
  unintended files.
- All local Markdown links in both the repository and packaged skill must
  resolve.
- The complete existing test suite, packaged Stage 0 run, deterministic build,
  and official skill/plugin validators must pass.
- A clean GitHub release must publish tag `v0.2.1` with the packaged plugin.

## Acceptance criteria

GitHub shows the banner on both README language pages; users can move between
English and Chinese README and skill documents; installed plugin users receive
the Chinese companion; Codex still discovers exactly one canonical skill; and
the release is validator-clean.
