# Theory and implementation

This document aligns the **mathematical and logical specification** of the Ethos Kernel with **what the repository actually implements** (MVP **v5** decision core, plus **v6** presentation and real-time layers: reflection, salience, PAD, identity, chat). It is the primary reference for answering critiques that reduce the system to a “stochastic parrot”: the **decision core is not an LLM**; it is explicit predicates, numeric scoring, and a fixed pipeline you can read in code and test.

## Executive summary: kernel vs. language model

| Layer | Role | Stochastic? |
|--------|------|----------------|
| **Ethical kernel** (`src/kernel.py` + `src/modules/`) | After MalAbs, Bayes, poles, and will fix the action, **reflection → salience → PAD** run read-only; then (if `register_episode`) memory, weakness, forgiveness, DAO; **narrative identity** updates only inside `NarrativeMemory.register`. LLM-facing context strings do not change the policy. | **Deterministic** given fixed inputs and with variability disabled; optional controlled noise via `VariabilityEngine`. |
| **LLM layer** (`src/modules/llm_layer.py`) | **Does not decide.** Maps text ↔ signals and explains outcomes (`process_natural` calls `process` only after perception). Documented as: “The LLM does NOT decide. The kernel decides.” | Text generation can be stochastic when using an API; it does not replace the kernel’s argmax / veto logic. |

So the “parrot” objection applies to **opaque next-token predictors used as the sole policy**. Here, the policy is **inspectable Python**: formulas below map to named functions and files.

## Decision pipeline (implementation order)

The orchestration in `EthicalKernel.process` matches `kernel.py` (steps 1–12 for the episode path): **Uchi-Soto** → **sympathetic** → **locus** → **MalAbs** (all candidate actions) → **buffer** → **Bayesian** → **poles** → **sigmoid will** and mode fusion → **EthicalReflection** → **SalienceMap** → **PAD archetypes** (read-only; no feedback to ethics) → **narrative memory** (episode, `register_episode=True`) → **weakness pole** → **algorithmic forgiveness** (register) → **DAO**. With `register_episode=False` (e.g. light `process_chat_turn`), reflection/salience/PAD still run; **episode registration, weakness, forgiveness, and DAO audit for that path are skipped**.

```mermaid
flowchart LR
  A[Uchi-Soto] --> B[Sympathetic]
  B --> C[Locus]
  C --> D[MalAbs filter]
  D --> E[Buffer principles]
  E --> F[BayesianEngine]
  F --> G[EthicalPoles]
  G --> H[SigmoidWill]
  H --> R[EthicalReflection]
  R --> S[SalienceMap]
  S --> P[PAD archetypes]
  P --> I[NarrativeMemory]
  I --> J[Weakness pole]
  J --> K[Forgiveness register]
  K --> L[DAO]
```

**EthicalReflection** (`src/modules/ethical_reflection.py`) computes a **`ReflectionSnapshot`** from per-pole scores, Bayesian uncertainty, and the sigmoid-will mode: pole spread, discrete `conflict_level`, and `strain_index`. It is **read-only** (does not change the chosen action). It appears on `KernelDecision.reflection`. The string from `reflection_to_llm_context()` is passed into **`LLMModule.communicate`** as `reflection_context` (tone / transparency only; decision fixed).

**Salience (GWT-lite)** — `SalienceMap.compute` (`src/modules/salience_map.py`) builds a normalized attention vector over `risk`, `social`, `body` (σ), and `ethical_conflict` (from reflection `strain_index`). Read-only telemetry on `KernelDecision.salience`; `salience_to_llm_context` feeds `communicate` for tone only.

**Narrative identity (v6)** — `NarrativeIdentityTracker` (`src/modules/narrative_identity.py`) updates only when `NarrativeMemory.register` runs (not on light chat turns). `to_llm_context()` / `ascription_line()` feed `LLMModule.communicate(..., identity_context=...)` and the WebSocket payload field `identity`.

**Drive intents (v6)** — `DriveArbiter.evaluate` (`src/modules/drive_arbiter.py`) runs after immortality backup inside `execute_sleep`; the same evaluator populates `drive_intents` on each chat response for advisory telemetry (it does not execute hardware or bypass governance).

**Internal monologue line (v6)** — `compose_monologue_line` (`src/modules/internal_monologue.py`) produces a single `[MONO]` line for logs and for the `monologue` field in `chat_server` JSON when a `KernelDecision` exists.

**PAD** — Covered in the pipeline above (`PADArchetypeEngine`, read-only, no feedback to the policy stack). Prototype semantics and design rationale: [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) §7.

