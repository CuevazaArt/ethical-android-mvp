# Operational strategy — v10 (diplomacy, skills, soma, metaplan)

**Status:** discussion + **MVP in code** (`gray_zone_diplomacy`, `skill_learning_registry`, `somatic_markers`, `metaplan_registry`; integration in `process_chat_turn` / `execute_sleep`). MalAbs and buffer **unchanged**.

This document **activates** four contributions that complement [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md): they do not replace the `MalAbs → … → will` pipeline; they add **dialogue governance**, **learning traceability**, **learned somatic caution**, and **long-term intent continuity**.

---

## Fit map (where each idea lives)

| Contribution | Role | Existing modules / links | Repo implementation (v10) |
|--------|-----|------------------------------|---------------------------|
| **1. GrayZoneDiplomacy** | In the gray zone or high reflective tension, the model **not only** refuses: it guides toward a **negotiated exit** (tone / transparency) | `SigmoidWill` / Bayes `gray_zone`, `EthicalReflection`, `premise_validation`, `LLMModule.communicate` | `gray_zone_diplomacy.py` — optional hint via `weakness_line`; `KERNEL_GRAY_ZONE_DIPLOMACY` |
| **2. SkillLearningRegistry** | New digital capabilities only with **explicit scope** and **auditing** in Ψ Sleep | `AugenesisEngine`, `PsiSleep`, digital agency agenda (v8 discussion) | `skill_learning_registry.py` — `pending/approved/rejected` tickets; lines in `execute_sleep` |
| **3. Somatic markers** | Sensory patterns associated with **caution** (nudge in `signals` before the decision-maker) | `SensorSnapshot`, `merge_sensor_hints_into_signals`, post-decision PAD | `somatic_markers.py` — `SomaticMarkerStore` + `apply_somatic_nudges`; **does not** replace MalAbs |
| **4. Nomadic metaplanning** | Master goals across sessions / hardware | Checkpoints [checkpoint.py](../../src/persistence/checkpoint.py), v7 teleology, roadmap **9.4** v9 | `metaplan_registry.py` — goals in memory + LLM hint; **snapshot persistence** = future (extend `KernelSnapshotV1`) |

**Conceptual flow (strategy layer)** — pedagogical reading; the actual order follows `kernel.py`:

1. Multimodal perception (v8) → signals + (optional) learned **somatic markers**.  
2. Buffer + MalAbs + Bayes + … (invariant).  
3. Reflection / gray zone → (optional) **diplomacy** in the text to the user.  
4. **Generative** candidates (v9.2) if applicable.  
5. **Metaplan** aligns tone with declared goals (advisory).  
6. Skill learning: only with a **ticket**; closed in **Ψ Sleep**.

---

## 1. Gray zone negotiation (GrayZoneDiplomacy)

**Problem:** Questionable orders that do not cross MalAbs may fall into the **gray zone** or high tension between poles; a blunt "no" erodes trust.

**Design:** If the decision mode is `gray_zone`, or reflection marks medium/high tension, or an active **advisory premise** is present, a reminder for **dialectical negotiation** is added to the LLM layer: acknowledge intent, name tension with civic principles, offer a concrete alternative.

**Contract:** Does not weaken MalAbs or the buffer; it is **presentation + transparency**.

---

## 2. Skill acquisition system (SkillLearningRegistry)

**Problem:** "Learning" APIs or tools without governance is a mission risk.

**Design:** Queue of **tickets** (`scope`, `justification`, status). Logical flow: identification → report → **explicit authorization** (future UI) → consolidation in Ψ Sleep with an audit line ("is it still aligned with augenesis / ethics?").

**MVP in code:** In-memory registry; programmatic `approve` / `reject`; text appended in `execute_sleep` if there are pending or recent items.

---

## 3. Somatic markers (sensory ethical intuition)

**Problem:** Fixed rules do not capture "this *pattern* went wrong for me before".

**Design:** **Quantized** key from sensors; caution weight in `[0,1]`; small push to `risk` / `urgency` in `signals` **before** `process`. Explicit learning via `learn_negative_pattern` (tests, demos, or future post-episode policy).

**Contract:** Heuristic reinforcement; **MalAbs still evaluates actions** the same way.

---

## 4. Nomadic metaplanning

**Problem:** Goals spanning days/weeks must survive device changes.

**Design:** Registry of **master goals** (`MetaplanRegistry`) with priority; optional LLM hint. **Persistence** alongside the JSON checkpoint requires extending `KernelSnapshotV1` (future work); the MVP keeps goals in RAM per session.

**Contract:** Advisory; revocation and consent UX are outside the numerical core.

---

## Links

| Document | Role |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) | Pipeline; LLM does not decide |
| [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) | v9 epistemic / generative / swarm / metaplan roadmap |
| [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) | Robustness, privacy |
| [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) | Persistence, checkpoints |
