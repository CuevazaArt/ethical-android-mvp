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

## 9. Three-hemisphere variant — preferred architecture

> *L0 question (2026-04-16): "¿Podrían 3 hemisferios ser incluso mejores?"*

**Answer: yes.** The kernel already contains three implicit functional clusters
that map poorly to a bipartite split. Forcing the third cluster into either of
the other two is technical debt from day one.

### 9.1 The three implicit clusters in `EthicalKernel.__init__`

| Hemisphere | Role | Modules (from actual `__init__`) | Key property |
|-----------|------|----------------------------------|-------------|
| **Ethical** (analytical / decisory) | Evaluates, vetoes, decides | `absolute_evil`, `buffer`, `bayesian`, `poles`, `will`, `ethical_reflection` | **Has veto power.** Its `KernelDecision` is final and non-negotiable. |
| **Experiential** (contextual / affective) | Feels, contextualises, informs | `sympathetic`, `uchi_soto`, `pad_archetypes`, `salience_map`, `somatic_store`, `memory`, `weakness`, `forgiveness` | **Only informs.** Produces context the ethical hemisphere may consult but never overrides. |
| **Metacognitive** (self-observation / calibration) | Observes itself, models the other, plans | `metacognition`, `user_model`, `motivation`, `skill_learning`, `metaplan`, `strategist`, `subjective_clock`, `feedback_ledger`, `biographic_pruner` | **Neither vetoes nor feels: calibrates.** Adjusts internal parameters without producing decisions or emotions. |

### 9.2 Why 3 > 2 for this specific codebase

1. **Resolves the orphan problem.** With 2 hemispheres, metacognitive modules
   (`MetacognitiveEvaluator`, `UserModelTracker`, `MotivationEngine`,
   `ExecutiveStrategist`, `SubjectiveClock`, `SkillLearningRegistry`,
   `MetaplanRegistry`, `BiographicPruner`, `FeedbackCalibrationLedger`) are homeless.
   They are not ethical (they don't veto), not experiential (they don't feel).
   They are *observers of the system that adjust the system*. Forcing them into
   either hemisphere breaks the contract coherence.

2. **Maps to an established cognitive distinction.** In cognitive science the
   tripartite model is well-known:
   - **System 1** (fast, emotional) → Experiential hemisphere
   - **System 2** (deliberative, normative) → Ethical hemisphere
   - **Metacognition** (monitoring + control over the other two) → Third hemisphere

   The kernel already has this implicitly — `MetacognitiveEvaluator` is literally
   named after the concept.

3. **Cleaner contracts.** With 3 hemispheres, the tick flow gains precision:

```
1. ExperientialHemisphere.pre_tick(signals, sensors)
       → HemisphericContext(affect, social_eval, somatic, salience, narrative)

2. MetacognitiveHemisphere.calibrate(hemi_ctx, history)
       → CalibrationContext(user_model_update, motivation_vector,
                            epistemic_confidence, time_pressure,
                            strategy_hint, skill_priors)

3. EthicalHemisphere.decide(actions, context, hemi_ctx, cal_ctx)
       → KernelDecision   ← SOLE PLACE WITH VETO POWER

4. MetacognitiveHemisphere.post_tick(decision, episode)
       → updates: user_model, skill_learning, metaplan,
         subjective_clock, bayesian feedback ledger

5. ExperientialHemisphere.post_tick(decision, episode)
       → updates: episodic memory, somatic markers,
         algorithmic forgiveness, DAO hooks
```

   Note: the metacognitive hemisphere intervenes **twice** (before and after the
   decision), reflecting exactly what a real metacognitive system does: prepares
   parameters *before* and learns *after*.

### 9.3 Architecture diagram (3 hemispheres)

```
          ┌──────────────────────────────────────────────────────┐
          │            EthicalKernel  (public façade)             │
          │         Public API preserved unchanged                │
          └──────────┬──────────────┬──────────────┬─────────────┘
                     │              │              │
          ┌──────────▼──┐   ┌──────▼──────┐  ┌───▼──────────────────┐
          │  Experiential │   │ Metacognitive│  │   Ethical            │
          │  Hemisphere   │   │ Hemisphere   │  │   Hemisphere         │
          │               │   │              │  │                      │
          │ - UchiSoto    │   │ - Metacogn.  │  │ - AbsoluteEvil       │
          │ - Sympathetic │   │ - UserModel  │  │ - Buffer             │
          │ - Somatic     │   │ - Motivation │  │ - BayesianEngine     │
          │ - PAD         │   │ - SkillLearn │  │ - EthicalPoles       │
          │ - Salience    │   │ - Metaplan   │  │ - SigmoidWill        │
          │ - Memory      │   │ - Strategist │  │ - EthicalReflection  │
          │ - Weakness    │   │ - SubjClock  │  │                      │
          │ - Forgiveness │   │ - FeedbackLe │  │  ← SOLE VETO HOLDER │
          │               │   │ - BiogrPrune │  │                      │
          └───────┬───────┘   └──────┬───────┘  └──────────────────────┘
                  │                  │                     ▲
                  ▼                  ▼                     │
          HemisphericContext   CalibrationContext     KernelDecision
            (frozen)             (frozen)              (output)
```

### 9.4 Transfer objects

| Object | Source | Consumer | Mutability |
|--------|--------|----------|-----------|
| `HemisphericContext` | Experiential `.pre_tick()` | Ethical `.decide()` + Metacognitive `.calibrate()` | `@dataclass(frozen=True)` — load-bearing |
| `CalibrationContext` | Metacognitive `.calibrate()` | Ethical `.decide()` | `@dataclass(frozen=True)` — load-bearing |
| `KernelDecision` | Ethical `.decide()` | Metacognitive `.post_tick()` + Experiential `.post_tick()` | Existing immutable contract |

### 9.5 Comparative analysis: 2 vs 3 hemispheres

| Aspect | 2 hemispheres | 3 hemispheres |
|--------|--------------|---------------|
| Migration simplicity | Easier (fewer interfaces) | More complex (3 contracts) |
| Module placement ambiguity | Medium (~9 orphan modules) | Low (nearly all modules have a natural home) |
| Conceptual overhead | Low | Medium |
| Fidelity to actual kernel code | ~75% — forces classifications | ~95% — each module has a home |
| Number of transfer objects | 1 (`HemisphericContext`) | 2 (`HemisphericContext` + `CalibrationContext`) |
| Cognitive science alignment | Partial (System 1/2 only) | Full (System 1 + System 2 + Metacognition) |

### 9.6 Updated phased migration (3-hemisphere variant)

- **Phase 0** — 3 contracts (`HemisphericContext`, `CalibrationContext`,
  `KernelDecision` already exists) + this document. Zero logic change.
- **Phase 1** — Extract `ExperientialHemisphere` (affective modules).
- **Phase 1.5** — Extract `MetacognitiveHemisphere` (self-observation modules).
- **Phase 2** — Extract `EthicalHemisphere` (veto pipeline); kernel becomes
  ~200-line façade.
- **Phase 3** — Extract `ChatAdapter` from `process_chat_turn` /
  `process_chat_turn_async`.

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
