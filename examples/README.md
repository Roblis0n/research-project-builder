# Reproducible examples

These examples show the gated path without presenting fixture data as current literature evidence.

| Stage | Start here | What it proves |
| --- | --- | --- |
| Stage 0 | [`stage0_input.md`](stage0_input.md) | A rough idea renders a seven-decision Strategic Gate before any search artifact exists. |
| Stage 1 source shape | [`live_web_sources.sample.json`](live_web_sources.sample.json) | The required fields for recording sources actually retrieved by Codex live web search. |
| Stage 1 output shape | [`stage1_mock_output.md`](stage1_mock_output.md) | The required topic-landing sections; it is not a current literature claim. |
| Stage 1 offline proof | [`../tests/fixtures/topic_output/`](../tests/fixtures/topic_output/) | A deterministic direct response, source log, evidence matrix, and recommendation accepted by the validator. |
| Stage 2 output shape | [`stage2_mock_output.md`](stage2_mock_output.md) | The required expansion sections after a topic has been provisionally selected. |

## Verify Stage 0

Run from the repository root:

```bash
python scripts/render_strategic_gate.py --idea "generative AI and graduate student research productivity" --out-dir outputs/stage0-demo
python scripts/validate_output.py --out-dir outputs/stage0-demo --mode stage0 --user-input "rough idea only" --project-root .
```

Expected result: validation succeeds, `outputs/stage0-demo/codex_inline_response.txt` contains D1-D7, and no search manifest, live-source log, or evidence matrix is created.

## Verify the Stage 1 fixture

```bash
python scripts/record_live_web_sources.py --out-dir tests/fixtures/topic_output --validate-only
python scripts/validate_output.py --out-dir tests/fixtures/topic_output --mode topic --user-input "Use default strategy" --project-root .
```

Expected result: both validators succeed without network access. This proves the artifact and authorization contract only. Replace the sample source with sources retrieved during a real live search before making any current topic, gap, or novelty judgment.
