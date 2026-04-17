# Integration proposal: non-redundant contributions (v6 aligned with the repo)

> **Type:** v6 kernel evolution design; **status:** Phases 1–5 reflected in code (detail in each section).  
> **Related:** [EMERGENT_CONSCIOUSNESS_V6.md](EMERGENT_CONSCIOUSNESS_V6.md) (philosophical framework and redundancies), [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) (current technical contract).

## Objective

Incorporate only what **adds new measurable state** or **bounded proactive behavior**, without duplicating poles, PAD, σ, episodic narrative, or Psi Sleep/DAO as they already exist.

**Principles:**

1. **MalAbs and buffer** remain anchors; no phase modifies them in production.
2. **Nothing new** on the ethical veto critical path without non-regression tests.
3. Each phase = **bounded increment** + **falsifiable criteria** (simulation metrics or logs).

---

## Where we are today (model inventory, 2026)

### Orchestration layer

| Piece | File | Role |
|-------|---------|-----|
| Decision cycle | `src/kernel.py` | Chains modules; `KernelDecision`, `ChatTurnResult`; `process_chat_turn()` (chat + STM); `register_episode` on light turns. |
| Async bridge | `src/real_time_bridge.py` | Worker-thread offload (`run_in_threadpool` or optional `ThreadPoolExecutor`); optional `KERNEL_CHAT_TURN_TIMEOUT` — [ADR 0002](../adr/0002-async-orchestration-future.md). |
| WS server | `src/chat_server.py` | FastAPI `/ws/chat`, one kernel per connection. |

### Main `process()` flow (actual order in code)

1. **Uchi-Soto** — trust / dialectic from signals + `message_content`.  
2. **Sympathetic** — σ, energy mode.  
3. **Locus** — causal attribution (α, β, dominant).  
4. **MalAbs** — hard filter on candidate **actions**.  
5. **Buffer** — principles activated by context.  
6. **Bayes** — expected action choice.  
7. **Poles** — `TripartiteMoral` (scores, verdict, multipolar narrative).  
8. **Sigmoid will** — D_fast / gray_zone / etc. mode.  
9. **PAD + archetypes** — post-decision affective projection; does not govern veto.  
10. **Narrative memory** — episode (with `affect_pad` / `affect_weights` if applicable); **`NarrativeIdentityTracker`** updates self-state only when registering episode (`src/modules/narrative_identity.py`).  
11. **Weakness** — emotional load / weak episode logging.  
12. **Algorithmic forgiveness** — per-episode logging.  
13. **DAO** — auditing; solidarity alerts if risk is high.

**Outside the per-tick cycle:** `execute_sleep()` (Psi Sleep + forgiveness + weakness load + immortality + **`DriveArbiter.evaluate`**). `process_natural` adds LLM perceive → cycle → communicate → narrate. Structured monologue in logs via `compose_monologue_line` (`src/modules/internal_monologue.py`).

### Modules by folder (`src/modules/`)

| Module | File | Summary role |
|--------|---------|-------------------|
| MalAbs | `absolute_evil.py` | Action veto + conservative `evaluate_chat_text()`. |
| Constitution | `buffer.py` | Preloaded principles by context. |
| Impact | `weighted_ethics_scorer.py` | Expectations over actions; pruning (mixture; not full Bayes). |
| Poles | `ethical_poles.py` | Dynamic multipolar → `TripartiteMoral`. |
| Will | `sigmoid_will.py` | Decision mode from impact/uncertainty. |
| Body | `sympathetic.py` | σ, energy, sympathetic/parasympathetic mode. |
| Long memory | `narrative.py` | Episodes, morals, σ, optional PAD on episode. |
| Social | `uchi_soto.py` | Trust circles. |
| Attribution | `locus.py` | Locus of control. |
| Night | `psi_sleep.py` | Audit, loose recalibrations. |
| Governance | `mock_dao.py` | Voting, audits, alerts. |
| Noise | `variability.py` | Controlled variability (optional). |
| Language | `llm_layer.py` | Perception, communication, rich narrative. |
| Humanization | `weakness_pole.py` | Narrative imperfection without changing decision. |
| Forgiveness | `forgiveness.py` | Decay of negative memories. |
| Backup | `immortality.py` | Distributed backup. |
| Augenesis | `augenesis.py` | Synthetic “soul” profiles. |
| Affect | `pad_archetypes.py` | PAD + softmax over prototypes. |
| STM | `working_memory.py` | Short dialogue turns. |
| Drives (post-sleep) | `drive_arbiter.py` | Discrete advisory intents after backup. |
| Narrative identity | `narrative_identity.py` | EMA over episodes; LLM context + JSON chat. |
| Monologue | `internal_monologue.py` | One `[MONO]` line for logs / API. |

### Simulations and tests

| Area | Location |
|------|-----------|
| Scenarios 1–9 | `src/simulations/runner.py`, `src/main.py` |
| Ethical properties + chat + server | `tests/` |

