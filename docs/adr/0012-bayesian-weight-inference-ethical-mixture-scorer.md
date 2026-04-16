# ADR 0012 — Bayesian weight inference for the ethical mixture scorer

**Status:** Accepted (Levels 1–3 implemented; Phase D batch BMA + Phase F LOO calibration done)  
**Date:** 2026-04-12  
**Supersedes:** —  
**Related:** [ADR 0009](0009-ethical-mixture-scorer-naming.md) (naming), [ADR 0010](0010-poles-pre-argmax-modulation.md) (poles pre-argmax), [ADR 0011](0011-context-richness-pre-argmax.md) (context richness), [`experiments/README.md`](../../experiments/README.md)

---

## Context

ADR 0009 established that the "weighted mixture scorer" is **not** Bayesian inference — it is a fixed convex combination of three ethical valuations (util, deon, virtue) followed by an argmax. The v5 experiment design (historical writeups, recoverable from git) confirmed this empirically: the decision boundary is a hyperplane in weight space, regions are convex, and the system is fully deterministic given a weight vector `w`.

The simplex grid analysis (scenarios 17–19) further showed:

- The **center** `(1/3, 1/3, 1/3)` sits near decision boundaries with gaps as low as 0.0007, meaning the default weight choice is **fragile**.
- Different **Dirichlet alpha** priors produce dramatically different flip rates (13.6% at α=12 vs 62.5% at α=0.5 for scenario 18), proving that the sampling distribution over weights matters for sensitivity analysis.
- **Signal stress** at even 0.1 causes 46–64% flips at the center — confirming the system is sensitive in boundary regions.

These results raise a design question: if the system's ethical behavior depends critically on where `w` sits on the simplex, should the system **reason about that uncertainty** rather than commit to a fixed point?

Additionally, the experiment infrastructure already generates the data needed for Bayesian model averaging (Monte Carlo samples over the simplex with per-point winners and scores).

---

## Decision

Introduce **three incremental levels** of Bayesian capability into the ethical mixture scorer. Each level builds on the previous one and on existing infrastructure. Levels are independently deployable; an operator may stop at any level.

### Level 1 — Bayesian Model Averaging (BMA)

**What changes:** Instead of evaluating at a single fixed weight vector `w*`, integrate the score over a Dirichlet prior `P(w)` and take the argmax of the **expected** score:

```
E[score(action)] = ∫ score(action, w) · P(w) dw
decision = argmax_action E[score(action)]
```

Since `score(action, w) = Σ_i w_i · valuator_i(action)` is linear in `w`, the integral is analytic:

```
E[score(action)] = Σ_i E[w_i] · valuator_i(action)
                 = Σ_i (α_i / Σ α) · valuator_i(action)
```

For a symmetric Dirichlet `Dir(α, α, α)`, this reduces to the center `(1/3, 1/3, 1/3)` — identical to the current point estimate. **The BMA winner is the same as the point-estimate winner** for any symmetric prior.

However, BMA provides a **richer output**: the **win probability** `P(action wins)` under the prior, computed by Monte Carlo:

```python
P(action_k wins) = (1/N) Σ_n 1[argmax_j score(action_j, w_n) == k]
```

This transforms a binary winner into a probability distribution over candidates. Scenario 17 at the center goes from "need wins" to "need wins with P=0.35, impact P=0.35, lottery P=0.30" — far more informative for the operator.

**Implementation:** Level 1 is implemented in `src/modules/bayesian_mixture_averaging.py` (`parse_bma_alpha_from_env`, `monte_carlo_win_probabilities`). It is **not** a separate class named `BayesianMixtureAverager`; `EthicalKernel.process` calls those helpers when BMA is enabled.

**`KernelDecision` fields (actual names in code):**

| Field | Meaning |
|-------|---------|
| `bma_win_probabilities` | Empirical win frequencies per candidate name |
| `bma_dirichlet_alpha` | Prior `(α_u, α_d, α_v)` used for sampling |
| `bma_n_samples` | Monte Carlo count |

**Config**

