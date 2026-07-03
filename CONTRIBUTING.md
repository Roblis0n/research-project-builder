# Contributing

Contributions are welcome if they preserve the skill's workflow gates and evidence discipline.

## Required principles

Changes must preserve:

- Stage 0 before search;
- explicit authorization before Stage 1;
- live evidence before novelty, gap, dataset, benchmark, method, or model-status claims;
- direct Codex display of the main result;
- no absolute novelty claims;
- no forced user choice;
- validation before release.

## Development checks

Run before opening a pull request:

```bash
python -m py_compile scripts/*.py
python -m unittest discover -s tests
```

## Style

Keep generated user-facing content direct, operational, and evidence-scoped. Avoid motivational filler and avoid method/theory dumping that does not change the research design.