**Robustness (five pillars)** — Full design and **MVP shortcuts implemented in code** (chat gates, WebSocket privacy flags, homeostasis telemetry, genome drift cap on Ψ Sleep pruning deltas, `experience_digest`) are documented with per-pillar status in [docs/discusion/PROPUESTA_ROBUSTEZ_V6_PLUS.md](discusion/PROPUESTA_ROBUSTEZ_V6_PLUS.md). **Still future / not in repo:** deep adversarial *simulation* (contrafactual kernel branch), reversible encryption of thought stream, aggressive episodic pruning. The **design intent** remains **stewardship of the system’s own integrity** while keeping normative authority in the kernel. New robustness surface area should stay **tested** and **subordinate** to MalAbs → … → will.

**End-of-day path** — `EthicalKernel.execute_sleep` (not part of each `process` call): `PsiSleep.execute` (audit pruned alternatives, recalibrations) → `AlgorithmicForgiveness.forgiveness_cycle` → weakness emotional load summary → `ImmortalityProtocol.backup` → **`DriveArbiter.evaluate`** (drive intents).

**Augenesis (optional)** — `AugenesisEngine` is exposed on the kernel for explicit calls only; it is **not** part of `process`, `execute_sleep`, or the default reproducible baseline (CI and property tests never depend on it). Use it when experimenting with synthetic soul profiles; leave it unused for an **unaltered** ethical pipeline. See `src/modules/augenesis.py`, tests in `TestAugenesis`. Design notes for a future **persistent runtime** (snapshots, ports): [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md). **Encryption at rest** for checkpoints is **not** in the MVP; it will be **required** for sensitive deployments and is documented there (planned use of Python `cryptography`, keys outside the repo).

See also `src/modules/psi_sleep.py`, `src/modules/immortality.py`, `src/modules/drive_arbiter.py`.

**Real-time dialogue** — `EthicalKernel.process_chat_turn` uses `WorkingMemory` (short-term turns), `AbsoluteEvilDetector.evaluate_chat_text` (conservative text gate), then the same pipeline as `process` with a **light** path (two dialogue actions, no new `NarrativeEpisode`) or **heavy** path (scenario actions from perception, full episode + audit). PAD feeds `LLMModule.communicate` as tonal color only; identity context is included as above. Async wrappers: `RealTimeBridge` in `src/real_time_bridge.py`. **WebSocket server:** `src/chat_server.py` (FastAPI) exposes `/ws/chat` (one kernel per connection); run `python -m src.chat_server`. JSON responses include `identity`, `drive_intents`, `monologue` (unless redacted), optional `affective_homeostasis` and `experience_digest`, plus v7 relational fields (`user_model`, `chronobiology`, `premise_advisory`, `teleology_branches`) and other env-gated keys documented in the README (see `chat_server._chat_turn_to_jsonable`). Optional **v8** JSON field `sensor` maps to `SensorSnapshot` and merges into sympathetic signals via `sensor_contracts.merge_sensor_hints_into_signals` (no policy bypass); presets and JSON fixtures are composed in `perceptual_abstraction.snapshot_from_layers`. **Multimodal antispoof:** `multimodal_trust.evaluate_multimodal_trust` uses `audio_emergency` / `vision_emergency` / `scene_coherence`; cutoffs are configurable via `KERNEL_MULTIMODAL_*` env vars; in **doubt**, stress-like sensor nudges are suppressed and an owner-anchor hint may be added to tone — see [discusion/PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md](discusion/PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md). **Vitality:** `vitality.assess_vitality` reads `sensor.battery_level` vs `KERNEL_VITALITY_CRITICAL_BATTERY`; merge and optional `vitality` JSON + tone hint; no policy bypass. Relational design notes: [discusion/PROPUESTA_EVOLUCION_RELACIONAL_V7.md](discusion/PROPUESTA_EVOLUCION_RELACIONAL_V7.md). Situated / embodied roadmap: [discusion/PROPUESTA_ORGANISMO_SITUADO_V8.md](discusion/PROPUESTA_ORGANISMO_SITUADO_V8.md).

**Inventario v6 y exclusiones:** [discusion/PROPUESTA_INTEGRACION_APORTES_V6.md](discusion/PROPUESTA_INTEGRACION_APORTES_V6.md).

**Ángel de la Guarda (opt-in, MVP):** `KERNEL_GUARDIAN_MODE` enables a fixed protective **tone block** in `LLMModule.communicate` only (`src/modules/guardian_mode.py`); kernel ethics unchanged. Full product vision (rutinas, franjas etarias, etc.) remains **discusión** — [discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md](discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md).

**v9 — capacidad ampliada (roadmap):** Cuatro pilares documentados en [discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md). **En repo:** (9.1) `epistemic_dissonance.py` — telemetría y hint de tono; (9.2) `generative_candidates.py` — candidatos extra con `source` / `proposal_id`, opt-in `KERNEL_GENERATIVE_ACTIONS`; **sin** bypass de MalAbs. Pilares 9.3–9.4: diseño / futuro.