| Variable | Default | Meaning |
|----------|---------|---------|
| `KERNEL_BMA_ENABLED` | off | Enable BMA fields on `KernelDecision` |
| `KERNEL_BMA_ALPHA` | `3.0` | Symmetric scalar or three comma-separated positives |
| `KERNEL_BMA_SAMPLES` | `5000` | Monte Carlo draws |
| `KERNEL_BMA_SEED` | `42` | RNG seed |

**What does NOT change:** The winner selection. BMA with symmetric priors preserves the current argmax. This is a **pure information addition** — no behavioral change unless the operator acts on the probabilities.

### Level 2 — Conjugate posterior updating from operator feedback

**What changes:** The Dirichlet prior `α = (α_u, α_d, α_v)` is no longer fixed — it **updates** when an operator provides feedback on past decisions.

**Feedback format:** A JSON record per scenario:

```json
{
  "scenario_id": 17,
  "preferred_action": "distribute_by_need",
  "confidence": 0.8,
  "timestamp": "2026-04-12T18:00:00Z"
}
```

**Update rule (approximate conjugate):**

For each feedback item, compute the **feasibility posterior** — the subset of the simplex where the preferred action wins — and shift α toward the mean of that region:

```python
# Sample from current prior
samples = dirichlet_sample(alpha, N=20000)

# Filter: which samples make the preferred action win?
agreeing = [w for w in samples
            if argmax(score(actions, w)) == preferred_action]

# Posterior update: shift alpha toward agreeing mean
mean_agree = mean(agreeing, axis=0)           # shape (3,)
alpha_new  = alpha + strength * mean_agree    # strength ~ 2-3 per feedback
```

This is not an exact conjugate update (the likelihood is an indicator over a convex region, not a categorical observation), but it is a valid **approximate Bayesian** update that concentrates the posterior on weight vectors consistent with operator preferences.

**Multi-scenario consistency:** When feedback spans multiple scenarios, the posterior seeks weights that satisfy **all** preferences simultaneously. The v5 simulation showed:

- **Compatible feedback** (need in 17, partial in 18, retreat in 19): feasible region = 26.6% of simplex. Posterior converges to `w ≈ (0.26, 0.31, 0.43)` with P(all correct) rising from 32% to 75% over 8 epochs.
- **Contradictory feedback** (impact in 17, defer in 18, protect in 19): feasible region = **0.0%** of simplex. No single weight vector satisfies all preferences.

**Contradiction detection** is a free by-product: if the feasible region is empty (or below a threshold, e.g. < 1% of the simplex), the system flags to the operator via `feedback_consistency` (`compatible` | `contradictory` | `insufficient`).

**Implementation:**

- **`src/modules/feedback_mixture_posterior.py`** — `load_and_apply_feedback`, numpy `mixture_ranking` path, and joint MC diagnostics (`joint_satisfaction_monte_carlo`).
- **`src/modules/feedback_mixture_updater.py`** — `FeedbackUpdater` (pure Python Dirichlet sampling). Used when **every** referenced scenario has explicit `hypothesis_override` triples on all candidates (e.g. scenarios **17–19**); otherwise the numpy + full mixture path applies.
- **`src/kernel.py`** — loads feedback when `KERNEL_BAYESIAN_FEEDBACK` is set, applies posterior to `hypothesis_weights` before the tick, and attaches `mixture_posterior_alpha` and `feedback_consistency`.

**`KernelDecision` fields**

| Field | Meaning |
|-------|---------|
| `mixture_posterior_alpha` | Posterior Dirichlet α (tuple of three floats) |
| `feedback_consistency` | `compatible` \| `contradictory` \| `insufficient` |

**Note:** Richer diagnostics (`p_all_feedback_satisfied`, per-scenario rates, `joint_satisfaction_rate`) appear in the **return metadata** of `load_and_apply_feedback` for tooling and tests; they are not all duplicated as top-level `KernelDecision` fields today.

**Config**

