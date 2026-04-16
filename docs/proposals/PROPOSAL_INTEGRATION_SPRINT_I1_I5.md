# Integration Sprint I1–I5: Closing the Interlayer Gaps

**Author:** Claude Team  
**Date:** 2026-04-14  
**Status:** In Progress  
**ADR:** [ADR 0015](../adr/0015-interteam-integration-sprint.md)

---

## Summary

This document describes the five integration items that close the gaps between the Claude
(Bayesian kernel), Antigravity (narrative), and Cursor (perception) teams. Each item is
small, backward-compatible, and guarded by a feature flag where behavior changes.

---

## Current Architecture (before this sprint)

```
[Cursor]                    [Claude]                  [Antigravity]
_run_perception_stage()  →  bayesian.evaluate()   →   memory.register()
  signals{}                  KernelDecision             NarrativeEpisode
  PerceptionCoercionReport   applied_mixture_weights    significance / arc_id
  TemporalContext             hypothesis_weights         semantic_embedding
  LimbicProfile              WeightAuthorityStack        NarrativeIdentityState

  ↑ coercion lost             ↑ weights not persisted    ↑ leans not fed back
  ↑ ETA not used              ↑ events not emitted       ↑ not connected
```

## Target Architecture (after this sprint)

```
[Cursor]                    [Claude]                  [Antigravity]
_run_perception_stage()  →  signals["perception_uncertainty"] (I3)
TemporalContext          →  signals["urgency"] boost if ETA_MODULATION (I5)
                         →  bayesian.evaluate()
                         →  KernelDecision
                              applied_mixture_weights
                         →  EVENT_KERNEL_WEIGHTS_UPDATED (I2) → bus
                         →  memory.register(weights_snapshot=...) (I1)
                         →  NarrativeEpisode.weights_snapshot persisted

[Antigravity]
NarrativeIdentityState.leans → (if IDENTITY_POLICY=pole_pre_argmax)
                             → bayesian.pre_argmax_pole_weights (I4)
```

---

## I1 — `weights_snapshot` in NarrativeEpisode

**Files changed:** `src/modules/narrative.py`, `src/kernel.py`

**What:** Add `weights_snapshot: tuple[float,float,float] | None` to `NarrativeEpisode`
dataclass. Pass `decision.applied_mixture_weights` when calling `memory.register()`.

**Why:** Antigravity persists episodes to SQLite. Without weights, post-hoc questions
like "did high utilitarian weight correlate with worse outcomes in trauma arcs?" cannot
be answered.

**Backward compat:** Field is `None` for all episodes created before this sprint.
Antigravity schema migration: `ALTER TABLE episodes ADD COLUMN weights_snapshot TEXT`.

---

## I2 — `EVENT_KERNEL_WEIGHTS_UPDATED`

**Files changed:** `src/modules/kernel_event_bus.py`, `src/modules/weight_authority.py`

**What:** New bus constant + emission in `compose_mixture_weights()` when the output
differs from the input nudge layer (i.e., feedback actually changed the weights).

**Payload:**
```json
{
  "prior": [0.4, 0.35, 0.25],
  "posterior": [0.45, 0.32, 0.23],
  "trust": 1.0,
  "source": "feedback_posterior"
}
```

**Why:** Telemetry and future DAO hooks need to observe weight drift over time without
polling the kernel state directly.

---

## I3 — `perception_uncertainty` → Bayesian signals

**Files changed:** `src/kernel.py`

**What:** Read `PerceptionCoercionReport.uncertainty()` from the perception stage result
and inject into `signals["perception_uncertainty"]` before `bayesian.evaluate()`.

**Effect on scoring:** `_ethical_hypothesis_valuations()` uses `signals.get("uncertainty", 0)`
in the virtue hypothesis path. High perception_uncertainty will reduce virtue valuation,
making gray_zone outcomes more likely under degraded perception — correct behavior.