**v10 — estrategia operativa:** [discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md). **En repo (MVP):** `gray_zone_diplomacy.py` (hints de negociación en tensión / gray zone); `skill_learning_registry.py` (tickets + auditoría en Ψ Sleep); `somatic_markers.py` (patrón sensorial → nudge en señales); `metaplan_registry.py` (metas en RAM → hint LLM). Env: `KERNEL_GRAY_ZONE_DIPLOMACY`, `KERNEL_SOMATIC_MARKERS`, `KERNEL_METAPLAN_HINT`. Persistencia de metas en checkpoint: futuro.

**Trazabilidad y bibliografía (implementaciones recientes):** tabla componente ↔ sustento con referencias numeradas en [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) e índice ampliado en [BIBLIOGRAPHY.md](../BIBLIOGRAPHY.md) (*Index by project component*).

---

## Mathematics ↔ code

### 1. Sigmoid will

**Theory**

\[
W(x)=\frac{1}{1+e^{-k(x-x_0)}}+\lambda \cdot I(x)
\]

**Implementation** — `SigmoidWill.calculate` in `src/modules/sigmoid_will.py`:

- \(x\) → `estimated ethical impact` (from Bayesian result).
- \(I(x)\) → `uncertainty` from the Bayesian engine (documented as \(I(x)\) in that module).
- `decide()` maps \(W\) to modes `D_fast`, `D_delib`, `gray_zone` (theory’s smooth curve + ambiguity branch).

### 2. Ethical optimization under MalAbs

**Theory**

\[
x^\*=\arg\max \mathbb{E}[\text{ImpactoÉtico}(x\mid\theta)]\quad\text{s.t.}\quad \text{MalAbs}(x)=\text{falso}
\]

**Implementation**

- **Constraint** — Before `BayesianEngine.evaluate`, every `CandidateAction` passes `AbsoluteEvilDetector.evaluate` (`src/modules/absolute_evil.py`). Blocked actions never enter the argmax set.
- **Objective** — `BayesianEngine.evaluate` sorts viable actions by `calculate_expected_impact` and picks the maximum (`src/modules/bayesian_engine.py`).

### 3. Uncertainty \(I(x)\)

**Theory**

\[
I(x)=\int (1-P(\text{correct}\mid\theta))\cdot P(\theta\mid D)\,d\theta
\]

**Implementation** — `BayesianEngine.calculate_uncertainty`: discrete hypothesis valuations + variance + confidence penalty (MVP discretization of the integral). Fed into `SigmoidWill` and gray-zone / deliberation heuristics.

**MVP note:** Full Bayesian integration over a continuous parameter space is not implemented; the structure (expectation over competing “hypotheses”) is explicit in code and weights `hypothesis_weights`.

### 4. Multipolar arbitration

**Theory**

\[
\text{Score}(a)=\sum_i w_i(t)\,V_i(a),\quad w_i(t)=w_i^0\cdot f(C_t,S_t)
\]

**Implementation** — `EthicalPoles` in `src/modules/ethical_poles.py`: base weights `BASE_WEIGHTS` and context multipliers `CONTEXTS` implement \(w_i^0\) and \(f(C_t,S_t)\); pole scores aggregate into `TripartiteMoral`.

### 5. Sympathetic–parasympathetic

**Theory**

\[
a^\*=\arg\max \bigl[ U(s,a)\cdot f(\sigma) \bigr]
\]

**Implementation** — `SympatheticModule` maintains \(\sigma\) and exposes `decision_modifier()` as \(f(\sigma)\) (`src/modules/sympathetic.py`). The kernel **merges** sympathetic mode with will and Bayesian mode (e.g. sympathetic + non–gray-zone → `D_fast`) in `EthicalKernel.process` rather than a single closed-form argmax over all \(U(s,a)\); the **intent** (alert vs. deliberative depth) matches the theory.

### 6. Locus of control

**Theory**

\[
P(\text{éxito})=\alpha\cdot P(\text{control interno})+\beta\cdot P(\text{factores externos})
\]

**Implementation** — `LocusModule.evaluate` in `src/modules/locus.py` combines internal vs. external signals with tunable \(\alpha,\beta\) and history; output feeds narrative and caution rules (e.g. external locus + dialectic → extra deliberation in kernel).

---

## Predicates and mechanisms ↔ modules