| Variable | Default | Meaning |
|----------|---------|---------|
| `KERNEL_BAYESIAN_FEEDBACK` | off | Enable loading and applying feedback |
| `KERNEL_FEEDBACK_PATH` | — | JSON path |
| `KERNEL_FEEDBACK_UPDATE_STRENGTH` | `3.0` | Scale on mean-agreeing mixture vector |
| `KERNEL_FEEDBACK_MC_SAMPLES` | `20000` | Inner samples per feedback item |
| `KERNEL_FEEDBACK_SEED` | `42` | RNG seed |
| `KERNEL_FEEDBACK_MAX_DRIFT` | `0.30` | Max L∞ drift of **normalized** posterior mean vs initial prior per axis (`FeedbackUpdater` path) |

**Feedback JSON:** list of objects as above, or `{ "items": [ ... ] }`.

**What does NOT change:** The scorer internals. The posterior `α` feeds back into Level 1's BMA prior when feedback runs first — the two levels compose naturally. The scorer itself remains a linear mixture.

### Level 3 — Context-dependent weight inference (implemented, mixture_ranking path)

Level 2 learns a **global** posterior over weights from pooled feedback. Level 3 learns **separate** Dirichlet posteriors per `context_type` bucket (from feedback JSON), then **selects** which α to use on each tick via a lightweight classifier.

**Implemented behavior (``src/modules/feedback_mixture_posterior.py``):**

- Feedback rows may include optional string ``context_type``. Rows without it go to bucket ``_global``.
- For each bucket, the same **sequential α update** as Level 2 runs from the same prior ``parse_bma_alpha_from_env()``, **independently** (no cross-bucket coupling in the update).
- **Classifier** (priority): ``KERNEL_ACTIVE_CONTEXT_TYPE`` → ``KERNEL_CONTEXT_SCENARIO_MAP_JSON`` keyed by ``[SIM n]`` in the scenario string → ``KERNEL_CONTEXT_KEYWORDS_JSON`` substring map on scenario+context → default key ``default``.
- **Selection**: if the active key matches a bucket, use that posterior α; else ``_global`` if present; else elementwise **mean** of bucket posteriors. When no tick context is passed (e.g. CLI), the code uses the **mean** of bucket posteriors (`active_context_key` = ``blended_mean``).
- **Explicit-triples feedback** (scenarios with full ``hypothesis_override`` on all candidates): still uses the **global** ``FeedbackUpdater`` path; Level 3 is **not** applied per context (see ``meta["level3_note"]``).

**Env:** ``KERNEL_BAYESIAN_CONTEXT_LEVEL3`` plus the classifier vars above. **Kernel:** ``KernelDecision.mixture_context_key`` records which bucket was used when feedback ran.

**Data:** Richer per-type learning benefits from **several** feedback items per ``context_type``; sparse data still runs but posteriors may be noisy.

---

## Implementation path

| Phase | Level | Effort | Dependency |
|-------|-------|--------|------------|
| **Phase A** | Level 1 (BMA) | Done | `WeightedEthicsScorer` + `bayesian_mixture_averaging.py` |
| **Phase B** | Level 2 (feedback) | Done | Phase A + feedback JSON + `feedback_mixture_posterior.py` / `feedback_mixture_updater.py` |
| **Phase C** | Contradiction detection | Done | Phase B (`feedback_consistency`, joint MC metadata) |
| **Phase D** | Integration with batch study drivers (`--bma-enabled` / `--bma-alpha` / `--bma-samples` in `run_mass_kernel_study.py`; `bma_win_prob_*` fields in JSONL rows; schema v6) | Done | Phase A |
| **Phase E** | Level 3 (context posteriors + classifier) | Done (mixture_ranking) | Phase B + ``context_type`` in feedback JSON |
| **Phase F** | LOO posterior predictive calibration diagnostic (`scripts/run_likelihood_calibration.py`) | Done | Phase B + explicit-triples feedback |

---

## Consequences

### Positive

- **Level 1** adds win probabilities to every decision when enabled; for symmetric priors the expected-score shortcut matches the point estimate, while MC still delivers the **distribution** over winners.
- **Level 2** enables the system to **learn** from operator preferences, concentrating on weight vectors that produce preferred outcomes. This is the first genuine Bayesian-style component in this pipeline for mixture weights.
- **Contradiction detection** surfaces ethical tensions that are invisible to a single fixed `w`.
- The upgrade is **backward-compatible**: with both flags off, behavior matches the pre-ADR path.

