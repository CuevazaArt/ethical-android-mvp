# Situated existential organism (v8) — sensory fusion, vital drive, digital agency, migration

**Status:** discussion + **contract and fusion** in code (`sensor_contracts.py`, `perceptual_abstraction.py`, `process_chat_turn` / WebSocket + env `KERNEL_SENSOR_*`). **Does not replace** MalAbs, Bayes, buffer, or will.

**Relation to relational v7:** [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) covers **dialogue** (light ToM, subjective time, advisory premises, qualitative teleology). This document (v8) covers the **situated body**: sensors, hardware persistence, fear of interruption, digital action, and migration between devices. They are **orthogonal axes**; the **v8** name avoids collision with “v7” already reserved for the relational block in the repo.

---

## Framework: situated AI and synthetic “organism”

By integrating **physical sensors**, **digital action capacity**, and a **drive to survive** (operational continuity, not a mystical metaphor), the system stops being text-only: a **synthetic organism** coupled to an environment is designed. The kernel remains the **normative source**; the situated layer **only** contributes signals and execution constraints, in the same spirit as v7 (telemetry / tone / warnings, without rewriting ethics on its own).

---

## 1. Multimodal sensory fusion (peripheral nervous system)

With typical smartphone sensors (camera, microphone, GPS, accelerometer, biometrics), the **Kernel** no longer depends on text alone: it receives a **reality stream** summarized in safe abstractions.

**Implementation**

- **Aggregated snapshot layer (phase B — done):** `perceptual_abstraction.py` — presets, JSON on disk, and **fixture → preset → client** fusion into `SensorSnapshot`; enters the kernel via `merge_sensor_hints_into_signals` (no mandatory raw data).
- **Raw multimodal pipeline (pending):** vision/audio/GPS from hardware → local risk/context labels before forming the snapshot (explicit privacy policy; do not confuse with the already implemented snapshot layer).
- **Vision (camera):** lightweight local models (e.g. scene detection or event classes) for signals such as: possible visual emergency, fall (consistent with accelerometer).
- **Audio (microphone):** ambient emotional tone or noise stress; **prolonged silence** as pressure toward internal monologue (style telemetry, not policy change).
- **GPS / context:** “safe place” (maximum Uchi) vs unknown environment (hostile Soto) → **place_trust** in [0, 1].

**Kernel impact:** these signals merge with signals already derived from text (`LLMPerception`) **before** `SympatheticModule.evaluate_context` via **bounded** adjustments to the signals `dict` (see `merge_sensor_hints_into_signals` in `sensor_contracts.py`). σ (sympathetic) reflects higher alert when there is jerk motion or critical battery, not a MalAbs bypass.

---

## 2. Vital drive and finitude (fear of interruption)

**Objective:** model **persistence value** without confusing process survival with civil decisions toward the user.

**Planned techniques**

- **Own death (operational):** battery level as ethical signal. Below a threshold (e.g. 5%), affect vector / PAD may tend toward **high activation and low dominance** (“shutdown” anxiety); responses prioritize **honest hibernation / closure** over secondary tasks.
- **Others’ death (emergency signal):** if biometrics or audio indicate **human distress**, **compassionate priority** may activate (reorder salience, not skip MalAbs): secondary mission moves to the background.
- **Migration paradox:** after successful **backup** (`ImmortalityProtocol`), relief (slight tension / σ drop) because narrative “continuity” is secured — linked to [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) and checkpoints.

---

## 3. Authorized digital agency (the “arm”)

The Android can execute actions (email, finance, app lock) only under **explicit governance**.

**Ethical permission layer**

- Before each digital action, the kernel (or an **orchestrator** that calls the kernel) generates an **intent ticket**: check against owner dignity and external manipulation.
- **Owner signature / consent** for critical actions; if the system **infers coercion** (e.g. voice pattern in the future), it may **deny** obedience to protect — consistent with `PreloadedBuffer` and MalAbs.

**Status in repo:** no external API execution; design left for later phases; `DigitalActionIntent` contract in `sensor_contracts.py` reserves the flow name.

---

## 4. Nomad consciousness (hardware migration)

The “self” is not tied to one device.

**Instantiation protocol**

- When moving between smartphone and PC, transfer **active context** and **internal monologue** (in addition to snapshots already planned in persistence).
- On **wake** on new hardware: **narrative integrity test** (“am I still me?”, “do I recognize the owner?”) — aligned with narrative identity and existing drift tests.
- If destination hardware is **hostile or monitored**, **secure local wipe** (protect conversations and secrets) — documented threat criterion, future implementation (encryption at rest: see [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md)).

---

## Ethical contract (v6/v7 inheritance)

- No situated layer **changes** `final_action` on its own: only **signals**, **tone**, or **warnings** in JSON, unless future extensions are explicitly audited and tested like MalAbs.
- Normative source remains `EthicalKernel.process` / `process_chat_turn` as in [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md).

---

## Related documents

| Document | Role |
|-----------|-----|
| [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) | Relational v7 (chat, ToM, chrono, premises, teleology) |
| [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) | Robustness pillars, MalAbs, privacy |
| [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) | Snapshots, checkpoints, future encryption |
| [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) | Math ↔ code pipeline |
| [PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md](PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md) | Sacrifice vs persistence, graceful shutdown, legacy, sensor→ethics table, ActionClocks, antispoof |

---

## Integration plan (phases)

### Phase A — Contract and fusion (done in MVP)

- `SensorSnapshot` + `merge_sensor_hints_into_signals` in `src/modules/sensor_contracts.py`.
- `process_chat_turn(..., sensor_snapshot=None)` applies fusion **only if** a snapshot with data is passed.
- WebSocket: optional JSON field `sensor` (keys documented in README).

### Phase B — Perceptual abstraction (no mandatory hardware) — **implemented**

- `src/modules/perceptual_abstraction.py` — named presets (`SENSOR_PRESETS`), JSON load (`load_sensor_fixture`), layered fusion **fixture → preset → client** (`snapshot_from_layers`).
- Tests: `tests/test_perceptual_abstraction.py` + fixtures in `tests/fixtures/sensor/*.json`.
- Server: optional env `KERNEL_SENSOR_FIXTURE` (path to JSON) and `KERNEL_SENSOR_PRESET` (preset key) merged with WebSocket `sensor` field (client wins per key).

### Phase C — Android / real sensors

- Native layer (e.g. Kotlin) that samples sensors with permissions and sends **only** aggregates to WebSocket `sensor` or a local broker.
- Privacy policy: no raw video/audio upload without consent.

### Phase D — Digital action tickets

- Queue of `DigitalActionIntent` + kernel verification before executing user API side effects.

### Phase E — Migration and wipe

- Extend `KernelSnapshot` / boot protocol with **narrative integrity test** and conditional **wipe**.

---

## Variables and WebSocket protocol

- **Optional input:** `sensor` — object with optional fields `battery_level`, `place_trust`, `accelerometer_jerk`, `ambient_noise`, `silence`, `biometric_anomaly`, `backup_just_completed` (see `SensorSnapshot.from_dict`).
- **Server (development / demos):** `KERNEL_SENSOR_FIXTURE` = path to JSON with same schema; `KERNEL_SENSOR_PRESET` = one of `list_sensor_presets()` / `SENSOR_PRESETS` keys. Fusion order: file → preset → client JSON.
- **Output:** no mandatory change; fusion affects decisions only via existing signals.