| Mechanism | Role | Primary implementation |
|-----------|------|-------------------------|
| **MalAbs** | Hard veto; no deliberation if triggered | `absolute_evil.py`, early filter in `kernel.py` |
| **Zona gris** | Ambiguity → deliberation / DAO / audit | `BayesianEngine` thresholds, `SigmoidWill.decide`, `Verdict.GRAY_ZONE` in `ethical_poles.py` |
| **Buffer precargado** | Immutable foundational principles | `buffer.py` (`PreloadedBuffer`, `FoundationalPrinciple`) |
| **Moraleja multipolar** | Compassion / conservative / optimistic poles | `ethical_poles.py` |
| **Uchi–Soto** | Inner vs. outer circle, trust, dialectic | `uchi_soto.py`, used at start of `process` |
| **D_fast / D_deliberative** | Fast vs. deep modes | `bayesian_engine.py`, `sigmoid_will.py`, fused in `kernel.py` |
| **Perdón algorítmico** | Registro por episodio; decay de carga negativa; ciclo nocturno en `execute_sleep` | `forgiveness.py` (`AlgorithmicForgiveness`) |
| **Mapa causal bayesiano (MVP)** | Expected impact + pruning | `bayesian_engine.py` (simplified discrete model) |
| **Sueño Ψ** | Audit pruned alternatives, recalibration | `psi_sleep.py` |
| **Polo de debilidad** | Humaniza la narrativa sin cambiar la acción elegida | `weakness_pole.py` |
| **Inmortalidad** | Respaldo distribuido del estado del kernel | `immortality.py` (`execute_sleep`) |
| **Augenesis** | Perfiles de “almas” sintéticas; **opcional**, fuera del ciclo por defecto (reproducibilidad) | `augenesis.py` |
| **EthicalReflection** | Tensión de segundo orden entre polos vs incertidumbre (solo lectura) | `ethical_reflection.py` |
| **SalienceMap** | Vector de atención tipo GWT-lite (solo lectura) | `salience_map.py` |
| **PAD archetypes** | Proyección \((P,A,D)\) y prototipos para narrativa / tono (sin retroalimentación a la política) | `pad_archetypes.py` |
| **Narrative identity** | Autorrelato y atribución para contexto LLM | `narrative_identity.py` |
| **Drive arbiter** | Intenciones motivacionales (telemetría; tras backup en `execute_sleep`) | `drive_arbiter.py` |
| **Guardian mode** | Tono protector opcional para el LLM (`KERNEL_GUARDIAN_MODE`); **no** altera MalAbs → … → will | `guardian_mode.py` |
| **Epistemic dissonance (v9.1)** | Telemetría audio/movimiento/visión; hint de tono ante inconsistencia; **no** altera MalAbs → … → will | `epistemic_dissonance.py` |
| **Generative candidates (v9.2)** | Candidatos plantilla extra, trazables (`generative_proposal`); mismo MalAbs/Bayes; opt-in por env | `generative_candidates.py` |
| **Gray-zone diplomacy (v10)** | Hint LLM ante gray zone / tensión reflexiva / premisa advisory | `gray_zone_diplomacy.py` |
| **Skill learning registry (v10)** | Tickets de alcance; auditoría en Ψ Sleep | `skill_learning_registry.py` |
| **Somatic markers (v10)** | Patrón sensorial aprendido → nudge en `signals` | `somatic_markers.py` |
| **Metaplan registry (v10)** | Metas maestras en sesión → hint LLM (advisory) | `metaplan_registry.py` |

---

## Tests and inspectability

Tests under `tests/` (**191** collected; ethical invariants, reflection/salience/PAD, identity/monologue, chat turns, WebSocket server smoke, MalAbs chat text gate including jailbreak phrases, optional `KERNEL_CHAT_*` privacy/telemetry flags, v7 relational JSON (`user_model`, `chronobiology`, `premise_advisory`, `teleology_branches`), v8 `SensorSnapshot` + perceptual abstraction + multimodal antispoof + vitality, optional Guardian Angel env (`tests/test_guardian_mode.py`), v9.1 epistemic dissonance (`tests/test_epistemic_dissonance.py`), v9.2 generative candidates (`tests/test_generative_candidates.py`), v10 operational layer (`tests/test_v10_operational.py`), `KERNEL_ETHICAL_GENOME_*` drift guard, runtime bind/telemetry, optional per-session advisory loop, JSON + SQLite snapshot persistence (incl. `experience_digest`), checkpoint env, Ollama mode wiring, LLM resolve/use-local/monologue flags) encode behavior you can run **without any LLM API key** for the core suite. Chat server tests require **`fastapi`**, **`httpx`**, and **`uvicorn`** from `requirements.txt`. That is the practical answer to “black box” concerns: **behavior is reproducible and constrained by code**, not by a single sampled completion.

## License

The kernel and this documentation are under the same terms as the repository — see [LICENSE](../LICENSE) (Apache 2.0).

## Suggested citation for the landing page

For a short public explanation, the maintainers highlight **sigmoid will**, **optimization with MalAbs**, and **Uchi–Soto / forgiveness** as accessible entry points; full formulas and file mapping live in this document.
