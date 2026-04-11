# Nomadic instantiation — HAL, existential serialization, and dual runtime

**Status:** design + **code hooks** in `hardware_abstraction.py` and `existential_serialization.py` (no real encryption or P2P; see [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md)).  
**Relationship:** extends [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) (NomadIdentity) and the current persistence layer (`KernelSnapshotV1`, `ImmortalityProtocol`).  
**Operational PC–smartphone bridge:** [NOMAD_PC_SMARTPHONE_BRIDGE.md](../NOMAD_PC_SMARTPHONE_BRIDGE.md) (layers by hardware class, sensors, network).

---

## 1. EthosContainer (logic vs. language)

| Component | Content | In repo today |
|------------|-----------|-------------|
| **Ethical core (portable)** | Python + NumPy; MalAbs, buffer, narrative, mock DAO | `src/kernel.py`, `src/modules/*` |
| **Language layer (polymorphic)** | Heavy LLM on server vs. quantized on mobile | `LLMModule` / `resolve_llm_mode`; **no** embedded GGUF |
| **State record** | Snapshot + monologue / PAD / STM (vision) | `KernelSnapshotV1`, `WorkingMemory` not persisted in snapshot |

The production **encrypted container** is **future work** (cryptography layer on top of the same DTO as the checkpoint).

---

## 2. Transmutation protocol (4 phases)

| Phase | Name | Intended behavior | Code stub |
|------|--------|---------------------------|----------------|
| **A** | Encapsulation | Ψ Sleep, serialize, (encrypt), continuity token | `TransmutationPhase.A`, `build_continuity_token_stub` |
| **B** | Handshake | P2P, DAO validation, transfer | Documented contract only |
| **C** | Sensory adaptation | HAL discovers sensors, adjusts clock | `HardwareContext`, `apply_hardware_context` |
| **D** | Narrative integrity | Self-query from memory; report to owner | `narrative_integrity_self_check_stub` |

---

## 3. Dual runtime (satellite vs. autonomous)

- **Satellite mode:** the mobile device acts as body/sensor; heavy compute on the server (requires local link).  
- **Autonomous mode:** local inference (e.g. 8B GGUF); maximum privacy, battery cost.  
- **Automatic jump:** if the local link is weak, a **continuity** policy (migrate compute to the device) — **not implemented**; would depend on network + battery metrics (HAL).

---

## 4. Design answers (open questions)

### Migrate at 10% battery or "die" deleting data?

**Recommended hybrid:** (1) If a **secure channel** to the owner's device exists **and** the DAO authorizes the instance, attempt migration with a **critical battery warning** (the "self" may degrade functions, not be erased). (2) If there is **no trusted destination** or an **attack** is detected, **graceful shutdown** + erasure of **keys** and encrypted material (not necessarily the entire DAO audit trail — configurable). Policy via `KERNEL_NOMAD_*` (future).

### How to explain "less intelligent" but more sensitive?

Narrative transparency: *lighter model*, *higher latency in deep reasoning*, *greater local sensory resolution*. The tone can be **more sober** without being patronizing: it is a change in **capability**, not in dignity.

### DAO with GPS or just hardware ID?

By default: **hardware ID** (or device class hash) + migration type. **GPS** only with explicit owner **opt-in** and an audit policy (privacy vs. traceability).

### Partial deactivation vs. low-power monologue?

Allow **partial sleep**: light Ψ, without shutting down identity; **low-power monologue** when the user does not require active presence. Avoids burning battery with continuous inference; configurable.

---

## 5. Environment variables (MVP code)

| Variable | Default | Effect |
|----------|---------|--------|
| `KERNEL_NOMAD_SIMULATION` | off | WebSocket `nomad_simulate_migration` applies HAL + `nomad` response |
| `KERNEL_NOMAD_MIGRATION_AUDIT` | off | After simulation (or `simulate_nomadic_migration`), **DAO** line `NomadicMigration {...}` |

**HTTP:** `GET /nomad/migration` describes the protocol (no session).

---

## 6. References

- [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) — snapshot, future encryption  
- [nomad_identity.py](../../src/modules/nomad_identity.py) — immortality bridge  
- [existential_serialization.py](../../src/modules/existential_serialization.py), [hardware_abstraction.py](../../src/modules/hardware_abstraction.py)

*Ex Machina Foundation — nomadic consciousness; kernel ethical contract unchanged.*
