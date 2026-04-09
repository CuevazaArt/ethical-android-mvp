# Theory and implementation

This document aligns the **mathematical and logical specification** of the Ethical Android kernel with **what the repository actually implements**. It is the primary reference for answering critiques that reduce the system to a “stochastic parrot”: the **decision core is not an LLM**; it is explicit predicates, numeric scoring, and a fixed pipeline you can read in code and test.

## Executive summary: kernel vs. language model

| Layer | Role | Stochastic? |
|--------|------|----------------|
| **Ethical kernel** (`src/kernel.py` + `src/modules/`) | Chooses actions via MalAbs filtering, Bayesian expectation, multipolar scores, sigmoid will, and mode fusion. | **Deterministic** given fixed inputs and with variability disabled; optional controlled noise via `VariabilityEngine`. |
| **LLM layer** (`src/modules/llm_layer.py`) | **Does not decide.** Maps text ↔ signals and explains outcomes. Documented as: “The LLM does NOT decide. The kernel decides.” | Text generation can be stochastic when using an API; it does not replace the kernel’s argmax / veto logic. |

So the “parrot” objection applies to **opaque next-token predictors used as the sole policy**. Here, the policy is **inspectable Python**: formulas below map to named functions and files.

## Decision pipeline (implementation order)

The orchestration in `EthicalKernel.process` matches the conceptual flow: social context → body state → attribution → **hard veto** → constitution → Bayesian choice → multipolar narrative → will → memory / audit / forgiveness.

```mermaid
flowchart LR
  A[Uchi-Soto] --> B[Sympathetic]
  B --> C[Locus]
  C --> D[MalAbs filter]
  D --> E[Buffer principles]
  E --> F[BayesianEngine]
  F --> G[EthicalPoles]
  G --> H[SigmoidWill]
  H --> I[Narrative + DAO]
  I --> J[Forgiveness / Weakness]
```

After `final_action` and `decision_mode` are fixed, **`PADArchetypeEngine`** (`src/modules/pad_archetypes.py`) projects sympathetic σ, multipolar `total_score`, and locus dominance into \((P,A,D)\in[0,1]^3\) and softmax weights over fixed prototypes. This step **does not** feed back into MalAbs, buffer, Bayesian choice, poles, or will; results attach to `KernelDecision` and `NarrativeEpisode` for narrative and presentation. Canonical design notes: `docs/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` §7.

Psi Sleep (`PsiSleep`) and Immortality / Augenesis run on their own schedules or auxiliary paths; see `src/modules/psi_sleep.py` and `kernel` docstring.

**Real-time dialogue** — `EthicalKernel.process_chat_turn` uses `WorkingMemory` (short-term turns), `AbsoluteEvilDetector.evaluate_chat_text` (conservative text gate), then the same pipeline as `process` with a **light** path (two dialogue actions, no new `NarrativeEpisode`) or **heavy** path (scenario actions from perception, full episode + audit). PAD feeds `LLMModule.communicate` as tonal color only. Async wrappers: `RealTimeBridge` in `src/real_time_bridge.py`. **WebSocket server:** `src/chat_server.py` (FastAPI) exposes `/ws/chat` (one kernel per connection); run `python -m src.chat_server`.

**Evolución propuesta (v6, discusión):** inventario del modelo y fases de integración no redundantes — [discusion/PROPUESTA_INTEGRACION_APORTES_V6.md](discusion/PROPUESTA_INTEGRACION_APORTES_V6.md).

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
| **Perdón algorítmico** | Decay of negative memory weight | `forgiveness.py` (`AlgorithmicForgiveness`) |
| **Mapa causal bayesiano (MVP)** | Expected impact + pruning | `bayesian_engine.py` (simplified discrete model) |
| **Sueño Ψ** | Audit pruned alternatives, recalibration | `psi_sleep.py` |

---

## Tests and inspectability

Property and integration tests under `tests/` (e.g. `test_ethical_properties.py`) encode invariants you can run without any LLM API key. That is the practical answer to “black box” concerns: **behavior is reproducible and constrained by code**, not by a single sampled completion.

## License

The kernel and this documentation are under the same terms as the repository — see [LICENSE](../LICENSE) (Apache 2.0).

## Suggested citation for the landing page

For a short public explanation, the maintainers highlight **sigmoid will**, **optimization with MalAbs**, and **Uchi–Soto / forgiveness** as accessible entry points; full formulas and file mapping live in this document.
