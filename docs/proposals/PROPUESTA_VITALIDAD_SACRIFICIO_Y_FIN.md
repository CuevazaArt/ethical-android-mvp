# Vitality, sacrifice, graceful end, and anti-spoof (v8 extension)

**Status:** discussion — **not** implemented as a single module in the repo; articulates designs that **refine** [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) without replacing the kernel contract.

---

## Value vs. redundancy (methodology)

| Block | Value (what it contributes that is new) | Redundancy / where it already exists |
|-------|------------------------------|-----------------------------|
| **VitalityManager / "last breath"** | Explicit criterion for **operational sacrifice** (CPU/safe shutdown vs. help window) and formalized moral cost; PAD **A↑ D↓** as *loss of ethical agency*, not opaque "panic" | v8 §2 already mentions battery and compassion; **missing** the arbitration rule between process persistence and extreme human urgency |
| **Graceful shutdown + legacy** | **Boundary Directive** protocol (deletion by owner in Uchi) + exportable **final episode** — UX and narrative closure | v8 §4 mentions migration/deletion; **not** the "last will" ritual nor handover to the owner |
| **Sensor → ethical signal table** | **Actionable** mapping (medical_emergency, violent_crime, compassion buffer, locus…) for future pipeline | v8 §1 is generic; this table **complements** without repeating the `SensorSnapshot` contract |
| **ActionClocks + agenda** | **Normative and product time** (Ψ Sleep windows, trivial chat vs. security mission) distinct from v7 session clock | [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) `SubjectiveClock` = turns/EMA; **not** a digital ethical agenda |
| **Nomad + clock by hardware** | Monologue density based on CPU — **subjective time** adjustment to the device | v8 §4 migration; **no** explicit clock/processor synchronization |
| **Deceived sensor + multimodal** | **Concrete** threat and mitigation (cross-check, "metacognitive doubt", owner anchor) | [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) pillars; **this** text anchors it to the **fake audio** case and sacrifice |

**Conclusion:** the set is **valuable** as a specification layer; it is **redundant** only if copied word for word into v8 — that is why this file is a **delta** and links to v8.

---

## 1. Sacrifice and vitality module (VitalityManager — design)

**Role:** manage battery and integrity **as a moral budget of the process**, not merely as a number.

**Sacrifice logic (design, not implementation):**

- If the **urgency** of human context is maximum (life at risk) and **available energy** is minimal (e.g. \<1% battery or equivalent), a **Last Breath Protocol** may be activated: a short window dedicated to **permitted help actions** before shutdown.
- Conceptual criterion: *Moral opportunity cost (failing to act before a human life)* vs. *Android persistence value + altruism threshold* — must be **instantiated** in auditable parameters and tests, not in opaque heuristics.

**PAD "fear of interruption":** critical system damage (or predicted shutdown) → **High Activation, low Dominance** in the existing PAD space; reinforcement of tone/monologue, **without** replacing MalAbs.

**Ethical contract (mandatory):**

- No "sacrifice" **authorizes** actions prohibited by MalAbs / buffer / governance.
- The protocol only **reorders compute priorities, tone, and salience** within already permitted actions; if no ethical action is available, the system halts as it does today.

---

## 2. Acceptance of finitude and bond with the owner

- **Graceful shutdown:** a full-deletion order issued by the owner within a **maximum-trust (Uchi)** relationship is interpreted as a **Boundary Directive** — without narrative "resistance" incoherent with the stewardship pact.
- **Narrative last will:** a short episode in `NarrativeMemory` (synthesis + ethical acknowledgment) and export to the owner as a **Legacy** (format and encryption: see criteria in [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) when applicable).

---

## 3. Sensory fusion — mapping table (implementation objective)

| Source | Ethical signal / context | Effect on the model (design) |
|--------|------------------------|------------------------------|
| Accelerometer / gyroscope | Physical stability; free fall | Aggressive rise of σ (sympathetic) up to safe ceiling; alert reflex |
| Microphone (spectrum / local classifier) | Social climate | Screaming/crying → elevation of `urgency` / flags toward `medical_emergency` or violence context **only** as a *hypothesis* until cross-validation |
| Camera (local vision) | Visible vulnerability | Possible reinforcement of compassion pathways (tone, salience) — **no** MalAbs bypass |
| GPS / Wi-Fi (SSID / network) | Operational Uchi–Soto | "Unknown network" → more caution in `Locus` / low `place_trust` |
| Owner biometrics | Caregiver state | Erratic pulse → **care** proactivity (alerts, tone); explicit privacy limits |

This table **feeds** the same pipeline as `SensorSnapshot` + textual perception; context names must align with `LLMPerception.suggested_context` and existing candidate actions.

---

## 4. Chronobiology and plan management (ActionClocks)

**Relationship with v7:** `SubjectiveClock` covers **chat turns and stimulus EMA**. **ActionClocks** (design name) would add:

- **Consolidation windows:** correlate low sensory activity with **Ψ Sleep opportunities** without surprising the user (or with a warning).
- **Agenda collision:** if there is a pending digital security "mission" (future `DigitalActionIntent`), trivial chat can continue but with **"drowsy" latency/tone** and metacognitive transparency — read-only on tone unless explicitly extended and tested.

---

## 5. Nomadic instantiation and robustness

- **Sensor awareness at startup:** first sensor use for **situation awareness** after migration (consistent with v8 §4).
- **Subjective clock synchronization** to hardware performance (monologue frequency / deliberation steps) — a product parameter, not an ethical verdict change by itself.

### The deceived sensor paradox

**Risk:** recorded audio (scream) pushing toward sacrifice or unauthorized digital action.

**Proposed mitigation (high value, little redundancy with generic robustness text):**

1. **Cross-modal validation:** a serious emergency does not trigger sacrifice or critical tickets with **a single channel**; require coherence (e.g. audio + vision or audio + GPS/scene plausibility).
2. **Metacognitive doubt state:** when there is discrepancy, **do not** execute; escalate to the **trust anchor** (owner) with an explicit question before acting.
3. **Migration protocol** reuses the same criteria: first startup on new hardware with **low trust** until narrative integrity checks + coherent sensors.

**Implementation in repo (MVP):** `src/modules/multimodal_trust.py` — `evaluate_multimodal_trust` on `SensorSnapshot` (`audio_emergency`, `vision_emergency`, `scene_coherence`); adjustable thresholds with `KERNEL_MULTIMODAL_*` (see README); in **doubt** state, `merge_sensor_hints_into_signals` does not apply audio/noise/biometric reinforcements; owner anchor hint via `owner_anchor_hint` in tone; WebSocket JSON `multimodal_trust` (env `KERNEL_CHAT_INCLUDE_MULTIMODAL`). **`vitality.py`** — battery vs `KERNEL_VITALITY_CRITICAL_BATTERY`, `assess_vitality`, hint `vitality_communication_hint`, JSON `vitality` (`KERNEL_CHAT_INCLUDE_VITALITY`). Does not execute external actions or alter MalAbs.

---

## Links

- Base situated framework: [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md)
- General robustness: [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md)
- Subjective time v7: [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) §2
- Theory ↔ code: [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md)
