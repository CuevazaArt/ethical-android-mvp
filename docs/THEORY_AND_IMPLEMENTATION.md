# Theory and implementation

This document aligns the **mathematical and logical specification** of the Ethical Android kernel with **what the repository actually implements** (MVP **v5** decision core, plus **v6** presentation and real-time layers: reflection, salience, PAD, identity, chat). It is the primary reference for answering critiques that reduce the system to a “stochastic parrot”: the **decision core is not an LLM**; it is explicit predicates, numeric scoring, and a fixed pipeline you can read in code and test.

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

**End-of-day path** — `EthicalKernel.execute_sleep` (not part of each `process` call): `PsiSleep.execute` (audit pruned alternatives, recalibrations) → `AlgorithmicForgiveness.forgiveness_cycle` → weakness emotional load summary → `ImmortalityProtocol.backup` → **`DriveArbiter.evaluate`** (drive intents).

**Augenesis (optional)** — `AugenesisEngine` is exposed on the kernel for explicit calls only; it is **not** part of `process`, `execute_sleep`, or the default reproducible baseline (CI and property tests never depend on it). Use it when experimenting with synthetic soul profiles; leave it unused for an **unaltered** ethical pipeline. See `src/modules/augenesis.py`, tests in `TestAugenesis`. Design notes for a future **persistent runtime** (snapshots, ports): [RUNTIME_PERSISTENTE.md](RUNTIME_PERSISTENTE.md).

See also `src/modules/psi_sleep.py`, `src/modules/immortality.py`, `src/modules/drive_arbiter.py`.

**Real-time dialogue** — `EthicalKernel.process_chat_turn` uses `WorkingMemory` (short-term turns), `AbsoluteEvilDetector.evaluate_chat_text` (conservative text gate), then the same pipeline as `process` with a **light** path (two dialogue actions, no new `NarrativeEpisode`) or **heavy** path (scenario actions from perception, full episode + audit). PAD feeds `LLMModule.communicate` as tonal color only; identity context is included as above. Async wrappers: `RealTimeBridge` in `src/real_time_bridge.py`. **WebSocket server:** `src/chat_server.py` (FastAPI) exposes `/ws/chat` (one kernel per connection); run `python -m src.chat_server`. JSON responses include `identity`, `drive_intents`, and `monologue` (see `chat_server._chat_turn_to_jsonable`).

**Inventario v6 y exclusiones:** [discusion/PROPUESTA_INTEGRACION_APORTES_V6.md](discusion/PROPUESTA_INTEGRACION_APORTES_V6.md).

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

---

## Tests and inspectability

Tests under `tests/` (**77** collected; ethical invariants, reflection/salience/PAD, identity/monologue, chat turns, WebSocket server smoke) encode behavior you can run **without any LLM API key** for the core suite. Chat server tests require **`fastapi`**, **`httpx`**, and **`uvicorn`** from `requirements.txt`. That is the practical answer to “black box” concerns: **behavior is reproducible and constrained by code**, not by a single sampled completion.

## License

The kernel and this documentation are under the same terms as the repository — see [LICENSE](../LICENSE) (Apache 2.0).

## Suggested citation for the landing page

For a short public explanation, the maintainers highlight **sigmoid will**, **optimization with MalAbs**, and **Uchi–Soto / forgiveness** as accessible entry points; full formulas and file mapping live in this document.
