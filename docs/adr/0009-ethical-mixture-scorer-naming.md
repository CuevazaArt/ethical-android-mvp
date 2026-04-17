# ADR 0009 — Ethical mixture scorer naming (not Bayesian inference)

## Status

Accepted — April 2026

## Context

The kernel scores and prunes candidate actions using a **weighted mixture** over three stylized ethical viewpoints (utilitarian / deontological / virtue-ethical). Default weights are fixed hyperparameters (`[0.4, 0.35, 0.25]`). Optional **bounded** nudges (episodic memory, temporal-horizon prior) adjust those weights; they are **not** likelihood-based posterior updates over a model.

The historical module and class names (`bayesian_engine`, `BayesianEngine`) suggested full Bayesian inference, which is **technically misleading** for reviewers and operators.

## Decision

1. **Canonical implementation** lives in [`src/modules/weighted_ethics_scorer.py`](../../src/modules/weighted_ethics_scorer.py) with primary types `WeightedEthicsScorer` and `EthicsMixtureResult`.
2. **Backward compatibility:** [`src/modules/bayesian_engine.py`](../../src/modules/bayesian_engine.py) exports `BayesianEngine` as an alias of `BayesianInferenceEngine`, which **wraps** `WeightedEthicsScorer` and may run optional telemetry or posterior-assisted modes (see module docstring; related ADR 0012). `BayesianResult` aliases `EthicsMixtureResult`. Default behavior remains mixture-first; the export name stays historically loaded.
3. **Environment variables** retaining `KERNEL_BAYESIAN_*` (e.g. `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`, `KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS`) are **not** renamed in this ADR, to avoid breaking deployments; their documented meaning is “mixture weights / legacy valuation mode,” not “run full Bayes.”

## Consequences

- New code and docs should point to `weighted_ethics_scorer` and describe **hyperparameters** and **bounded nudges** honestly.
- Forks that still import `bayesian_engine` continue to work without changes.
- A future ADR could introduce true online Bayesian updating (explicit likelihoods and posteriors) as a **separate** component, without overloading the mixture scorer name.

## Related

- [`THEORY_AND_IMPLEMENTATION.md`](../proposals/THEORY_AND_IMPLEMENTATION.md) — objective / uncertainty sections
- [ADR 0005](0005-temporal-prior-from-consequence-horizons.md) — temporal nudge to mixture weights
