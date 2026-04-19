# ADR 0015 — Inter-team Integration Sprint: Closing the Interlayer Gaps

**Date:** 2026-04-14  
**Status:** Accepted (implemented)  
**Team:** Claude (proposer) | Affects: Antigravity, Cursor  
**Branch:** Integration landed via `master-Cursor` / peer hubs (see [`PROPOSAL_INTEGRATION_SPRINT_I1_I5.md`](../proposals/PROPOSAL_INTEGRATION_SPRINT_I1_I5.md) land record).

---

## Context

After completing Sprints 1–3 of the Bayesian kernel (ADRs 0012–0014), an architectural
audit was performed comparing the state of all three active teams:

- **Claude** — Bayesian kernel (weight inference, Weight Authority Stack, temporal decay,
  posterior predictive check)
- **Antigravity** — Narrative persistence (NarrativeArcs, identity EMA, semantic embeddings,
  Immortality protocol)
- **Cursor** — Perception hardening (LLM degradation policies, TemporalContext, LimbicProfile,
  PerceptionCoercionReport)

The audit confirmed that **the three teams are architecturally complementary**:

```
Cursor → signals → Claude (decide) → KernelDecision → Antigravity (archive)
```

No team touches `hypothesis_weights` except Claude. No merge conflicts exist on the core
Bayesian logic. However, **five interlayer gaps** were identified that prevent the teams
from operating together effectively.

---

## Decision

Pause P6 (codepath unification) and deliver a focused **Integration Sprint** that closes
the five gaps before any structural refactoring. This sprint is owned by the Claude team
but the interfaces it defines are **contracts for all three teams**.

---

## Integration Items

### I1 — `weights_snapshot` in `NarrativeEpisode`
**Gap:** `applied_mixture_weights` (added in Sprint 1, P1) is captured in `KernelDecision`
but never persisted in `NarrativeEpisode`. Antigravity now stores episodes in SQLite with
`significance`, `arc_id`, and `semantic_embedding`. Without the weights used at decision
time, post-hoc audit of why a past decision leaned a certain way is impossible.

**Fix:** Add `weights_snapshot: tuple[float,float,float] | None` to `NarrativeEpisode`
and pass it from `KernelDecision.applied_mixture_weights` in `kernel.py::memory.register()`.

**Interface contract for Antigravity:** The field is optional (None for legacy episodes).
Schema migration in `narrative_storage.py` should add the column with `DEFAULT NULL`.

---

### I2 — `EVENT_KERNEL_WEIGHTS_UPDATED` on the event bus
**Gap:** `kernel_event_bus.py` emits only `EVENT_KERNEL_DECISION` and
`EVENT_KERNEL_EPISODE_REGISTERED`. Changes to `hypothesis_weights` (from feedback
posterior, episodic nudge, hierarchical update) are invisible to external observers
(telemetry, monitoring, future DAO hooks).

**Fix:** Add `EVENT_KERNEL_WEIGHTS_UPDATED` constant and emit it from
`weight_authority.compose_mixture_weights()` when a blend actually changes the weights.

**Interface contract for all teams:** Event payload is
`{"prior": [f,f,f], "posterior": [f,f,f], "trust": float, "source": str}`.

---

### I3 — `perception_uncertainty` from Cursor into Bayesian signals
**Gap:** Cursor's `PerceptionCoercionReport.uncertainty()` computes a composite distrust
score [0,1] based on JSON parse failures, LLM degradation, dual-vote discrepancies. This
number is never passed to `WeightedEthicsScorer.evaluate()`. A degraded perception should
make the kernel more cautious, but currently does not.

**Fix:** Inject `signals["perception_uncertainty"]` from `PerceptionCoercionReport` in
`kernel.py` before `bayesian.evaluate()`. The scorer's `_ethical_hypothesis_valuations()`
will naturally reduce confidence when perception_uncertainty is high (it uses
`signals.get("uncertainty", 0)` implicitly).

