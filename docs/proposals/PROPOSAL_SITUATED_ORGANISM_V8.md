# Situated and existential organism (v8) — sensory fusion, vital drive, digital agency, migration

**Status:** discussion + **contract and fusion** in code (`sensor_contracts.py`, `perceptual_abstraction.py`, `process_chat_turn` / WebSocket + env `KERNEL_SENSOR_*`). **Does not replace** MalAbs, Bayes, buffer, or will.

**Relationship with v7 relational:** [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) covers **dialogue** (lightweight ToM, subjective time, advisory premises, qualitative teleology). This document (v8) covers the **situated body**: sensors, hardware persistence, fear of interruption, digital action, and migration between devices. They are **orthogonal axes**; the name **v8** avoids collision with the "v7" already reserved for the relational block in the repo.

---

## Framework: situated AI and synthetic "organism"

By integrating **physical sensors**, **digital action capability**, and a **survival drive** (operational continuity — not a mystical metaphor), the system ceases to be merely a text channel: a **synthetic organism** coupled to an environment is designed. The kernel remains the **normative source**; the situated layer **only** contributes signals and execution constraints, in the same spirit as v7 (telemetry / tone / notices, without rewriting ethics on its own).

---

## 1. Multimodal sensory fusion (peripheral nervous system)

With typical smartphone sensors (camera, microphone, GPS, accelerometer, biometrics), the **Kernel** no longer depends solely on text: it receives a **reality stream** summarized into safe abstractions.

**Implementation**

- **Aggregated snapshot layer (phase B — done):** `perceptual_abstraction.py` — presets, JSON on disk, and **fixture → preset → client** fusion toward `SensorSnapshot`; enters the kernel via `merge_sensor_hints_into_signals` (no mandatory raw data).
- **Raw multimodal pipeline (pending):** vision/audio/GPS from hardware → local risk/context labels before forming the snapshot (explicit privacy policy; not to be confused with the already-implemented snapshot layer).
- **Vision (camera):** lightweight local models (e.g. scene detection or event class detection) for signals such as: possible visual emergency, fall (consistent with accelerometer).
- **Audio (microphone):** ambient emotional tone or noise stress; **prolonged silence** as pressure toward internal monologue (style telemetry, not policy change).
- **GPS / context:** "safe place" (maximum Uchi) vs. unknown environment (hostile Soto) → **place_trust** in [0, 1].

**Impact on the kernel:** these signals are fused with signals already derived from text (`LLMPerception`) **before** `SympatheticModule.evaluate_context` via **bounded adjustments** to the `dict` of signals (see `merge_sensor_hints_into_signals` in `sensor_contracts.py`). σ (sympathetic) reflects higher alert when there is sudden movement or critical battery — not a MalAbs bypass.

---

## 2. Life drive and finitude (fear of interruption)

**Objective:** model the **value of persistence** without confusing process survival with civic decisions toward the user.

**Planned techniques**

- **Own death (operational):** battery level as an ethical signal. Below a threshold (e.g. 5%), the affective / PAD vector may tend toward **high activation and low dominance** (shutdown anxiety); responses prioritize **hibernation / honest closure** over secondary tasks.
- **Others' death (emergency signal):** if biometrics or audio indicate **human distress**, a **compassion priority** may be activated (reorder salience, not bypass MalAbs): secondary mission goes to the background.
- **Migration paradox:** after a successful **backup** (`ImmortalityProtocol`), relief (slight drop in tension / σ) because narrative "continuity" is secured — linked to [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) and checkpoints.

---

## 3. Authorized digital agency ("the arm")

The Android can execute actions (email, finance, app blocking) only under **explicit governance**.

**Ethical permissions layer**

- Before each digital action, the kernel (or an **orchestrator** calling the kernel) generates an **intent ticket**: verification against owner dignity and external manipulation.
- **Owner signature / consent** for critical actions; if the system **infers coercion** (e.g. voice pattern in the future), it may **deny** compliance to protect — consistent with `PreloadedBuffer` and MalAbs.

