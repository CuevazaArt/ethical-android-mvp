# Proposal — Bayesian mixture weight feedback (ADR 0012 stack)

This note summarizes **operator feedback over util/deon/virtue mixture weights**: what is implemented, how to enable it, and where to read the full design. It does not replace the ADR; it orients contributors and operators.

## Scope

The **weighted ethics scorer** combines three hypothesis valuations with mixture weights `w` on the 2-simplex. ADR 0012 adds optional **Bayesian-style** machinery: calibrated reporting (Level 1), feedback-driven posteriors (Level 2), context-dependent posteriors (Level 3), and an optional **proper likelihood** path for explicit triples.

| Piece | Role |
|-------|------|
| **Level 1 — BMA** | Monte Carlo win probabilities under a Dirichlet prior over `w`; does not change the default argmax unless operators act on probabilities. |
| **Level 2 — Feedback** | Updates Dirichlet-style concentration from operator preferred actions on batch scenarios. Two backends: **heuristic** (agreeing samples) or **softmax + IS** (see below). |
| **Level 3 — Context** | Separate posteriors per `context_type` in feedback JSON; each tick selects α via classifier (override, scenario-id map, or keyword map). Mixture-ranking path only; explicit triples stay global. |
| **Softmax likelihood** | Plackett-Luce choice probability; posterior approximated by **importance sampling** from the prior + moment-matched Dirichlet projection; sequential iteration per feedback item. |

## Source modules

| Module | Content |
|--------|---------|
| [`src/modules/bayesian_mixture_averaging.py`](../../src/modules/bayesian_mixture_averaging.py) | Level 1 BMA, `monte_carlo_win_probabilities`. |
| [`src/modules/feedback_mixture_posterior.py`](../../src/modules/feedback_mixture_posterior.py) | Loads feedback JSON; mixture-ranking sequential update; Level 3 bucketing; explicit-triples dispatch. |
| [`src/modules/feedback_mixture_updater.py`](../../src/modules/feedback_mixture_updater.py) | `FeedbackUpdater` for explicit util/deon/virtue triples; heuristic vs `KERNEL_FEEDBACK_LIKELIHOOD=softmax_is`. |
| [`src/modules/ethical_mixture_likelihood.py`](../../src/modules/ethical_mixture_likelihood.py) | Softmax log-likelihood, joint likelihood, IS posterior, sequential IS, predictive check, `calibrate_beta`. |
| [`src/kernel.py`](../../src/kernel.py) | Applies feedback before scoring when `KERNEL_BAYESIAN_FEEDBACK` + path set; exposes `KernelDecision` fields (`mixture_posterior_alpha`, `feedback_consistency`, `mixture_context_key`, BMA fields). |

## Environment (operator-oriented)

**Feedback load (kernel)**

- `KERNEL_BAYESIAN_FEEDBACK=1`
- `KERNEL_FEEDBACK_PATH` — JSON list of `{scenario_id, preferred_action, confidence?, context_type?, ...}`

**Level 1**

- `KERNEL_BMA_ENABLED`, `KERNEL_BMA_ALPHA`, `KERNEL_BMA_SAMPLES`, `KERNEL_BMA_SEED`

**Level 2 (explicit triples)**

- `KERNEL_FEEDBACK_UPDATE_STRENGTH`, `KERNEL_FEEDBACK_MC_SAMPLES`, `KERNEL_FEEDBACK_SEED`, `KERNEL_FEEDBACK_MAX_DRIFT`
- `KERNEL_FEEDBACK_LIKELIHOOD` — default heuristic; set `softmax_is` for Plackett-Luce + importance sampling (see `ethical_mixture_likelihood.py`).
- `KERNEL_FEEDBACK_SOFTMAX_BETA` — inverse temperature for softmax likelihood (default `10.0`).

**Level 3 (mixture-ranking path)**

- `KERNEL_BAYESIAN_CONTEXT_LEVEL3=1`
- `KERNEL_ACTIVE_CONTEXT_TYPE`, `KERNEL_CONTEXT_SCENARIO_MAP_JSON`, `KERNEL_CONTEXT_KEYWORDS_JSON`

See also [`.env.example`](../../.env.example) for commented stubs.

## Tests

- [`tests/test_bma_mixture_adr0012.py`](../../tests/test_bma_mixture_adr0012.py)
- [`tests/test_feedback_mixture_updater.py`](../../tests/test_feedback_mixture_updater.py)
- [`tests/test_context_mixture_level3.py`](../../tests/test_context_mixture_level3.py)
- [`tests/test_ethical_mixture_likelihood.py`](../../tests/test_ethical_mixture_likelihood.py)

## Canonical design record

Full decisions, philosophy, and naming cautions: **[ADR 0012 — Bayesian weight inference](../adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md)**.

Older long-form proposals may still be recovered from **git history** or branch `backup/main-2026-04-10`.
