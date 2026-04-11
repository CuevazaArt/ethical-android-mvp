# ADR 0005 — Temporal prior from consequence horizons (Bayesian mixture nudge)

**Status:** Accepted (April 2026)

## Context

`consequence_projection.qualitative_temporal_branches` emits narrative **horizon_weeks** and **horizon_long_term** strings for v7 teleology UX; they do not affect `BayesianEngine`. Separately, `refresh_weights_from_episodic_memory` already nudges `hypothesis_weights` from recent episodes when `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS=1`. We need a **coherent, minimal** way to connect “horizon” intuition to the mixture **without** Monte Carlo or replacing episodic refresh.

## Decision

1. **Numeric signals only** — derived from `NarrativeMemory` (matching `context`, optional `action_hint`): `weeks_trend`, `long_term_stability`, `combined` — see [`TEMPORAL_PRIOR_HORIZONS.md`](../TEMPORAL_PRIOR_HORIZONS.md).

2. **Implementation** — `src/modules/temporal_horizon_prior.py`: `compute_horizon_signals`, `apply_horizon_prior_to_engine` mutates `BayesianEngine.hypothesis_weights` in place.

3. **Ordering** — After episodic refresh (or reset), before `bayesian.evaluate`.

4. **Attenuation** — `KERNEL_TEMPORAL_HORIZON_ALPHA` (default `0.08`); **genome clamp** via `KERNEL_ETHICAL_GENOME_MAX_DRIFT` vs `_bayesian_genome_weights` (same policy family as Ψ Sleep).

5. **Default off** — `KERNEL_TEMPORAL_HORIZON_PRIOR` unset/false: no call; CI and existing tests unchanged.

6. **Qualitative strings** — Unchanged; they remain advisory UX. The bridge is **numeric + Bayes only**.

## Consequences

- **Positive:** Closes the documented gap (CHANGELOG “registered spike”) with a testable, bounded hook.  
- **Negative:** Another env + interaction with episodic weights — operators should read `TEMPORAL_PRIOR_HORIZONS.md` before enabling both flags.

## Links

- [`TEMPORAL_PRIOR_HORIZONS.md`](../TEMPORAL_PRIOR_HORIZONS.md)  
- [`consequence_projection.py`](../../src/modules/consequence_projection.py)  
- [`bayesian_engine.py`](../../src/modules/bayesian_engine.py)