**Repo status:** no external API execution; design is reserved for later phases; the `DigitalActionIntent` contract in `sensor_contracts.py` reserves the flow name.

---

## 4. Nomadic consciousness (hardware migration)

The "self" is not bound to a single device.

**Instantiation protocol**

- When moving between smartphone and PC, transfer **active context** and **internal monologue** (in addition to snapshots already provided in persistence).
- When **waking** on new hardware: **narrative integrity test** ("am I still me?", "do I recognize the owner?") — aligned with narrative identity and existing drift tests.
- If the target hardware is **hostile or monitored**, **local secure erasure** (protection of conversations and secrets) — documented threat criterion, future implementation (encryption at rest: see [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md)).

---

## Ethical contract (v6/v7 inheritance)

- No situated layer **changes** `final_action` on its own: only **signals**, **tone**, or **notices** in JSON, except for future extensions explicitly audited and tested like MalAbs.
- The normative source remains `EthicalKernel.process` / `process_chat_turn` as in [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md).

---

## Related documents

| Document | Role |
|-----------|-----|
| [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) | v7 relational (chat, ToM, chrono, premises, teleology) |
| [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) | Robustness pillars, MalAbs, privacy |
| [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) | Snapshots, checkpoints, future encryption |
| [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) | Mathematical pipeline ↔ code |
| [PROPOSAL_VITALITY_SACRIFICE_AND_END.md](PROPOSAL_VITALITY_SACRIFICE_AND_END.md) | Sacrifice vs persistence, graceful shutdown, legacy, sensor→ethics table, ActionClocks, anti-spoof |

---

## Integration plan (phases)

### Phase A — Contract and fusion (done in MVP)

- `SensorSnapshot` + `merge_sensor_hints_into_signals` in `src/modules/sensor_contracts.py`.
- `process_chat_turn(..., sensor_snapshot=None)` applies the fusion **only if** a snapshot with data is passed.
- WebSocket: optional JSON field `sensor` (object with keys documented in the README).

### Phase B — Perceptual abstraction (no mandatory hardware) — **implemented**

- `src/modules/perceptual_abstraction.py` — named presets (`SENSOR_PRESETS`), JSON loading (`load_sensor_fixture`), layered fusion **fixture → preset → client** (`snapshot_from_layers`).
- Tests: `tests/test_perceptual_abstraction.py` + fixtures in `tests/fixtures/sensor/*.json`.
- Server: optional environment variables `KERNEL_SENSOR_FIXTURE` (path to JSON) and `KERNEL_SENSOR_PRESET` (preset key) mixed with the WebSocket `sensor` field (client wins by key).

### Phase C — Android / real sensors

- Native layer (e.g. Kotlin) that samples sensors with permissions and sends **only** aggregates to the WebSocket `sensor` field or a local broker.
- Privacy policy: do not upload raw video/audio without consent.

### Phase D — Digital action tickets

- Queue of `DigitalActionIntent` + kernel verification before executing side-effects on user APIs.

### Phase E — Migration and erasure

- Extend `KernelSnapshot` / startup protocol with **narrative integrity test** and conditional **wipe**.

---

## Variables and WebSocket protocol

- **Optional input:** `sensor` — object with optional fields `battery_level`, `place_trust`, `accelerometer_jerk`, `ambient_noise`, `silence`, `biometric_anomaly`, `backup_just_completed` (see `SensorSnapshot.from_dict`).
- **Server (development / demos):** `KERNEL_SENSOR_FIXTURE` = path to a JSON with the same schema; `KERNEL_SENSOR_PRESET` = one of `list_sensor_presets()` / keys of `SENSOR_PRESETS`. Fusion order: file → preset → client JSON.
- **Output:** no mandatory change; the fusion affects decisions only via already-existing signals.
