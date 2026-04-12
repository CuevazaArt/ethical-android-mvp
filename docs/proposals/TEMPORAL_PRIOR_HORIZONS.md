# Temporal prior from consequence horizons (`horizon_weeks` / `horizon_long_term`)

## Problem

`qualitative_temporal_branches` in `consequence_projection.py` exposes **three narrative strings** (`horizon_immediate`, `horizon_weeks`, `horizon_long_term`) for UX / LLM tone. They do **not** feed the decision core. The question is how **horizon_weeks** (recent pattern) and **horizon_long_term** (arc / stability) could **modulate the Bayesian mixture** without Monte Carlo or full teleology scoring.

## Design principle

Use **NarrativeMemory** episodes (same `context`, optional `action_taken` hint) to extract **two scalar signals**, then apply a **small bounded nudge** to `BayesianEngine.hypothesis_weights` **after** optional episodic refresh (`KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`) and **before** `evaluate()`.

The qualitative strings in the chat JSON **remain**; the numeric bridge is **orthogonal** (operators can enable one without the other).

## Signals (numeric)

**Episodes considered:** `NarrativeEpisode` rows with `context ==` current kernel context; optionally filtered by similarity to `action_hint` (prefix or substring on `action_taken`) when non-empty.

1. **`weeks_trend` (−1 … +1)** — *horizon_weeks*  
   - Window: last **N** calendar days (`KERNEL_TEMPORAL_HORIZON_WEEKS_DAYS`, default 21).  
   - Episodes in window, chronological order.  
   - If fewer than 3 episodes → `0.0` (no drift claim).  
   - Otherwise: compare mean `ethical_score` in the **first third** vs **last third** of that window (by time).  
   - Map difference to `[-1, 1]` with a small scale (e.g. divide by 2 and clamp): rising outcomes → positive; falling → negative.

2. **`long_term_stability` (0 … 1)** — *horizon_long_term*  
   - All matching episodes (full arc), or cap last 200 for cost.  
   - `stability = 1 / (1 + std(ethical_score))` — high variance → lower stability.  
   - Optional: blend with `|mean(ethical_score)|` to reflect overall “virtue of arc” (kept bounded).

3. **`combined` (−1 … +1)** — single nudge axis  
   - Default blend: `combined = 0.55 * weeks_trend + 0.45 * (2 * long_term_stability - 1)` so long arc can slightly open or close the mixture when stability is interpretable.  
   - Tunable via env in code if needed; **α** below scales the effect, not this blend.

## Effect on `hypothesis_weights`

- **Not** a full retargeting: use **`α_temporal`** (`KERNEL_TEMPORAL_HORIZON_ALPHA`, default **0.08**) to mix current weights toward a **direction vector**:
  - **Deteriorating** (`combined < 0`): shift modestly toward **caution / deontological** slot (index 1 in `[util, deon, virtue]` ordering used in `DEFAULT_HYPOTHESIS_WEIGHTS`).
  - **Improving** (`combined > 0`): slight shift toward **utilitarian** direct impact (index 0).
- Renormalize to sum 1.

## Genome drift cap (same family as Ψ Sleep)

After the nudge, **clamp** each component so **relative deviation** from `kernel._bayesian_genome_weights` does not exceed `KERNEL_ETHICAL_GENOME_MAX_DRIFT` (same policy as `identity_integrity.hypothesis_weights_allowed` / Ψ Sleep). This mirrors “attenuated, never overwrites” and reuses existing robustness knobs.

## Ordering in `EthicalKernel.process`

1. `reset_mixture_weights` **or** `refresh_weights_from_episodic_memory` (if `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`).  
2. If `KERNEL_TEMPORAL_HORIZON_PRIOR`: `apply_horizon_prior_to_engine(...)` (uses `compute_horizon_signals` + clamp).  
3. `bayesian.evaluate(clean_actions)`.

## Environment

| Variable | Role |
|----------|------|
| `KERNEL_TEMPORAL_HORIZON_PRIOR` | `1` / `true` to enable the nudge (default **off**). |
| `KERNEL_TEMPORAL_HORIZON_ALPHA` | α_temporal (default `0.08`). |
| `KERNEL_TEMPORAL_HORIZON_WEEKS_DAYS` | Window for weeks signal (default `21`). |

## Relation to UX teleology

- `teleology_branches` JSON is still produced from `qualitative_temporal_branches` for transparency.  
- When the temporal prior is enabled, optional JSON key `temporal_prior_debug` (future) could echo `weeks_trend`, `combined` — not required for MVP.

## See also

- [ADR 0005](adr/0005-temporal-prior-from-consequence-horizons.md)  
- `src/modules/weighted_ethics_scorer.py` — `refresh_weights_from_episodic_memory` (compat import: `bayesian_engine.py`)  
- `src/modules/temporal_horizon_prior.py` — implementation hook  
- `src/modules/consequence_projection.py` — qualitative strings only
