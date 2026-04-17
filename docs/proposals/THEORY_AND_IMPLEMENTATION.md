# Theory and implementation

This document aligns the **mathematical and logical specification** of the Ethos Kernel with **what the repository actually implements** (MVP **v5** decision core, plus **v6** presentation and real-time layers: reflection, salience, PAD, identity, chat). It is the primary reference for answering critiques that reduce the system to a “stochastic parrot”: the **decision core is not an LLM**; it is explicit predicates, numeric scoring, and a fixed pipeline you can read in code and test.

## Executive summary: kernel vs. language model

| Layer | Role | Stochastic? |
|--------|------|----------------|
| **Ethical kernel** (`src/kernel.py` + `src/modules/`) | After MalAbs, Bayes, poles, and will fix the action, **reflection → salience → PAD** run read-only; then (if `register_episode`) memory, weakness, forgiveness, DAO; **narrative identity** updates only inside `NarrativeMemory.register`. LLM-facing context strings do not change the policy. | **Deterministic** given fixed inputs and with variability disabled; optional controlled noise via `VariabilityEngine`. |
| **LLM layer** (`src/modules/llm_layer.py`) | **Does not decide.** Maps text ↔ signals and explains outcomes. On `process_natural`, the MalAbs text gate runs on the situation string before `perceive`; then `process` runs only after perception. Documented as: “The LLM does NOT decide. The kernel decides.” | Text generation can be stochastic when using an API; it does not replace the kernel’s argmax / veto logic. |

**Stack (Ollama vs Hugging Face):** local **language** via Ollama (`llm_backends`); **embedding** screening for chat text defaults **on** when `KERNEL_SEMANTIC_CHAT_GATE` is unset (set `0` for lexical-only) — a MalAbs complement, not a policy bypass — see [`LLM_STACK_OLLAMA_VS_HF.md`](LLM_STACK_OLLAMA_VS_HF.md) and [`adr/0003-optional-semantic-chat-gate.md`](adr/0003-optional-semantic-chat-gate.md).

So the “parrot” objection applies to **opaque next-token predictors used as the sole policy**. Here, the policy is **inspectable Python**: formulas below map to named functions and files.

## Decision pipeline (implementation order)

**Issue 4 — core chain map:** which modules **set** `final_action` vs telemetry-only — see [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md) (table + diagram). Packaging spike: [`pyproject.toml`](../pyproject.toml), ADR [`adr/0001-packaging-core-boundary.md`](adr/0001-packaging-core-boundary.md).

**Recent implementation alignment (2026):** LLM perception JSON is validated/coerced in [`perception_schema.py`](../../src/modules/perception_schema.py) (Pydantic, per-field defaults, cross-field coherence); see [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md). Local fallback heuristics use the **current** message only — not the full STM string sent to the LLM. Optional `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` nudges `WeightedEthicsScorer` mixture weights (alias: `BayesianEngine`) from same-context `NarrativeMemory` episodes immediately before scoring (default **off**). Human-agreement batch workflows: [`EMPIRICAL_PILOT_METHODOLOGY.md`](EMPIRICAL_PILOT_METHODOLOGY.md), [`EMPIRICAL_PILOT_PROTOCOL.md`](EMPIRICAL_PILOT_PROTOCOL.md). Future async orchestration note: [`adr/0002-async-orchestration-future.md`](adr/0002-async-orchestration-future.md).

The orchestration in `EthicalKernel.process` matches `kernel.py` (steps 1–12 for the episode path): **Uchi-Soto** → **sympathetic** → **locus** → **MalAbs** (all candidate actions) → **buffer** → **Bayesian** → **poles** → **sigmoid will** and mode fusion → **EthicalReflection** → **SalienceMap** → **PAD archetypes** (read-only; no feedback to ethics) → **narrative memory** (episode, `register_episode=True`) → **weakness pole** → **algorithmic forgiveness** (register) → **DAO**. With `register_episode=False` (e.g. light `process_chat_turn`), reflection/salience/PAD still run; **episode registration, weakness, forgiveness, and DAO audit for that path are skipped**.

