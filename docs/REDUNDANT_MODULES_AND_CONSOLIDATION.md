# Redundant modules and consolidation roadmap

**Status:** ADR 0016 Axis C2 (April 2026) — identify overlaps and propose consolidation strategy

This document flags modules with **functional overlap** or **diminishing returns** — candidates for consolidation, deprecation, or merger in future releases. None of these modules are **blocked** yet; all remain active and tested.

---

## Identified overlaps

### 1. Affect/emotional state family (HIGH REDUNDANCY)

These three modules re-describe the same "affect space" with partial overlap:

| Module | Scope | Function | Tier | Note |
|--------|-------|----------|------|------|
| `SomaticMarkerStore` | Bodily markers (tension, fatigue, warmth) | Store visceral states for narrative context | narrative_layer | **Deprecated v0.3.0**; no causal effect on `final_action` |
| `PADArchetypeEngine` | Pleasure/Arousal/Dominance 3D space | Project multi-pole scores → affect archetypes | narrative_layer | Core narrative module; used for LLM tone |
| `AffectiveHomeostasis` | Equilibrium of affect (valence, arousal) | Homeostatic feedback loop for body state | narrative_layer | Modulates PAD; drives recovery narratives |

**Consolidation proposal (post-field-tests):**
- Keep **PADArchetypeEngine** as primary affect model (well-used, tested).
- Merge **AffectiveHomeostasis** logic into PAD or somatic_markers.
- **Remove SomaticMarkerStore** (deprecated; purely narrative).
- Single `__affect_state__` dataclass unifies storage.

**Impact:** ~200 LOC reduction; no change to `final_action`.

---

### 2. Narrative identity & self-reflection family (MEDIUM REDUNDANCY)

Two modules attempt to model "who is the agent, how does it see itself":

| Module | Scope | Function | Tier | Note |
|--------|-------|----------|------|------|
| `NarrativeIdentity` | Autobiographical identity construction | Build identity narrative from episodes | narrative_layer | Tracks self-concept, values persistence |
| `IdentityReflection` | Self-directed reflection on identity | Reflect on own moral judgments + growth | narrative_layer | Post-episode reflection; asks "who am I?" |
| `IdentityIntegrity` | Coherence pruning of identity statements | Prune contradictions in self-description | narrative_layer | Ensures narrative consistency |

**Overlap:** `NarrativeIdentity` + `IdentityReflection` both answer "who am I?" — one builds it, one critiques it. Could be unified.

**Consolidation proposal (post-field-tests):**
- Merge `IdentityReflection` into `NarrativeIdentity` as a reflection method.
- Keep `IdentityIntegrity` as a separate coherence filter.
- Result: single `IdentityModel` with build + reflect + prune stages.

**Impact:** ~150 LOC reduction; narrative only.

---

### 3. Ethical reflection & metacognition (MEDIUM REDUNDANCY)

Two modules engage in post-decision reasoning about morality and capability:

| Module | Scope | Function | Tier | Note |
|--------|-------|----------|------|------|
| `EthicalReflection` | Post-decision moral self-assessment | Explain choice to self; learn from past | narrative_layer | Reflects on whether we chose well |
| `MetacognitiveEvaluator` | Self-doubt & epistemic assessment | Evaluate own knowledge limits & confidence | narrative_layer | Advises on when to seek clarification |

**Overlap:** Both answer "How confident am I in my reasoning?" — one focuses on morality, one on epistemic soundness.

**Consolidation proposal (post-field-tests):**
- Merge into unified `ReflectionModule` with moral + epistemic dimensions.
- Separate concerns (morality vs. knowledge) as sub-methods, not separate modules.

**Impact:** ~100 LOC reduction; purely advisory (narrative-layer).

---

### 4. Sympathetic module & weak adjacencies (LOW REDUNDANCY, UNCLEAR SIGNAL)

`SympatheticModule` is a catch-all for "what do we care about in this context?" — adjacent to:

