# Hemisphere Kernel Refactor — Copilot Analysis & Proposal

**Author:** Team Copilot (GitHub Copilot Agent)  
**Date:** 2026-04-16  
**Status:** Proposal / Discussion — awaiting L0/L1 directive  
**Related:**
- [`PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md`](PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md) — P1 risk: single-orchestrator complexity
- [`CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md`](CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md) — Bayesian architecture seam (BI-P1-01)
- [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) — architecture debt reduction
- [`src/kernel.py`](../../src/kernel.py) — God Object under analysis (3 424 lines)

---

## 1. Context and motivation

The document `CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md` was referenced in a cross-team
discussion but did not yet exist in the repository. This file materialises the analysis
requested of Team Copilot and registers it as a formal discussion artifact.

The discussion was triggered by the observation that `src/kernel.py` has grown to
**3 424 lines** with a single `EthicalKernel` class carrying four orthogonal
responsibilities simultaneously. `PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md`
already flags this as **P1 risk**:

> *"Single-orchestrator complexity remains high — `src/kernel.py` carries extensive
> responsibilities. Risk: cross-feature regressions and costly maintenance as feature
> count grows."*

---

## 2. Diagnosis: the four mixed responsibilities

| Layer | What it does | Representative code |
|-------|-------------|---------------------|
| **Hard ethical pipeline** | Blocks, evaluates, decides — has veto power | `AbsoluteEvil → Buffer → BayesianEngine → Poles → Will → EthicalReflection` |
| **Experiential context** | Informs but never vetoes | `Sympathetic → Somatic → PAD → Salience → NarrativeMemory` |
| **Chat I/O orchestration** | Adapts WebSocket I/O to the pipeline | `process_chat_turn` / `process_chat_turn_async` (~900 lines) |
| **Infrastructure** | Persists, observes, emits events | `DAO`, `EventBus`, `CheckpointPersistence` |

The `process()` method alone spans ~770 lines. `process_chat_turn` adds ~500 more.
`process_chat_turn_async` adds another ~400. These three methods account for ~1 670 lines
of the class — almost half its mass — and they interleave all four responsibilities.

---

## 3. The hemispheric metaphor: why it fits here

Neurological lateralisation is not strict — both hemispheres collaborate continuously.
The ethical android has the same natural duality:

**Left hemisphere — Ethical (analytical / decisory)**

- Executes the non-negotiable pipeline
- `AbsoluteEvilDetector → PreloadedBuffer → BayesianEngine → EthicalPoles →
  SigmoidWill → EthicalReflection`
- **Has veto power.** Its `KernelDecision` is never overridden by the experiential side
- Completely testable without LLM, emotions, or narrative

**Right hemisphere — Experiential (contextual / informative)**

- Prepares the context that enriches deliberation
- `UchiSotoModule → SympatheticModule → SomaticMarkerStore → PADArchetypeEngine →
  SalienceMap → NarrativeMemory → WeaknessPole → AlgorithmicForgiveness`
- **Only informs.** Produces a typed `HemisphericContext` that the ethical hemisphere
  may consult — never a decision
- It is the *"how it feels"*; the ethical hemisphere is *"what is right"*

---

## 4. Proposed architecture

```
          ┌──────────────────────────────────────────┐
          │       EthicalKernel  (public façade)       │
          │  Public API preserved unchanged             │
          └──────────────┬──────────────┬─────────────┘
                         │              │
          ┌──────────────▼──┐    ┌──────▼──────────────────┐
          │ EthicalHemisphere│◄───│  ExperientialHemisphere  │
          │  (hard pipeline) │    │  (context + affect)      │
          │                  │    │                          │
          │ - AbsoluteEvil   │    │ - UchiSoto               │
          │ - Buffer         │    │ - Sympathetic            │
          │ - BayesianEngine │    │ - SomaticMarkerStore     │
          │ - EthicalPoles   │    │ - PADArchetypeEngine     │
          │ - SigmoidWill    │    │ - SalienceMap            │
          │ - EthicalReflect.│    │ - NarrativeMemory        │
          └──────────────────┘    │ - WeaknessPole           │
                   ▲              │ - AlgorithmicForgiveness  │
                   │              └──────────────────────────┘
          HemisphericContext        (typed interhemispheric
            (typed contract)          transfer object)
```

**Tick flow:**

```
1. ExperientialHemisphere.pre_tick(signals, sensor_snapshot)
       → produces: HemisphericContext(affect, social_eval, somatic_state,
                                      salience_weights, narrative_hint, ...)

2. EthicalHemisphere.decide(actions, context, hemi_ctx: HemisphericContext)
       → produces: KernelDecision   ← SOLE PLACE WITH VETO POWER

3. ExperientialHemisphere.post_tick(decision, episode)
       → updates: episodic memory, algorithmic forgiveness, DAO hooks
```

**Key contract constraint:** `HemisphericContext` must be `@dataclass(frozen=True)`.
Once produced by the experiential hemisphere it is immutable — the ethical hemisphere
reads it but cannot retroactively change what the experiential side computed.

---

## 5. Risk analysis