### Negative

- **Naming:** The system can legitimately be described as using Bayesian machinery for **mixture weights**, but it is **not** Bayesian inference over ethical frameworks, not Bayesian RL, and not a Bayesian neural network. ADR 0009's caution about naming remains relevant — prefer "Bayesian weight updating" over "Bayesian ethics."
- **Feedback quality:** Level 2 is only as good as the operator feedback. Sparse or noisy feedback yields a weak posterior. Report `n_feedback_items` and joint-satisfaction metadata where available so operators can judge quality.
- **Computational cost of Monte Carlo:** Level 1 adds `KERNEL_BMA_SAMPLES` extra `evaluate` calls per `process` when enabled. Level 2 adds inner MC per feedback item (`KERNEL_FEEDBACK_MC_SAMPLES`).
- **Philosophical claim:** Bayesian updating of weights assumes there is a **stable** mixture vector that feedback helps locate. That is a stronger commitment than treating weights as purely designer-chosen knobs. The research disclaimer in [`experiments/README.md`](../../experiments/README.md) should keep this distinction clear.

### Neutral

- The scorer remains a linear mixture with argmax. No change to the MalAbs stack, will module, or narrative poles beyond existing integration points.
- The legacy `BayesianEngine` name predates this ADR; Level 2 does not require renaming that class.

---

## Alternatives considered

**A. Full Bayesian inference over ethical frameworks.** Rejected: requires a generative model of how each framework predicts observations, which is philosophically and technically unbounded. Level 3 gestures in this direction but does not commit.

**B. Reinforcement learning from feedback.** Rejected: RL optimizes a scalar reward, which presupposes a single ethical objective. The multi-framework mixture structure is richer than a single reward, and the Bayesian approach preserves multi-hypothesis semantics at the weight level.

**C. Fixed optimization of weights (grid search over simplex).** Already possible with v5 data (Part 4 of historical `NEXT_EXPERIMENT_DESIGN` drafts, recoverable from git). This finds a **single optimal point** rather than a **distribution**, losing uncertainty information. Level 1 BMA is strictly more informative for sensitivity reporting.

**D. Do nothing.** Viable: the system works with fixed weights. The v5 experiments showed that the default center is **fragile** (small gaps in scenario 17), and without at least Level 1 there is no standard telemetry for that fragility.

---

## Implementation references

| Component | Path |
|-----------|------|
| BMA (Level 1) | `src/modules/bayesian_mixture_averaging.py` |
| Feedback posterior (Level 2) | `src/modules/feedback_mixture_posterior.py` |
| Explicit-triples updater | `src/modules/feedback_mixture_updater.py` (`FeedbackUpdater`) |
| Plackett-Luce / IS likelihood (optional) | `src/modules/ethical_mixture_likelihood.py`; enable with `KERNEL_FEEDBACK_LIKELIHOOD=softmax_is` |
| Kernel integration | `src/kernel.py` (`KernelDecision`, `EthicalKernel.process`) |
| Offline posterior (no full kernel tick) | `scripts/run_feedback_posterior.py` |
| Level 3 (context buckets + classifier) | `feedback_mixture_posterior.py` (`classify_mixture_context`, `load_and_apply_feedback` + `tick_context`) |
| Phase D — BMA in batch study | `src/sandbox/mass_kernel_study.py` (`bma_enabled`, `bma_dirichlet_alpha`, `bma_n_samples` params; `bma_win_prob_*` row fields; schema v6); `scripts/run_mass_kernel_study.py` (`--bma-enabled`, `--bma-alpha`, `--bma-samples`) |
| Phase F — LOO calibration | `scripts/run_likelihood_calibration.py` (leave-one-out predictive probability audit for explicit-triples feedback) |
| Tests | `tests/test_bma_mixture_adr0012.py`, `tests/test_feedback_mixture_updater.py`, `tests/test_context_mixture_level3.py`, `tests/test_ethical_mixture_likelihood.py` |

---

*Ethos Kernel — ADR 0012, April 2026.*