| Module | Commonality | Distinction |
|--------|-------------|-------------|
| `DriveArbiter` | Both ask "what matters now?" | DriveArbiter selects among 5 drives; Sympathetic evaluates care/empathy contextually |
| `Locus` | Both assess relational stance | Locus is self-location; Sympathetic is other-orientation |
| `UchiSoto` | Both model relationship dynamics | UchiSoto is trust+forget; Sympathetic is present concern |

**Assessment:** No immediate consolidation; `SympatheticModule` is narrow enough to justify separation.  
**Future:** Monitor for bloat if new empathy logic gets added.

---

### 5. Experience digest / Psi Sleep (LOW REDUNDANCY)

`ExperienceDigest` (used by `PsiSleep`) summarizes episodes into a counterfactual replay state.

| Module | Role | Note |
|--------|------|------|
| `PsiSleep` | Sleep learning + counterfactual update | Runs offline; optional Bayesian feedback |
| `ExperienceDigest` | Summary of episode for sleep input | Extracted from narrative memory |

**Assessment:** Clean separation (digest ← memory, sleep ← digest). No consolidation needed.

---

## Deprecation & consolidation roadmap

| Group | Tier | Status | Action | Timeline |
|-------|------|--------|--------|----------|
| Affect family (SomaticMarkers, PAD, Homeostasis) | narrative_layer | 🔴 HIGH redundancy | Consolidate after F0 field tests | v0.3.0 (Q3 2026) |
| Identity family (NarrativeIdentity, IdentityReflection, IdentityIntegrity) | narrative_layer | 🟡 MEDIUM redundancy | Merge into unified IdentityModel | v0.4.0 (Q3 2026) |
| Reflection family (EthicalReflection, Metacognition) | narrative_layer | 🟡 MEDIUM redundancy | Merge into ReflectionModule | v0.4.0 (Q3 2026) |
| Sympathetic module | narrative_layer | 🟢 OK | Monitor for scope creep | Review Q4 2026 |
| Sleep family (PsiSleep, ExperienceDigest) | narrative_layer | 🟢 OK | No action | — |

---

## Non-causal impact guarantee

**Key property:** All modules flagged for consolidation are **narrative-tier only** (do not affect `final_action`).

- Consolidating or removing them does **not** change decision outcomes.
- Decision-core modules (`AbsoluteEvilDetector`, `WeightedEthicsScorer`, poles, etc.) are **not** flagged.
- This was verified via `test_narrative_tier_is_non_causal.py` (10 tests, all passing).

---

## Testing & migration strategy

For each consolidation:

1. **Unit tests:** Keep existing tests; add new consolidated-module tests.
2. **Integration:** Run `tests/integration/test_cross_tier_decisions.py` — verify `final_action` is invariant.
3. **Narrative tests:** Run `tests/test_narrative_tier_is_non_causal.py` — verify non-causal property holds.
4. **Regression:** Full pytest suite must pass before merging.

---

## See also

- [ETHICAL_TIER_MAP.md](ETHICAL_TIER_MAP.md) — module tier classification
- [WEAKNESSES_AND_BOTTLENECKS.md](WEAKNESSES_AND_BOTTLENECKS.md) — architectural debt context
- [PROPOSAL_CONSOLIDATION_PRE_DAO.md](proposals/PROPOSAL_CONSOLIDATION_PRE_DAO.md) — consolidation rationale (Axis C2)
- `tests/test_narrative_tier_is_non_causal.py` — non-causal verification

---

## Bloque 32.3 — tracking (no merges executed)

Consolidation items above remain **deferred** until after field tests. Progress on *decoupling* without deleting narrative modules:

- **Runtime / chat:** `lifespan` is owned by `src/runtime/chat_lifecycle.py` (`chat_lifespan`); `src/runtime/chat_server.py` exposes a stable `app` alias for `uvicorn` while routes stay in `src/chat_server.py` until a full split is scheduled.

---

*Last updated: ADR 0016 C2, April 2026. Next review: after F0 field tests.*
