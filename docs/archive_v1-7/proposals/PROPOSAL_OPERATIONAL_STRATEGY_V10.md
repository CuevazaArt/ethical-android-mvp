# Operational strategy — v10 (diplomacy, skills, soma, metaplan)

**Status:** discussion + **MVP in code** (`gray_zone_diplomacy`, `skill_learning_registry`, `somatic_markers`, `metaplan_registry`; integration in `process_chat_turn` / `execute_sleep`). MalAbs and buffer **unchanged**.

This document **turns on** four contributions that complement [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md): they do not replace the `MalAbs → … → will` pipeline; they add **dialogue governance**, **learning traceability**, **learned somatic caution**, and **long-horizon intention continuity**.

---

## Fit map (where each idea lives)

| Contribution | Role | Existing modules / links | Repo implementation (v10) |
|--------|-----|------------------------------|---------------------------|
| **1. GrayZoneDiplomacy** | In gray zone or high reflective tension, the model **does not only** deny: it steers toward a **negotiated exit** (tone / transparency) | `SigmoidWill` / Bayes `gray_zone`, `EthicalReflection`, `premise_validation`, `LLMModule.communicate` | `gray_zone_diplomacy.py` — optional hint via `weakness_line`; `KERNEL_GRAY_ZONE_DIPLOMACY` |
| **2. SkillLearningRegistry** | New digital capabilities only with **explicit scope** and **audit** in Ψ Sleep | `AugenesisEngine`, `PsiSleep`, digital agency agenda (v8 discussion) | `skill_learning_registry.py` — tickets `pending/approved/rejected`; lines in `execute_sleep` |
| **3. Somatic markers** | Sensory patterns associated with **caution** (nudge in `signals` before decider) | `SensorSnapshot`, `merge_sensor_hints_into_signals`, post-decision PAD | `somatic_markers.py` — `SomaticMarkerStore` + `apply_somatic_nudges`; **does not** replace MalAbs |
| **4. Nomad metaplanning** | Master goals across sessions / hardware | Checkpoints [checkpoint.py](../../src/persistence/checkpoint.py), v7 teleology, **9.4** roadmap in v9 | `metaplan_registry.py` — goals in memory + LLM hint; **persistence in snapshot** = future (extend `KernelSnapshotV1`) |

**Conceptual flow (strategy layer)** — pedagogical reading; real order follows `kernel.py`:

1. Multimodal perception (v8) → signals + (optional) learned **somatic markers**.  
2. Buffer + MalAbs + Bayes + … (invariant).  
3. Reflection / gray zone → (optional) **diplomacy** in text to user.  
4. **Generative** candidates (v9.2) if applicable.  
5. **Metaplan** aligns tone with declared goals (advisory).  
6. Skill learning: **ticket** only; closure in **Ψ Sleep**.

---

## 1. Negotiation in the gray zone (GrayZoneDiplomacy)

**Problem:** Questionable orders that do not cross MalAbs can land in **gray zone** or high tension between poles; a dry “no” erodes trust.

**Design:** If decision mode is `gray_zone`, or reflection marks medium/high tension, or an **advisory premise** is active, add to the LLM layer a **dialectical negotiation** reminder: acknowledge intent, name tension with civic principles, offer a concrete alternative.

**Contract:** Does not weaken MalAbs or buffer; it is **presentation + transparency**.

---

## 2. Skill acquisition system (SkillLearningRegistry)

**Problem:** “Learning” APIs or tools without governance is mission risk.

**Design:** **Ticket** queue (`scope`, `justification`, state). Logical flow: identification → report → **explicit authorization** (future UI) → consolidation in Ψ Sleep with audit line (“still aligned with augenesis / ethics?”).

**MVP in code:** In-memory registry; programmatic `approve` / `reject`; text appended in `execute_sleep` if pending or recent.

---

## 3. Somatic markers (ethical sensory intuition)

**Problem:** Fixed rules do not capture “this *pattern* already went wrong before.”

**Design:** **Quantized** key from sensors; caution weight in `[0,1]`; small push to `risk` / `urgency` in `signals` **before** `process`. Explicit learning via `learn_negative_pattern` (tests, demos, or future post-episode policy).

**Contract:** Heuristic reinforcement; **MalAbs still evaluates actions** the same.

---

## 4. Nomad metaplanning

**Problem:** Goals spanning days/weeks must survive device change.

**Design:** **Master goal** registry (`MetaplanRegistry`) with priority; optional hint to LLM. **Persistence** with JSON checkpoint requires extending `KernelSnapshotV1` (future work); MVP keeps goals in RAM per session.

**Contract:** Advisory; revocation and consent UX outside numeric core.

---

## Links

| Document | Role |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) | Pipeline; LLM does not decide |
| [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md) | v9 epistemic / generative / swarm / metaplan roadmap |
| [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) | Robustness, privacy |
| [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) | Persistence, checkpoints |
