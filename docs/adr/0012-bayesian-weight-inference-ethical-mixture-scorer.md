# ADR 0012 — Bayesian weight inference for the ethical mixture scorer

**Status:** Accepted (Level 1–2 implemented; Level 3 future)  
**Date:** 2026-04-12  
**Supersedes:** —  
**Related:** [ADR 0009](0009-ethical-mixture-scorer-naming.md) (naming), [ADR 0010](0010-poles-pre-argmax-modulation.md), [ADR 0011](0011-context-richness-pre-argmax.md), [`NEXT_EXPERIMENT_DESIGN.md`](../../experiments/million_sim/NEXT_EXPERIMENT_DESIGN.md)

## Context

ADR 0009 states that the weighted mixture scorer is **not** full Bayesian inference over latent ethical truths: it is a fixed convex combination of three valuations (util, deon, virtue) and an argmax. The v5 simplex experiments show that the **default** center `(1/3, 1/3, 1/3)` can sit near **decision boundaries** (small top-2 gaps), so the operating point is **fragile** unless additional telemetry is reported.

This ADR adds **optional**, **backward-compatible** machinery:

1. **Level 1 — BMA:** Monte Carlo **win probabilities** under a Dirichlet prior over mixture weights `w` (same scoring path as production; does not change the chosen action when the prior is symmetric about the mean used for point estimation — see implementation note).
2. **Level 2 — feedback posterior:** Approximate **Dirichlet posterior** updates from operator feedback on batch `scenario_id`s (mixture-only winners), plus **compatibility** reporting when joint preferences are geometrically impossible.

Level 3 (context-dependent hierarchical Dirichlet) is **out of scope** here; reserve a `context_type` field on feedback records for a future ADR.

## Decision

### Level 1 — `KERNEL_BMA_ENABLED`

After the usual `WeightedEthicsScorer.evaluate`, optionally run **Monte Carlo** sampling `w ~ Dirichlet(α)` with the **same** scorer configuration (including pre-argmax poles/context already set on `self.bayesian`), and tabulate empirical **win frequencies** per candidate action name.

**Environment**

| Variable | Default | Meaning |
|----------|---------|---------|
| `KERNEL_BMA_ENABLED` | off | Enable BMA attachment on `KernelDecision` |
| `KERNEL_BMA_ALPHA` | `3.0` | Symmetric scalar or three comma-separated positives |
| `KERNEL_BMA_SAMPLES` | `5000` | Monte Carlo draws |
| `KERNEL_BMA_SEED` | `42` | RNG seed |

**`KernelDecision` fields:** `bma_win_probabilities`, `bma_dirichlet_alpha`, `bma_n_samples`.

**Note:** For symmetric `Dirichlet(α,α,α)`, `E[w] = (1/3,1/3,1/3)`. The **point-estimate** winner from `evaluate` with default weights matches the winner under `E[w]` for **linear** scores in `w`. BMA’s primary value is the **distribution** over winners, not changing the argmax.

**Module:** `src/modules/bayesian_mixture_averaging.py`

### Level 2 — `KERNEL_BAYESIAN_FEEDBACK`

If enabled and `KERNEL_FEEDBACK_PATH` points to a JSON file, load feedback records and run **sequential approximate updates** to a Dirichlet `α` (see `src/modules/feedback_mixture_posterior.py`). Set `self.bayesian.hypothesis_weights = α / sum(α)` **before** episodic weight refresh (so episodic nudges can still apply afterward).

**Environment**

| Variable | Default | Meaning |
|----------|---------|---------|
| `KERNEL_BAYESIAN_FEEDBACK` | off | Enable |
| `KERNEL_FEEDBACK_PATH` | — | JSON path |
| `KERNEL_FEEDBACK_UPDATE_STRENGTH` | `3.0` | Scale on mean-agreeing mixture vector |
| `KERNEL_FEEDBACK_MC_SAMPLES` | `20000` | Inner samples per feedback item |
| `KERNEL_FEEDBACK_SEED` | `42` | RNG seed |

**Feedback JSON:** list of objects `{ "scenario_id": int, "preferred_action": str, "confidence"?: float, "timestamp"?: str, "context_type"?: str }` or `{ "items": [ ... ] }`.

**`KernelDecision` fields:** `mixture_posterior_alpha`, `feedback_consistency` (`compatible` | `contradictory` | `insufficient`).

Winners for feedback are evaluated with **mixture-only** `mixture_ranking` on `ALL_SIMULATIONS` scenarios (no full kernel).

## Consequences

### Positive

- Operators gain **uncertainty telemetry** (BMA) without changing the default decision path when BMA is off.
- **Inconsistent** feedback across scenarios can yield `feedback_consistency="contradictory"` after an inner MC finds no agreeing weight sample.

### Negative / caution

- **Naming:** This is **Bayesian weight / mixture** reporting, not “Bayesian ethics” in a foundational sense — ADR 0009’s caution remains.
- **Cost:** BMA adds `KERNEL_BMA_SAMPLES` extra `evaluate` calls per `process` when enabled.
- **Philosophy:** Feedback updates treat stated preferences as **constraints on `w`** in the mixture model — a stronger stance than fixed designer weights. Document in experiment disclaimers.

## Implementation references

| Component | Path |
|-----------|------|
| BMA | `src/modules/bayesian_mixture_averaging.py` |
| Feedback posterior | `src/modules/feedback_mixture_posterior.py` |
| Kernel integration | `src/kernel.py` (`KernelDecision`, `EthicalKernel.process`) |

---

*MoSex Macchina Lab — ADR 0012, April 2026.*
