# Agent and Contributor Orientation

Entry point for humans and AI assistants working in this repository.

## Read first

- [`README.md`](README.md) — product, quick start, current measured numbers.
- [`CONTEXT.md`](CONTEXT.md) — current state and last execution wave.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — language policy, tests, CI.

## What this repository is

A local-first cognitive kernel with a deterministic ethics evaluator and a
Flutter Desktop MVP connected to a Python/FastAPI backend. The active product
surface is `Flutter Desktop` + `Python kernel`. Mobile Android is in
freeze-lane (security/health maintenance only).

## What this repository is not

- It is not a multi-agent orchestration framework. The earlier multi-agent
  vocabulary is **abandoned** and was removed in the V2.147 cleanup. If you
  find references to it in old commits, ignore them.
- It is not a "nomadic P2P" product. The `ARCHITECTURE_NOMAD_V3` and
  `VISION_NOMAD` documents were aspirational, never implemented, and removed.

## Engineering rules that actually matter

These are kept because they map to concrete code quality, not vocabulary:

1. **Read the file before editing it.** Don't assume the rest is fine.
2. **Reproduce bugs with a test before fixing them.** For features, define
   "works" as a passing test before implementing.
3. **Anti-NaN.** Math and latency code must use `math.isfinite()` checks.
   `NaN`/`Inf` is never a valid score, weight, or duration.
4. **No empty `try/except`.** If you catch, handle or re-raise. No silent
   swallowing.
5. **Delete dead code in the same change.** Don't comment out, don't archive.
   Git preserves history.
6. **One concept = one file.** Don't keep "v1" and "v2" of the same module
   coexisting.
7. **Don't introduce a new top-level doc** unless it replaces an existing one
   or is explicitly requested. Add to the relevant existing file instead.

## How to validate changes

The full local quality battery (same as CI):

```bash
python scripts/eval/verify_collaboration_invariants.py
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python -m pytest tests/ -q --tb=short
```

Ethics evaluator regression:

```bash
python scripts/eval/run_ethics_benchmark.py --suite v1
```

The benchmark compares against `evals/ethics/BASELINE_v1.json`. Document any
delta in `docs/proposals/ETHICAL_BENCHMARK_BASELINE.md`. Do not overwrite the
baseline.

## Push policy

- `main` is protected. Only the repository owner pushes there.
- Contributors and AI agents push to feature branches and open pull requests.
- Pull requests must keep the local quality battery green and document any
  benchmark delta.

## Language policy

- Day-to-day collaboration: Latin American Spanish.
- Everything merged into the repository (docs, code comments, docstrings,
  user-facing strings, proposal files): English.
- Exception: deliberate non-English test/security payloads. Add a short
  comment if intent is not obvious.

## Disclaimer

Any reference to third-party trademarks is purely descriptive and does not
imply affiliation or endorsement.
