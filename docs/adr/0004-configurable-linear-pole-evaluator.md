# ADR 0004 — Configurable linear pole evaluator (JSON)

**Status:** Accepted (April 2026)

## Context

`EthicalPoles.evaluate_pole` historically mixed three concerns in one `if/elif` chain: **hardcoded coefficients** (e.g. `0.6`, `0.4`, `0.2`), **no use of `action`** beyond moral strings, and **adding a pole** required editing the same method. Operators and tests need **versioned, auditable** weights without forked kernel code.

## Decision

1. **Layer 1 (implemented):** `LinearPoleEvaluator` in `src/modules/pole_linear.py` loads a JSON document defining, per pole name:
   - **terms:** weighted sum of named **features** (`risk`, `benefit`, `third_party_vulnerability`, `legality`, `one_minus_risk`, `const`).
   - **thresholds:** `good` / `bad` boundaries for `Verdict` (defaults preserve legacy ±0.3).
   - **moral:** templates with `{action}` for good / bad / gray.

2. **Default file:** `src/modules/pole_linear_default.json` — numerically equivalent to the pre-ADR heuristics.

3. **Override:** `KERNEL_POLE_LINEAR_CONFIG` — absolute path to an alternate JSON file (same schema). Invalid path → startup error when `EthicalPoles()` is constructed.

4. **Registration:** `EthicalPoles.base_weights` remains the **list of pole names** for aggregation. Each name must have an entry in the JSON (or evaluation falls back to the unknown-pole stub). Adding a **fourth pole** requires: new key in JSON, new entry in `BASE_WEIGHTS` (and context multipliers as today).

5. **Future layers (not in this ADR):** nonlinear interaction terms (e.g. `risk × vulnerability`) and `sklearn` / pickle evaluators behind the same **evaluate → `PoleEvaluation`** contract, loaded via a future `KERNEL_POLE_EVALUATOR` switch.

## Consequences

- **Positive:** Fixtures and golden tests can pin coefficients; experiments are diffable.
- **Negative:** Malformed JSON breaks construction — fail fast; document schema in this ADR and `pole_linear_default.json`.

## Links

- `src/modules/ethical_poles.py`, `src/modules/pole_linear.py`  
- [`POLES_WEAKNESS_PAD_AND_PROFILES.md`](../POLES_WEAKNESS_PAD_AND_PROFILES.md)  
- [`PRODUCTION_HARDENING_ROADMAP.md`](../PRODUCTION_HARDENING_ROADMAP.md) (pole limits)
