# Empirical pilot fixtures

- **`scenarios.json`** — curated simulation IDs + optional `reference_action` labels for agreement metrics (see [`docs/proposals/EMPIRICAL_METHODOLOGY.md`](../../docs/proposals/EMPIRICAL_METHODOLOGY.md)). Optional **`difficulty_tier`** tags each batch row for `summary.by_tier` (e.g. `common`, `difficult`, `sensor_fusion`).
- **`last_run_summary.json`** — archived **summary** from `scripts/run_empirical_pilot.py --json` (expected agreement rates for the default fixture). Update when labels or kernel batch behavior changes deliberately.

**Stochastic stress (research, not regression):** `scripts/run_stochastic_sandbox.py` — Monte Carlo rolls with artificial signal noise; see `docs/proposals/README.md` §4b.

Regression coverage: `tests/test_empirical_pilot_runner.py`.