**Interface contract for Cursor:** `PerceptionCoercionReport` must expose
`.uncertainty() -> float` (already exists). `PerceptionStageResult` should carry
`coercion_report: PerceptionCoercionReport | None` (to be added by Cursor if not present).

---

### I4 — `KERNEL_NARRATIVE_IDENTITY_POLICY` — identity leans → poles pre-argmax
**Gap:** Antigravity maintains `NarrativeIdentityState` with `civic_lean`, `care_lean`,
`deliberation_lean`, `careful_lean` (EMA over past decisions). These leans are exactly
the kind of persistent self-model that should inform `pre_argmax_pole_weights` in the
Bayesian scorer — but no connection exists.

**Fix:** Add `KERNEL_NARRATIVE_IDENTITY_POLICY` env var with values:
- `off` (default) — no change to current behavior
- `pole_pre_argmax` — map identity leans to pole weights and inject as
  `bayesian.pre_argmax_pole_weights` before `evaluate()`

Mapping (Claude-owned):
```
civic_lean     → compassionate pole weight
careful_lean   → conservative pole weight
deliberation_lean → virtue/optimistic weight (blended)
```

**Interface contract for Antigravity:** `NarrativeMemory` must expose
`identity_state() -> NarrativeIdentityState` (or equivalent accessor).

---

### I5 — `KERNEL_TEMPORAL_ETA_MODULATION` — eta_seconds → urgency signal
**Gap:** Cursor's `TemporalContext` carries `eta_seconds` (estimated task completion time)
and `battery_horizon_state` ("critical", "low_horizon", "nominal"). Time pressure and
battery criticality should logically increase `signals["urgency"]`, affecting how the
Bayesian scorer evaluates risk-taking vs. caution — but this link does not exist.

**Fix:** Add `KERNEL_TEMPORAL_ETA_MODULATION` env var (default `off`). When enabled:
```
urgency_boost = clamp(reference_eta / max(eta_seconds, 1.0), 0.0, 1.0)
if battery_horizon_state == "critical":
    urgency_boost = min(urgency_boost + 0.3, 1.0)
signals["urgency"] = clamp(signals["urgency"] + urgency_boost * 0.4, 0.0, 1.0)
```

**Interface contract for Cursor:** `TemporalContext` must be accessible from
`PerceptionStageResult.temporal_context` before `bayesian.evaluate()` is called.

---

## What This ADR Does NOT Change

- `hypothesis_weights` update logic (Weight Authority Stack, ADR 0015 weight_authority.py)
- Bayesian scoring (`WeightedEthicsScorer.evaluate()`)
- AbsoluteEvil check (always first, before any of these integrations run)
- Narrative persistence schema (Antigravity owns this; we only add a field)
- LLM degradation policies (Cursor owns this; we only read `coercion_report`)

---

## Consequences

After this sprint:

1. Antigravity can persist `weights_snapshot` per episode and run post-hoc analysis
   ("did high utilitarian weight correlate with better outcomes in arc X?")
2. Cursor's perception quality directly modulates Bayesian caution
3. The event bus becomes a real observability backbone
4. Identity leans can optionally shape decision style (opt-in)
5. Time pressure can optionally sharpen urgency (opt-in)

P6 (codepath unification) is deferred until after this sprint is merged to `main`.

---

## Team Coordination Notes

**For Antigravity:**
- Add `weights_snapshot` column to SQLite schema (nullable, default NULL)
- Expose `NarrativeMemory.identity_state()` accessor for I4

**For Cursor:**
- Confirm `PerceptionCoercionReport.uncertainty()` is stable API
- Expose `PerceptionStageResult.coercion_report` if not already present
- Confirm `TemporalContext` is available before `kernel.process()` calls `bayesian.evaluate()`

**For Claude:**
- Original plan: implement in `master-claude`; **as of April 2026** the sprint is merged on integration hubs — see proposal land record.
- All new env vars default to backward-compatible values (off/None)
- PRs to `main` should be coordinated after all three teams have reviewed