### What **already covers** much of the “functional consciousness” vocabulary without the four new bridges

- **Decision tension:** poles + Bayesian uncertainty + will mode.  
- **Body / alert:** σ, Uchi-Soto.  
- **Tone / affect:** post-decision PAD.  
- **History:** episodes + Psi Sleep.  
- **Dialogue:** `WorkingMemory` + chat + WebSocket.  

**Covered in repo v6:** second-order reflection (**Phase 1**), salience (**Phase 2**), advisory drives (**Phase 3**), narrative self (**Phase 4**), compact monologue (**Phase 5**). What remains **out of scope** by default is operational ethics self-modification (see excluded section).

---

## Integration proposal (adapted to this repo)

### Phase 1 — `EthicalReflection` (minimal metacognition) — **implemented**

**What:** pure module `src/modules/ethical_reflection.py` that, given `TripartiteMoral` + `BayesianResult` + `SigmoidWill.decide` output, produces a **`ReflectionSnapshot`**:

- `pole_spread` = max(score) − min(score) per pole,  
- `conflict_level` ∈ {`low`, `medium`, `high`} (thresholds in `EthicalReflection.LOW_MAX` / `MEDIUM_MAX`),  
- `strain_index` ∈ [0, 1] = `(spread/2) * (0.5 + uncertainty)`,  
- brief `note` for logs / API.

**Where:** in `EthicalKernel.process`, after final mode and action choice, **before** PAD; field `KernelDecision.reflection`. Exposed in `format_decision` and `chat_server` JSON. `reflection_to_llm_context()` feeds `LLMModule.communicate(..., reflection_context=...)` in `process_natural` and `process_chat_turn`.

**Use:** explainability, telemetry, and voice nuance (without changing decision). **Does not** modify action or MalAbs.

**Success criterion:** tests in `tests/test_ethical_reflection.py`; ethical regression intact (same action with or without reflection — reflection is read-only).

---

### Phase 2 — `SalienceMap` (GWT-lite, read-only) — **implemented**

**What:** `src/modules/salience_map.py` — `SalienceSnapshot` with normalized `weights` on four axes (`risk`, `social`, `body`, `ethical_conflict`), `dominant_focus`, `raw_scores`. `social` combines hostility, `caution_level`, and dialectic; `body` uses σ; `ethical_conflict` uses `reflection.strain_index`.

**Where:** after `EthicalReflection`, before PAD; field `KernelDecision.salience`. `salience_to_llm_context()` → `communicate(..., salience_context=...)`. JSON in `chat_server`; block in `format_decision`.

**Evolutionary:** weight locus/Bayes (±ε) only with regression battery — **not** done yet.

---

### Phase 3 — `DriveArbiter` (bounded teleology) — **implemented**

**What:** `src/modules/drive_arbiter.py`. Evaluation **after** Psi Sleep and immortality (`EthicalKernel.execute_sleep`); also exposed in WebSocket JSON as `drive_intents` (advisory view each turn). Emits up to four `DriveIntent` with `suggest`, `reason`, `priority`.

**Does not** execute physical actions without policy/DAO layer; **does not** invent MalAbs-fragile actions.

**Criterion:** traceability; bounded list ordered by priority.

---

### Phase 4 — `NarrativeIdentity` (persistent self) — **implemented**

**What:** `NarrativeIdentityTracker` in `NarrativeMemory.identity`; `update_from_episode` only when registering episode. `ascription_line()` / `to_llm_context()` feed `LLMModule.communicate(..., identity_context=...)` and chat JSON (`identity` with leans + `ascription`).

**Does not** replace episodes; **does not** modify pole weights.

---

### Phase 5 — `InternalMonologue` (structured logging) — **implemented**

**What:** `compose_monologue_line(decision, episode_id)` in `internal_monologue.py` — compact `[MONO]` line for `format_decision` and `monologue` field in `chat_server` JSON when `KernelDecision` exists.

---

### Excluded from default roadmap

- **Operational ethics self-modification** (except MalAbs): lab only, reversibility, legal review — see [EMERGENT_CONSCIOUSNESS_V6.md](EMERGENT_CONSCIOUSNESS_V6.md).

---

## Suggested implementation order

1. Phase 1 (Reflection) — **done.**  
2. Phase 2 (Salience) — **done** (telemetry + LLM context).  
3. Phase 5 (structured monologue) — **done** (`format_decision` + JSON `monologue`).  
4. Phase 4 (Identity) — **done** (memory + LLM + JSON `identity`).  
5. Phase 3 (Drives) — **done** (post–Ψ Sleep + JSON `drive_intents` per turn).

---

## References

- Current contract: `docs/proposals/THEORY_AND_IMPLEMENTATION.md`  
- Affect: `docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` §7  
- Prior philosophical discussion: [EMERGENT_CONSCIOUSNESS_V6.md](EMERGENT_CONSCIOUSNESS_V6.md)

---

*Last updated: 2026-04-09 (Phases 3–5 integrated in kernel, LLM, and `chat_server`.)*
