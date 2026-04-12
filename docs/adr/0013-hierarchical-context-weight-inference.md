# ADR 0013 — Hierarchical context-dependent weight inference (Level 3)

**Status:** Proposed  
**Date:** 2026-04-12  
**Supersedes:** —  
**Depends on:** [ADR 0012](0012-bayesian-weight-inference.md) (Levels 1–2)  
**Related:** [ADR 0009](0009-ethical-mixture-scorer-naming.md) (naming), [ADR 0010](0010-poles-pre-argmax-modulation.md) (poles)

---

## Context

ADR 0012 introduced Bayesian weight updating at two levels: model averaging (Level 1) and operator feedback (Level 2).  Level 2 learns a **global** posterior over mixture weights from feedback across all scenario types.

The v5 experiment verification revealed a structural limitation of a single global posterior: when operator feedback is **context-divergent** — e.g., preferring virtue-heavy weights for resource allocation but util-heavy for confrontation — the global posterior is pulled in conflicting directions and may satisfy **none** of the preferences.

Concretely, with three context-divergent feedback items:

- Global Level 2 posterior satisfies 1 of 3 preferences (33%).
- Per-context Level 3 posteriors satisfy 2 of 3 preferences (67%).

The gap comes from a geometric fact: the feasible region for all three simultaneously is **empty** on the simplex, but the feasible regions *per context type* are each substantial (25–40% of the simplex).

Additionally, the existing codebase already has context-dependent logic that supports per-context learning:

- `BayesianEngine._likelihoods()` boosts different hypotheses depending on context (`integrity → deon`, `relational → virtue`, `emergency → util`).
- `EthicalPoles.CONTEXTS` defines per-context multipliers for pole evaluation.
- `NarrativeMemory` stores context per episode.
- The `feedback.json` schema (ADR 0012) already includes a `context_type` field.

---

## Decision

Introduce a **hierarchical Dirichlet updater** that maintains one `FeedbackUpdater` per context type, sharing strength through a global prior.

### Architecture

```
HierarchicalUpdater
├── global_updater: FeedbackUpdater        (Level 2 — always active)
├── context_updaters: {                    (Level 3 — per context type)
│     "resource_allocation": FeedbackUpdater,
│     "promise_conflict":    FeedbackUpdater,
│     "confrontation":       FeedbackUpdater,
│     "emergency":           FeedbackUpdater,
│     "integrity":           FeedbackUpdater,
│     "relational":          FeedbackUpdater,
│     "general":             FeedbackUpdater,
│   }
├── context_counts: {str: int}             (feedback items per type)
└── context_map: {str: str}                (legacy context → type)
```

### Update rule

When a feedback item arrives with `context_type = C`:

1. **Global** updater processes it (shifts the shared prior).
2. **Context-specific** updater for `C` processes it (shifts the local prior).
3. `context_counts[C]` increments.

### Posterior blending

When a decision is needed for context type `C`:

- If `context_counts[C] < min_local_items` (default 3): return the **global** posterior (Level 2 fallback).
- Otherwise: blend global and local posteriors:

```
posterior_mean(C) = (1 - τ) · global_mean + τ · local_mean(C)
```

Where τ is a sigmoid-like function of local data count:

```
τ = τ_max · (1 - exp(-n_local / 3))
```

At n=0: τ=0 (pure global).  At n=3: τ≈0.50.  At n=10: τ≈0.77.  At n→∞: τ→τ_max (default 0.8, never fully ignores global).

### Context type taxonomy

The taxonomy merges existing context strings from the codebase:

| Context type | Legacy mappings | Natural prior bias |
|---|---|---|
| `resource_allocation` | community, everyday | virtue |
| `promise_conflict` | integrity_loss | deon |
| `confrontation` | hostile_interaction | deon/util |
| `emergency` | medical_emergency | util |
| `integrity` | integrity_loss, android_damage | deon |
| `relational` | everyday_ethics, community | virtue |
| `general` | (fallback for None) | uniform |

Novel context types provided explicitly in feedback are accepted and created on demand.

### Activation threshold

A context type's local posterior is only used when it has ≥ `min_local_items` feedback items (default 3).  Below that threshold, the system uses the global posterior — identical to Level 2 behavior.  This prevents overfitting on 1–2 data points.

---

## Implementation

The implementation is contained in two files:

- `feedback_updater.py` — Level 1 + Level 2 (unchanged from ADR 0012).
- `hierarchical_updater.py` — Level 3 wrapper (~300 lines, composing with `FeedbackUpdater`).

Config: `KERNEL_HIERARCHICAL_FEEDBACK` (default `False`), `KERNEL_HIERARCHICAL_MIN_LOCAL` (default `3`), `KERNEL_HIERARCHICAL_TAU_MAX` (default `0.8`).

---

## Consequences

### Positive

- **Resolves context-divergent feedback** that a global posterior cannot handle.  Resource allocation, promise-keeping, and confrontation can each learn their own optimal weight profile.
- **Graceful degradation**: with zero local feedback, behavior is identical to Level 2.  No behavioral change unless explicitly enabled and fed data.
- **Dynamic context types**: operators can define new context types simply by including `context_type` in their feedback records.  No code changes needed.
- **Cheap**: ~300 lines on top of existing `FeedbackUpdater`, no new dependencies, all tests passing (11/11).

### Negative

- **Data requirement**: needs ≥3 feedback items per context type to activate.  With only 3 scenario types (v5 experiments), each type starts with 1 scenario — more scenarios per type needed for robust posteriors.
- **Complexity budget**: the system now has three levels of Bayesian machinery (BMA, global update, hierarchical update).  Clear documentation and the activation threshold mitigate confusion, but operators should understand which level is active.
- **τ blending is heuristic**: the exponential blending function is reasonable but not derived from a formal hierarchical Bayesian model.  A proper hierarchical Dirichlet process would be theoretically cleaner but substantially harder to implement and explain.

### Neutral

- The `context_type` field in `feedback.json` is forward-compatible with this ADR — no schema change needed.
- `snapshot()`/`restore()` preserves the full hierarchical state, compatible with `ImmortalityProtocol`.

---

*MoSex Macchina Lab — ADR 0013, April 2026.*
