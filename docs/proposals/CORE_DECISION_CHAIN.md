# Core decision chain (MalAbs → action)

**Audience:** reviewers and integrators who need a **single map** from inputs to `KernelDecision.final_action`, without reading all of `src/kernel.py` first.

**Cross-refs:** orchestration in [`src/kernel.py`](../src/kernel.py) (`EthicalKernel.process`), theory in [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md), runtime boundaries in [`RUNTIME_CONTRACT.md`](RUNTIME_CONTRACT.md), packaging spike in [`adr/0001-packaging-core-boundary.md`](adr/0001-packaging-core-boundary.md). **Bayesian mixture nudges** (optional, before `evaluate`): episodic refresh (`KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`, see [README](README.md)), temporal-horizon prior [`TEMPORAL_PRIOR_HORIZONS.md`](TEMPORAL_PRIOR_HORIZONS.md) (`KERNEL_TEMPORAL_HORIZON_PRIOR`) — see [`bayesian_engine.py`](../src/modules/bayesian_engine.py).

---

## Flow (batch path `process`)

The LLM is **not** on this path unless a higher layer calls `process_natural` / `process_chat_turn` first (those still end in `process` with structured `signals` and `CandidateAction` lists).

```mermaid
flowchart TD
  subgraph inputs [Inputs]
    A[CandidateAction list]
    S[signals + context]
  end
  subgraph pre [Pre-scoring]
    U[UchiSotoModule]
    Y[SympatheticModule]
    L[LocusModule]
  end
  subgraph veto [Veto / selection]
    M[AbsoluteEvilDetector — MalAbs]
    B[PreloadedBuffer.activate]
    E[BayesianEngine.evaluate]
  end
  subgraph post [Post-choice — does not change action id]
    P[EthicalPoles.evaluate]
    W[SigmoidWill.decide]
    X["Mode fusion → decision_mode"]
  end
  subgraph ro [Read-only telemetry]
    R[EthicalReflection]
    N[SalienceMap]
    PAD[PADArchetypeEngine]
  end
  subgraph ep [If register_episode]
    MEM[NarrativeMemory.register]
    WK[WeaknessPole]
    FG[Forgiveness / DAO audit]
  end
  A --> U
  S --> U
  U --> Y --> L --> M
  M -->|all blocked| Z[final_action = BLOCKED]
  M -->|survivors clean_actions| B --> E
  E -->|chosen_action.name| P --> W --> X
  X --> R --> N --> PAD
  PAD --> MEM --> WK --> FG
```

---

## Who sets `final_action`?

In `EthicalKernel.process`, **`final_action` is the string name of a surviving candidate**:

| Stage | Module(s) | Effect on `final_action` |
|-------|-----------|---------------------------|
| MalAbs | `AbsoluteEvilDetector` | **Veto:** drops candidates; if none remain → `"BLOCKED: no permitted actions"`. |
| Scoring / choice | `BayesianEngine` | **Selects** `chosen_action` among MalAbs survivors (prune + argmax expected impact in `evaluate`). |
| Buffer | `PreloadedBuffer.activate` | **Does not** pass principles into `BayesianEngine.evaluate` in the current code; L0 / constitution side effects apply elsewhere (see buffer + moral hub docs). |
| Poles | `EthicalPoles` | **No:** evaluates the **already chosen** action name; updates multipolar verdict / score for audit and LLM tone. |
| Will | `SigmoidWill` | **No:** feeds **mode** (`gray_zone`, etc.); `final_mode` merges will + sympathetic + locus + Bayesian mode. |
| Reflection / salience / PAD | `EthicalReflection`, `SalienceMap`, `PADArchetypeEngine` | **No** (read-only on policy). |
| Memory / weakness / DAO | `NarrativeMemory`, `WeaknessPole`, `MockDAO`… | **No:** run **after** `final_action` is fixed (when `register_episode` is true). |

**Optional noise:** `VariabilityEngine`, when active, perturbs impact/confidence **inside** `BayesianEngine` inputs — still within the same MalAbs → Bayes selection machinery.

**Chat path:** `process_chat_turn` may supply different candidate sets or block at the **text** gate (`evaluate_chat_text`); once `process` runs, the same rule applies: **`final_action` comes from `bayes_result.chosen_action.name` or a MalAbs block.**

---

## “Core” vs “theater” (product boundary)

Rough split for packaging and mental model — not a hard import graph yet (see ADR):

| Tier | Includes | Role |
|------|----------|------|
| **Core policy** | MalAbs, buffer (L0), `BayesianEngine`, `EthicalPoles`, `SigmoidWill`, sympathetic / locus / uchi-soto as wired in `process` | Deterministic ethical choice + modes. |
| **Narrative & audit** | `NarrativeMemory`, weakness, forgiveness, DAO mock, hub hooks | Identity and traceability; **do not** replace the core argmax. |
| **Advisory / UX** | PAD, reflection, salience, LLM `communicate`, WebSocket JSON extras | Tone and transparency; **read-only** on `final_action` per contract. HCI / poles honesty: [POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md). |
| **Runtime** | FastAPI, persistence, checkpoints, LAN clients | Deployment; **does not** redefine ethics ([`RUNTIME_CONTRACT.md`](RUNTIME_CONTRACT.md)). |

---

*Issue 4 deliverable — MoSex Macchina Lab.*
