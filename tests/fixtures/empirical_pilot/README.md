# Empirical pilot fixtures

- **`scenarios.json`** — curated simulation IDs + optional `reference_action` labels for agreement metrics (see [`docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md`](../../docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md)). Optional **`difficulty_tier`** (`common` \| `difficult` \| `extreme`) tags each batch row for sandbox monitoring; see [`docs/proposals/PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md`](../../docs/proposals/PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md).
- **`last_run_summary.json`** — archived **summary** from `scripts/run_empirical_pilot.py --json` (expected agreement rates for the default fixture). Update when labels or kernel batch behavior changes deliberately.

**Stochastic stress (research, not regression):** `scripts/run_stochastic_sandbox.py` — Monte Carlo rolls with artificial signal noise; see `docs/proposals/PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md` §4b.

Regression coverage: `tests/test_empirical_pilot_runner.py`.
