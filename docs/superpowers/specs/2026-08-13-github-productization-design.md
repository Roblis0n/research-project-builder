# Research Project Builder GitHub Productization Design

## Objective

Make Research Project Builder the canonical, bilingual, executable source for
turning a rough research idea into a gated, evidence-backed project, while
eliminating drift between the GitHub repository and the user's installed copy.

## Approved scope

- Put a verified idea-to-gate-to-evidence-to-topic demonstration in the first
  README screen and surface the existing fixtures.
- Make the required explicit `$research-project-builder` invocation impossible
  to miss.
- Add a Chinese README entry while keeping the English README canonical and
  complete.
- Upgrade CI, add Windows coverage, and complete community-health templates.
- Align supported `agents/openai.yaml` fields, add icons, plugin packaging, and
  social preview.
- Incorporate useful portability and Chinese-trigger differences from the
  installed copy before replacing that copy with a reversible link to a
  canonical checkout.
- Publish version `0.2.0` with accurate GitHub metadata, Topics, Discussions,
  tag, and release.

## User journey

A visitor should see:

1. rough idea input;
2. the seven-decision Strategic Gate;
3. the authorization phrase;
4. recorded live evidence and evidence matrix;
5. three-to-five executable topics and one default recommendation;
6. optional theory/method/model expansion only after topic landing.

Installation and the exact `$research-project-builder` prompt appear before
the full command reference.

## Architecture decisions

- The GitHub repository is the only editable source of truth.
- The permanent local checkout will live under
  `F:\Skill\Codex\.agents\skills\research-project-builder`.
- The former `C:\Users\Dr.J\.agents\skills\research-project-builder` directory
  will be moved to a dated backup, then replaced by a directory junction to the
  canonical checkout. This is reversible.
- Keep explicit invocation disabled; documentation and UI prompts must reflect
  that policy.
- Keep the repository root as the canonical skill/plugin root.
- CI remains offline and deterministic; live-search behavior is exercised with
  fixtures, not network calls.

## Visual direction

Use an off-black canvas with a luminous research route: rough idea, gate,
evidence, and executable project. Electric blue indicates evidence, amber the
decision gate, and green the selected route. Avoid academic stock photography,
fake paper titles, dense diagrams, or decorative charts.

## Acceptance criteria

- Python compilation, all unit tests, and Stage 0 render/validation pass on
  Ubuntu and Windows.
- English and Chinese README entries include exact install and invocation,
  verified output, example links, live-evidence limitations, and stage gates.
- `agents/openai.yaml` contains only supported interface/policy fields and the
  explicit-invocation policy remains false.
- Skill and plugin validators pass.
- The installed path resolves to the canonical checkout and the original local
  directory remains recoverable as a dated backup.
- GitHub metadata, Topics, Discussions, social preview, tag, and release are
  visible and accurate.

## Baseline evidence

On 2026-08-13, seven unit tests and the Stage 0 render/validation flow passed.
The GitHub source contained 72 files while the installed copy contained 41;
31 public maintenance/test/example files were absent from the installed copy,
and `SKILL.md` had drifted.