**Backward compat:** If `PerceptionStageResult` has no `coercion_report` (older Cursor
versions), defaults to 0.0. No change to existing behavior.

---

## I4 — `KERNEL_NARRATIVE_IDENTITY_POLICY`

**Files changed:** `src/kernel.py`

**What:** New env var, default `off`. When set to `pole_pre_argmax`, read
`NarrativeMemory.identity.state` leans and map to `pre_argmax_pole_weights`:

```python
# Mapping: identity lean → ethical pole
civic_lean     → "compassionate" pole weight
careful_lean   → "conservative" pole weight
deliberation_lean → average of virtue dimensions
```

**Why:** The system's past decisions created a self-model (identity leans). That self-model
should be able to gently modulate how new decisions are scored — without overriding the
Bayesian posterior.

**Backward compat:** Default `off` means no behavior change unless operator opts in.

**Requires from Antigravity:** `memory.identity` attribute exposing
`NarrativeIdentityState` with `.civic_lean`, `.care_lean`, `.deliberation_lean`,
`.careful_lean` fields.

---

## I5 — `KERNEL_TEMPORAL_ETA_MODULATION`

**Files changed:** `src/kernel.py`

**What:** New env var, default `off`. When enabled, boost `signals["urgency"]` based on
`TemporalContext.eta_seconds` and `battery_horizon_state`.

```python
reference_eta = float(os.environ.get("KERNEL_TEMPORAL_REFERENCE_ETA_S", "300"))
urgency_boost = clamp(reference_eta / max(eta_seconds, 1.0), 0.0, 1.0)
if battery_horizon_state == "critical":
    urgency_boost = min(urgency_boost + 0.3, 1.0)
signals["urgency"] = clamp(signals["urgency"] + urgency_boost * 0.4, 0.0, 1.0)
```

**Why:** A 30-second medical emergency with critical battery should score urgency ~1.0.
A nominal 10-minute task should not change urgency at all.

**Backward compat:** Default `off`. Requires Cursor's `PerceptionStageResult.temporal_context`.
Falls back gracefully if `temporal_context` is None.

---

## New Environment Variables Summary

| Variable | Default | Description |
|---|---|---|
| `KERNEL_NARRATIVE_IDENTITY_POLICY` | `off` | `off` \| `pole_pre_argmax` |
| `KERNEL_TEMPORAL_ETA_MODULATION` | `off` | `off` \| `on` |
| `KERNEL_TEMPORAL_REFERENCE_ETA_S` | `300` | Reference ETA in seconds for urgency normalization |

All previously defined variables (`KERNEL_FEEDBACK_TRUST_WEIGHT`, etc.) unchanged.

---

## Testing Plan

- I1: Unit test that `NarrativeEpisode.weights_snapshot` is set when
  `applied_mixture_weights` is present in `KernelDecision`
- I2: Unit test that event bus receives `EVENT_KERNEL_WEIGHTS_UPDATED` when
  `compose_mixture_weights` changes the weights
- I3: Unit test that `signals["perception_uncertainty"]` reaches scorer when
  coercion report has uncertainty > 0
- I4: Integration test that `pole_pre_argmax` mode sets `pre_argmax_pole_weights`
  from mock identity leans
- I5: Unit test that urgency is boosted under critical ETA + battery

---

## Coordination

| Team | Action Required | By |
|---|---|---|
| **Antigravity** | Add `weights_snapshot` column to SQLite schema (nullable) | Before merging to main |
| **Antigravity** | Confirm `memory.identity` accessor exists | Before I4 lands |
| **Cursor** | Confirm `PerceptionCoercionReport.uncertainty()` is stable | Before I3 lands |
| **Cursor** | Expose `PerceptionStageResult.coercion_report` if not present | Before I3 lands |
| **Cursor** | Confirm `PerceptionStageResult.temporal_context` accessible pre-scoring | Before I5 lands |
| **Claude** | All items in `master-claude`, all env vars default off | This sprint |
