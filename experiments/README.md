# Experiments

## Where things live

| Path | Purpose |
|------|---------|
| [`million_sim/`](million_sim/README.md) | Operator docs (report, history, **NEXT** design), v5 / simplex commands, env setup for batch runs. |
| [`million_sim/docs/ARTIFACTS_REGISTRY.md`](million_sim/docs/ARTIFACTS_REGISTRY.md) | **Lightweight** tables of last captured runs (no large JSONL/PNG in git). |
| [`million_sim/out/`](million_sim/out/) | **Generated only** (gitignored). Safe to delete; regenerate with scripts. Summaries: registry. |

## ADR 0012 feedback sample

Compatible operator feedback for scenarios **17–19** (explicit `hypothesis_override` triples) is versioned as:

[`tests/fixtures/feedback/compatible_17_18_19.json`](../tests/fixtures/feedback/compatible_17_18_19.json)

Point `KERNEL_FEEDBACK_PATH` at that file when testing `KERNEL_BAYESIAN_FEEDBACK=1`, or run the posterior CLI (same logic as the kernel, no `EthicalKernel.process` per row):

```bash
python scripts/run_feedback_posterior.py --pretty
python scripts/run_feedback_posterior.py --feedback tests/fixtures/feedback/compatible_17_18_19.json -o experiments/million_sim/out/feedback_posterior.json
```

(`million_sim/out/` is gitignored; pick any output path.)

## What does *not* belong here

- **Design specs and ADRs:** [`docs/adr/`](../docs/adr/), [`docs/proposals/`](../docs/proposals/).
- **Implementation:** [`src/modules/`](../src/modules/) (e.g. `feedback_mixture_updater.py`, `feedback_mixture_posterior.py`).

Avoid keeping duplicate drafts of those under `experiments/`; it causes drift and confusion.