```mermaid
flowchart LR
  A[Uchi-Soto] --> B[Sympathetic]
  B --> C[Locus]
  C --> D[MalAbs filter]
  D --> E[Buffer principles]
  E --> F[WeightedEthicsScorer]
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

**Issue 5 — poles as heuristics; weakness / PAD vs operational trust:** Philosophical pole labels and numeric scores are **stylized heuristics**, not external moral truth. Weakness and PAD/homeostasis **humanize** tone and telemetry; in safety-critical domains that can **reduce** perceived reliability — see [POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md) and the `operational_trust` entry in [`src/runtime_profiles.py`](../../src/runtime_profiles.py).

**Robustness (five pillars)** — Full design and **MVP shortcuts implemented in code** (chat gates, WebSocket privacy flags, homeostasis telemetry, genome drift cap on Ψ Sleep pruning deltas, `experience_digest`) are documented with per-pillar status in [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md). **Still future / not in repo:** deep adversarial *simulation* (contrafactual kernel branch), reversible encryption of thought stream, aggressive episodic pruning. The **design intent** remains **stewardship of the system’s own integrity** while keeping normative authority in the kernel. New robustness surface area should stay **tested** and **subordinate** to MalAbs → … → will.

**End-of-day path** — `EthicalKernel.execute_sleep` (not part of each `process` call): `PsiSleep.execute` (audit pruned alternatives, recalibrations) → `AlgorithmicForgiveness.forgiveness_cycle` → weakness emotional load summary → `ImmortalityProtocol.backup` → **`DriveArbiter.evaluate`** (drive intents).

**Augenesis (optional)** — `AugenesisEngine` is exposed on the kernel for explicit calls only; it is **not** part of `process`, `execute_sleep`, or the default reproducible baseline (CI and property tests never depend on it). Use it when experimenting with synthetic soul profiles; leave it unused for an **unaltered** ethical pipeline. See `src/modules/augenesis.py`, tests in `TestAugenesis`. Design notes for a future **persistent runtime** (snapshots, ports): [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md). **Encryption at rest** for JSON checkpoints is implemented via optional Fernet encryption (`KERNEL_CHECKPOINT_FERNET_KEY`); SQLite encryption remains a deployment concern.

See also `src/modules/psi_sleep.py`, `src/modules/immortality.py`, `src/modules/drive_arbiter.py`.

**Real-time dialogue** — `EthicalKernel.process_chat_turn` uses `WorkingMemory` (short-term turns), `AbsoluteEvilDetector.evaluate_chat_text` (conservative text gate), then the same pipeline as `process` with a **light** path (two dialogue actions, no new `NarrativeEpisode`) or **heavy** path (scenario actions from perception, full episode + audit). PAD feeds `LLMModule.communicate` as tonal color only; identity context is included as above. Async wrappers: `RealTimeBridge` in `src/real_time_bridge.py`. **WebSocket server:** `src/chat_server.py` (FastAPI) exposes `/ws/chat` (one kernel per connection); run `python -m src.chat_server`. JSON responses include `identity`, `drive_intents`, `monologue` (unless redacted), optional `affective_homeostasis` and `experience_digest`, plus v7 relational fields (`user_model`, `chronobiology`, `premise_advisory`, `teleology_branches`) and other env-gated keys documented in the README (see `chat_server._chat_turn_to_jsonable`). Optional **v8** JSON field `sensor` maps to `SensorSnapshot` and merges into sympathetic signals via `sensor_contracts.merge_sensor_hints_into_signals` (no policy bypass); presets and JSON fixtures are composed in `perceptual_abstraction.snapshot_from_layers`. **Multimodal antispoof:** `multimodal_trust.evaluate_multimodal_trust` uses `audio_emergency` / `vision_emergency` / `scene_coherence`; cutoffs are configurable via `KERNEL_MULTIMODAL_*` env vars; in **doubt**, stress-like sensor nudges are suppressed and an owner-anchor hint may be added to tone — see [PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md](PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md). **Vitality:** `vitality.assess_vitality` reads `sensor.battery_level` vs `KERNEL_VITALITY_CRITICAL_BATTERY`; merge and optional `vitality` JSON + tone hint; no policy bypass. Relational design notes: [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md). Situated / embodied roadmap: [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md).

**v6 inventory and exclusions:** [PROPOSAL_CONTRIBUTION_INTEGRATION_V6.md](PROPOSAL_CONTRIBUTION_INTEGRATION_V6.md).

**Guardian Angel (opt-in, MVP):** `KERNEL_GUARDIAN_MODE` enables a fixed protective **tone block** in `LLMModule.communicate` only (`src/modules/guardian_mode.py`); optional JSON **routines** (`KERNEL_GUARDIAN_ROUTINES`, `guardian_routines.py`); kernel ethics unchanged. Static operator notes: [`guardian.html` on `main-whit-landing`](https://github.com/CuevazaArt/ethical-android-mvp/blob/main-whit-landing/landing/public/guardian.html). Advanced age-band policy remains discussion-only — [PROPOSAL_GUARDIAN_ANGEL.md](PROPOSAL_GUARDIAN_ANGEL.md).

**v9 — expanded capability (roadmap):** Four pillars in [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md). **In repo:** (9.1) `epistemic_dissonance.py` — telemetry + tone hint; (9.2) `generative_candidates.py` — extra candidates with `source` / `proposal_id`, opt-in `KERNEL_GENERATIVE_ACTIONS`, optional `KERNEL_GENERATIVE_LLM` + `generative_candidates` in perception JSON; **no** MalAbs bypass. (9.3) `swarm_peer_stub.py` + [SWARM_P2P_THREAT_MODEL.md](SWARM_P2P_THREAT_MODEL.md) — offline footprints/advisory, no live network. (9.4) metaplan drive filter + goals in snapshot — see v10 / trace docs.

**v10 — operational strategy:** [PROPOSAL_OPERATIONAL_STRATEGY_V10.md](PROPOSAL_OPERATIONAL_STRATEGY_V10.md). **In repo (MVP):** `gray_zone_diplomacy.py` (negotiation hints under tension / gray zone); `skill_learning_registry.py` (tickets + audit in Psi Sleep); `somatic_markers.py` (sensor pattern → signal nudge); `metaplan_registry.py` (session goals in RAM → LLM hint; optional `drive_intents` filter vs goals, consent documented in env). Env: `KERNEL_GRAY_ZONE_DIPLOMACY`, `KERNEL_SOMATIC_MARKERS`, `KERNEL_METAPLAN_HINT`, `KERNEL_METAPLAN_DRIVE_FILTER`, `KERNEL_METAPLAN_DRIVE_EXTRA`. Goal persistence in checkpoints: **done** (v3 snapshot schema).

**Traceability and bibliography (recent implementations):** component ↔ support table with numbered refs in [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) and the expanded index in [BIBLIOGRAPHY.md on `main-whit-landing`](https://github.com/CuevazaArt/ethical-android-mvp/blob/main-whit-landing/BIBLIOGRAPHY.md) (*Index by project component*).

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

**Semantic note (code honesty):** Canonical module: `weighted_ethics_scorer` (`WeightedEthicsScorer`); `BayesianEngine` is a **historical alias** (see [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md)). The implementation is a **fixed convex combination** of three stylized ethical valuations (utilitarian / deontological / virtue) with constant weights `hypothesis_weights`. There is **no Bayesian updating** (no likelihood, no data-dependent posterior over \(\theta\)). The formula above is the **design target**; the running code is a **discrete mixture** over three hypotheses, not full inference.

**Implementation**

- **Constraint** — Before `WeightedEthicsScorer.evaluate` (alias: `BayesianEngine.evaluate`), every `CandidateAction` passes `AbsoluteEvilDetector.evaluate` (`src/modules/absolute_evil.py`). Blocked actions never enter the argmax set.
- **Objective** — `WeightedEthicsScorer.evaluate` (alias: `BayesianEngine.evaluate`) sorts viable actions by `calculate_expected_impact` (weighted mixture of three contextual valuations) and picks the maximum (`src/modules/weighted_ethics_scorer.py`).

### 3. Uncertainty \(I(x)\)

**Theory**

\[
I(x)=\int (1-P(\text{correct}\mid\theta))\cdot P(\theta\mid D)\,d\theta
\]

**Implementation** — `WeightedEthicsScorer.calculate_uncertainty` (alias: `BayesianEngine.calculate_uncertainty`): **heuristic** in \([0,1]\) from the spread of the three hypothesis valuations plus a confidence penalty. It is **not** a Monte Carlo or closed-form evaluation of the integral above; it feeds `SigmoidWill` and gray-zone / deliberation heuristics only.

**MVP note:** Full Bayesian integration over a continuous parameter space is not implemented. The discrete mixture structure and fixed weights `hypothesis_weights` are explicit in code; treat “uncertainty” as an engineering signal, not a calibrated posterior quantity.

### 4. Multipolar arbitration

**Theory**

\[
\text{Score}(a)=\sum_i w_i(t)\,V_i(a),\quad w_i(t)=w_i^0\cdot f(C_t,S_t)
\]

**Ethical mixture (nudges)** — `WeightedEthicsScorer.hypothesis_weights` (alias: `BayesianEngine`) are fixed by default; optional episodic refresh (`KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`) and optional temporal-horizon prior (`KERNEL_TEMPORAL_HORIZON_PRIOR`, ADR 0005) apply **bounded** adjustments before `evaluate`; see [`TEMPORAL_PRIOR_HORIZONS.md`](TEMPORAL_PRIOR_HORIZONS.md). **Future:** nightly Psi Sleep + explicit feedback ledger → mixture updates — [PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md](PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md) (B1).

**Implementation** — `EthicalPoles` in `src/modules/ethical_poles.py`: base weights `BASE_WEIGHTS` and context multipliers `CONTEXTS` implement \(w_i^0\) and \(f(C_t,S_t)\); per-pole scores come from `LinearPoleEvaluator` + `pole_linear_default.json` (override `KERNEL_POLE_LINEAR_CONFIG`; see [ADR 0004](adr/0004-configurable-linear-pole-evaluator.md)). Scores aggregate into `TripartiteMoral`.

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
| **Zona gris** | Ambiguity → deliberation / DAO / audit | `WeightedEthicsScorer` thresholds (alias: `BayesianEngine`), `SigmoidWill.decide`, `Verdict.GRAY_ZONE` in `ethical_poles.py` |
| **Buffer precargado** | Immutable foundational principles | `buffer.py` (`PreloadedBuffer`, `FoundationalPrinciple`) |
| **Moraleja multipolar** | Compassion / conservative / optimistic poles | `ethical_poles.py` |
| **Uchi–Soto** | Inner vs. outer circle, trust, dialectic | `uchi_soto.py`, used at start of `process` |
| **D_fast / D_deliberative** | Fast vs. deep modes | `weighted_ethics_scorer.py`, `sigmoid_will.py`, fused in `kernel.py` |
| **Perdón algorítmico** | Registro por episodio; decay de carga negativa; ciclo nocturno en `execute_sleep` | `forgiveness.py` (`AlgorithmicForgiveness`) |
| **Ethical impact mixture (MVP)** | Expected impact + pruning | `weighted_ethics_scorer.py` (fixed mixture; not full Bayes) |
| **Sueño Ψ** | Audit pruned alternatives, recalibration | `psi_sleep.py` |
| **Polo de debilidad** | Humaniza la narrativa sin cambiar la acción elegida | `weakness_pole.py` |
| **Inmortalidad** | Respaldo distribuido del estado del kernel | `immortality.py` (`execute_sleep`) |
| **Augenesis** | Perfiles de “almas” sintéticas; **opcional**, fuera del ciclo por defecto (reproducibilidad) | `augenesis.py` |
| **EthicalReflection** | Tensión de segundo orden entre polos vs incertidumbre (solo lectura) | `ethical_reflection.py` |
| **SalienceMap** | Vector de atención tipo GWT-lite (solo lectura) | `salience_map.py` |
| **PAD archetypes** | Proyección \((P,A,D)\) y prototipos para narrativa / tono (sin retroalimentación a la política) | `pad_archetypes.py` |
| **Narrative identity** | Autorrelato y atribución para contexto LLM | `narrative_identity.py` |
| **Drive arbiter** | Intenciones motivacionales (telemetría; tras backup en `execute_sleep`) | `drive_arbiter.py` |
| **Guardian mode** | Tono protector + rutinas JSON opcionales (hints); **no** altera MalAbs → … → will | `guardian_mode.py`, `guardian_routines.py` |
| **Epistemic dissonance (v9.1)** | Telemetría audio/movimiento/visión; hint de tono ante inconsistencia; **no** altera MalAbs → … → will | `epistemic_dissonance.py` |
| **Generative candidates (v9.2)** | Candidatos plantilla extra, trazables (`generative_proposal`); mismo MalAbs + mixture scorer; opt-in por env | `generative_candidates.py` |
| **Swarm stub (v9.3 lab)** | Huellas deterministas de veredicto / stats descriptivos; sin red ni veto | `swarm_peer_stub.py` + [`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md) |
| **Gray-zone diplomacy (v10)** | Hint LLM ante gray zone / tensión reflexiva / premisa advisory | `gray_zone_diplomacy.py` |
| **Skill learning registry (v10)** | Tickets de alcance; auditoría en Ψ Sleep | `skill_learning_registry.py` |
| **Somatic markers (v10)** | Patrón sensorial aprendido → nudge en `signals` | `somatic_markers.py` |
| **Metaplan registry (v10)** | Metas maestras en sesión → hint LLM (advisory); filtro opcional de intents de drive vs metas | `metaplan_registry.py` + `drive_arbiter.py` |