| Risk | Level | Mitigation |
|------|-------|------------|
| **State entanglement** — ~8 places in `process()` where somatic/PAD/sympathetic modify signals later consumed by bayesian | High | `HemisphericContext` frozen dataclass; all mutations happen in `pre_tick`, the frozen object crosses the boundary |
| **KernelComponentOverrides compatibility** — current injection API points directly at `EthicalKernel` fields | High | The façade delegates to hemispheres; `KernelComponentOverrides` continues working via an internal split inside the façade (no external API change) |
| **Transfer overhead** — constructing `HemisphericContext` on every tick | Medium | In-process object passing, zero serialisation; benchmark delta expected < 1 % |
| **`process_chat_turn` is a third entity** — it is an I/O adapter, not a hemisphere | Medium | Extract `ChatAdapter` explicitly; thin wrapper that prepares inputs and calls the two-hemisphere cycle |
| **Regression surface** — 3 400 lines, 100+ tests | Critical | Phased migration; tests must be green after each phase; Phase 0 adds zero logic changes |

---

## 6. Connection to active team work

The hemispheric refactor is the **architectural container** that makes existing roadmap
items coherent:

| Existing item | Lives in | Why the split helps |
|--------------|----------|---------------------|
| **BI-P1-01** Bayesian inference engine seam (Claude Playbook) | `EthicalHemisphere` | The seam is its internal API — clean boundary, no narrative noise |
| **BI-P1-02** Likelihood evidence profile matrix | `ExperientialHemisphere` → `HemisphericContext.evidence_profile` | Evidence profile is a natural experiential output fed to the posterior |
| **BI-P2-01** Bayesian observability contract | Hemisphere boundary | Natural telemetry emission point without polluting ethical logic |
| **Input trust #2** (CRITIQUE_ROADMAP_ISSUES #2) | `EthicalHemisphere` pre-gate | MalAbs hardening has a single, clear home |
| **Unified degradation** | `ExperientialHemisphere` degradation callbacks | Degradation path is isolated from veto logic |

Without the split, the Bayesian playbook adds more code to a 3 400-line God Object.
With the split, every new capability has an unambiguous home.

---

## 7. Phased migration (no big-bang, no regressions)

### Phase 0 — Contracts only (zero logic change, zero risk)

- Create `src/hemisphere_context.py`: `@dataclass(frozen=True) HemisphericContext`
  with typed fields mirroring what `process()` currently assembles ad-hoc
- Create this document
- `pytest tests/` must be green with no changes to existing logic

### Phase 1 — Extract ExperientialHemisphere

- Create `src/experiential_hemisphere.py` with `ExperientialHemisphere`
- Move: `Sympathetic`, `UchiSoto`, `PADArchetypeEngine`, `SalienceMap`,
  `NarrativeMemory`, `WeaknessPole`, `AlgorithmicForgiveness`
- `EthicalKernel.process()` delegates to `.pre_tick()` and `.post_tick()`
- `KernelComponentOverrides` preserved via façade internal split
- **Acceptance:** `pytest tests/` green; PR net diff < 400 lines

### Phase 2 — Extract EthicalHemisphere

- Create `src/ethical_hemisphere.py` with `EthicalHemisphere`
- Move: `AbsoluteEvilDetector`, `PreloadedBuffer`, `BayesianEngine`, `EthicalPoles`,
  `SigmoidWill`, `EthicalReflection`
- `EthicalKernel` becomes a façade of ~200 lines
- **Acceptance:** identical public interface; invariant test suite green; same decisions

### Phase 3 — ChatAdapter and process_natural

- Extract `ChatAdapter` from `process_chat_turn` / `process_chat_turn_async` (~900 lines)
- `process_natural` becomes a thin wrapper
- **Acceptance:** chat latency benchmark within ±5 % of baseline

---

## 8. Honest critique of the hemispheric metaphor itself

The metaphor is useful but has limits that should not be oversold:

1. **It is not a neuroscience claim.** The android does not have two physically separate
   compute paths. The split is a software engineering boundary, not a consciousness claim.

2. **The boundary will have seams.** `UserModelTracker`, `MotivationEngine`,
   `EpistemicHumility`, and `MetacognitionEvaluator` do not map cleanly to either
   hemisphere. A pragmatic third category — `KernelServices` (cross-cutting) — may be
   needed to avoid forced categorisation.

3. **The frozen context constraint is load-bearing.** If `HemisphericContext` ever
   becomes mutable, the ethical hemisphere loses its guarantee that context was not
   modified after pre-tick. This must be enforced by type (frozen dataclass or
   `__slots__` + property-only) not by convention.

4. **Phase 0 is the hardest political step, not the easiest.** Agreeing on what fields
   belong in `HemisphericContext` means explicitly deciding what is "context" (informs)
   vs. "veto input" (decides). This taxonomy discussion may reveal disagreements between
   teams that are currently hidden inside 3 400 lines.

---

## 9. Recommendation

**Immediate (Phase 0, Team Copilot):**  
Land this document. Propose `HemisphericContext` field taxonomy in a follow-up PR
and request explicit L1 (Antigravity) review before any code moves.

**Before Phase 1:**  
L1 (Antigravity) must sign off on the hemisphere boundary — specifically which
modules land on which side and what `KernelServices` contains. Without this,
Phase 1 risks becoming a large refactor without shared understanding.

**Not recommended:**  
A single PR that does Phases 1–3 together. The regression surface is too large and the
political cost of a rollback too high.

---

*Registered by Team Copilot, 2026-04-16. Awaiting L0/L1 directive before opening
any code-change PR.*
