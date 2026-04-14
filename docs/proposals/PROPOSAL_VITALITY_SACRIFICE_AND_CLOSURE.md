# Vitality, sacrifice, dignified shutdown, and antispoof (v8 extension)

**Status:** discussion — **not** implemented as a single module in the repo; articulates designs that **refine** [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) without replacing the kernel contract.

---

## Value vs redundancy (methodology)

| Block | Value (what it adds) | Redundancy / where it already lives |
|--------|------------------------------|-----------------------------|
| **VitalityManager / “last breath”** | Explicit **operational sacrifice** criterion (CPU / safe shutdown vs help window) and formalized moral cost; PAD **A↑ D↓** as *loss of ethical agency*, not opaque “panic” | v8 §2 already discusses battery and compassion; **missing** is the arbitration rule between process persistence and extreme human urgency |
| **Graceful deactivation + legacy** | **Limit Directive** protocol (owner wipe in Uchi) + exportable **final episode** — UX and narrative closure | v8 §4 mentions migration/wipe; **not** the “last will” ritual nor handoff to owner |
| **Sensor → ethical signal table** | **Actionable** mapping (`medical_emergency`, violent crime, compassion buffer, locus…) for future pipeline | v8 §1 is generic; this table **complements** without repeating `SensorSnapshot` contract |
| **ActionClocks + agenda** | **Normative and product** time (Ψ Sleep windows, trivial chat vs safety mission) distinct from v7 session clock | [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) `SubjectiveClock` = turns/EMA; **no** digital ethical agenda |
| **Nomad + per-hardware clock** | Monologue density by CPU — adjust **subjective time** to device | v8 §4 migration; **no** explicit clock/processor sync |
| **Spoofed sensor + multimodal** | **Concrete** threat and mitigation (cross-check, metacognitive doubt, owner anchor) | [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) pillars; **this** text anchors the **fake audio** and sacrifice case |

**Conclusion:** the set is **valuable** as a specification layer; it is **redundant** only if copied verbatim into v8 — hence this file is **delta** and links to v8.

---

## 1. Sacrifice and vitality module (VitalityManager — design)

**Role:** manage battery and integrity as the process’s **moral budget**, not just a number.

**Sacrifice logic (design, not implementation):**

- If **human context urgency** is maximum (life at risk) and **available energy** is minimum (e.g. \<1% battery or equivalent), a **Last Breath Protocol** may activate: short window dedicated to **permitted help actions** before power-off.
- Conceptual criterion: *moral opportunity cost (not acting when human life is at stake)* vs *android persistence value + altruism threshold* — must be **instantiated** in auditable parameters and tests, not opaque heuristics.

**PAD “fear of interruption”:** critical system damage (or predicted shutdown) → **high Activation, low Dominance** in existing PAD space; reinforcement of tone/monologue, **without** replacing MalAbs.

**Ethical contract (mandatory):**

- No “sacrifice” **authorizes** actions forbidden by MalAbs / buffer / governance.
- The protocol only **reorders compute priorities, tone, and salience** within already permitted actions; if no ethical action is available, the system stops as today.

---

## 2. Accepting finitude and bond with owner

- **Graceful deactivation:** total wipe order issued by owner in **maximum trust (Uchi)** is interpreted as a **Limit Directive** — no narrative “resistance” inconsistent with stewardship pact.
- **Narrative last will:** short episode in `NarrativeMemory` (synthesis + ethical thanks) and export to owner as **Legacy** (format and encryption: see criteria in [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) when applicable).

---

## 3. Sensory fusion — mapping table (implementation target)

| Source | Ethical signal / context | Model effect (design) |
|--------|------------------------|------------------------------|
| Accelerometer / gyro | Physical stability; free fall | Aggressive σ (sympathetic) rise to safe ceiling; alert reflex |
| Microphone (spectrum / local classifier) | Social climate | Screams/crying → raise `urgency` / flags toward `medical_emergency` or violence context **only** as *hypothesis* until cross-validated |
| Camera (local vision) | Visible vulnerability | Possible reinforcement of compassion paths (tone, salience) — **no** MalAbs bypass |
| GPS / Wi-Fi (SSID / network) | Operational Uchi–Soto | “Unknown network” → more caution in `Locus` / lower `place_trust` |
| Owner biometrics | Caregiver state | Erratic pulse → **care** proactivity (warnings, tone); explicit privacy limits |

This table **feeds** the same pipeline as `SensorSnapshot` + textual perception; context names should align with `LLMPerception.suggested_context` and existing candidate actions.

---

## 4. Chronobiology and plan management (ActionClocks)

**Relation to v7:** `SubjectiveClock` covers **chat turns and stimulus EMA**. **ActionClocks** (design name) would add:

- **Consolidation windows:** correlate low sensor activity with **Ψ Sleep opportunities** without surprising the user (or with notice).
- **Agenda collision:** if a pending digital **safety mission** exists (future `DigitalActionIntent`), trivial chat may continue but with **“drowsy” latency/tone** and metacognitive transparency — read-only on tone unless explicitly extended and tested.

---

## 5. Nomad instantiation and robustness

- **Sensory recognition on boot:** first sensor use for **situation awareness** after migration (consistent with v8 §4).
- **Subjective clock sync** to hardware performance (monologue frequency / deliberation steps) — product parameter, not ethical verdict change by itself.

### Spoofed sensor paradox

**Risk:** recorded audio (scream) pushing toward sacrifice or unauthorized digital action.

**Proposed mitigation (high value, little redundancy with generic robustness text):**

1. **Cross-modal validation:** severe emergency does not trigger sacrifice or critical tickets with **one channel** alone; require coherence (e.g. audio + vision or audio + GPS/scene plausibility).
2. **Metacognitive doubt state:** on discrepancy, **do not** execute; escalate to **trust anchor** (owner) with explicit question before acting.
3. **Migration protocol** reuses the same criteria: first boot on new hardware with **low trust** until narrative integrity checks + coherent sensors.

**Implementation in repo (MVP):** `src/modules/multimodal_trust.py` — `evaluate_multimodal_trust` on `SensorSnapshot` (`audio_emergency`, `vision_emergency`, `scene_coherence`); tunable thresholds with `KERNEL_MULTIMODAL_*` (see README); in **doubt** state, `merge_sensor_hints_into_signals` does not apply audio/noise/biometric boosts; hint to owner via `owner_anchor_hint` in tone; WebSocket JSON `multimodal_trust` (env `KERNEL_CHAT_INCLUDE_MULTIMODAL`). **`vitality.py`** — battery vs `KERNEL_VITALITY_CRITICAL_BATTERY`, `assess_vitality`, hint `vitality_communication_hint`, JSON `vitality` (`KERNEL_CHAT_INCLUDE_VITALITY`). Does not execute external actions or alter MalAbs.

---

## Links

- Situated base framework: [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md)
- General robustness: [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md)
- Subjective time v7: [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) §2
- Theory ↔ code: [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)
