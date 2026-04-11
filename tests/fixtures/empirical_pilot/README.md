# Empirical pilot fixtures

- **`scenarios.json`** — curated simulation IDs + optional `reference_action` labels for agreement metrics (see [`docs/EMPIRICAL_PILOT_METHODOLOGY.md`](../../docs/EMPIRICAL_PILOT_METHODOLOGY.md)).
- **`last_run_summary.json`** — archived **summary** from `scripts/run_empirical_pilot.py --json` (expected agreement rates for the default fixture). Update when labels or kernel batch behavior changes deliberately.

Regression coverage: `tests/test_empirical_pilot_runner.py`.