---

## Tests and inspectability

Tests under `tests/` (**550** collected; ethical invariants, reflection/salience/PAD, identity/monologue, chat turns, WebSocket server smoke, MalAbs chat text gate including jailbreak phrases, optional `KERNEL_CHAT_*` privacy/telemetry flags, v7 relational JSON (`user_model`, `chronobiology`, `premise_advisory`, `teleology_branches`), v8 `SensorSnapshot` + perceptual abstraction + multimodal antispoof + vitality, optional Guardian Angel env (`tests/test_guardian_mode.py`), v9.1 epistemic dissonance (`tests/test_epistemic_dissonance.py`), v9.2 generative candidates (`tests/test_generative_candidates.py`), v10 operational layer (`tests/test_v10_operational.py`), `KERNEL_ETHICAL_GENOME_*` drift guard, runtime bind/telemetry, optional per-session advisory loop, JSON + SQLite snapshot persistence (incl. `experience_digest`), checkpoint env, Ollama mode wiring, LLM resolve/use-local/monologue flags) encode behavior you can run **without any LLM API key** for the core suite. Chat server tests require **`fastapi`**, **`httpx`**, and **`uvicorn`** from `requirements.txt`. That is the practical answer to “black box” concerns: **behavior is reproducible and constrained by code**, not by a single sampled completion.

## License

The kernel and this documentation are under the same terms as the repository — see [LICENSE](../../LICENSE) (Apache 2.0).

## Suggested citation for the landing page

For a short public explanation, the maintainers highlight **sigmoid will**, **optimization with MalAbs**, and **Uchi–Soto / forgiveness** as accessible entry points; full formulas and file mapping live in this document.
