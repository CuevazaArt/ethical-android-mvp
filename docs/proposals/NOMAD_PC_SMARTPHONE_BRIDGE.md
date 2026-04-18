# First nomadic bridge: PC ↔ smartphone and per–hardware-class layers

This document sets the **frame** for nomadic capability between a **PC (brain / compute)** and a **smartphone (lightweight body / sensors)** without confusing the current MVP with the final deployment. It complements [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md), [PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md](PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md), and [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

---

## 1. What the “first bridge” is

Today the repository provides:

- **Transport:** WebSocket + HTTP on LAN (`CHAT_HOST`, `mobile.html`, checkpoints and conduct guide on session close).
- **Ethics:** the same `EthicalKernel` on the server; the phone **does not** replace the normative core.

Together this is the **first operational bridge** toward **PC–smartphone nomadic capability**: the same dialogue protocol, optional continuity on disk on the PC, and a base to add **sensor body** and **runtime handoffs** without redefining MalAbs.

Each **hardware class** (desktop, laptop, Android/iOS phone, future wearables, dedicated edge) will have **its own engineering** and **compatibility layers** to build: there is no single universal binary; there is a **shared contract** (messages, snapshot, HAL) and **per-platform adapters**.

---

## 2. Hardware classes and compatibility layers (to be built)

| Class | Typical role | Compatibility layers (examples, not exhaustive) |
|-------|--------------|--------------------------------------------------|
| **PC / workstation** | Full kernel, heavy LLM, on-disk checkpoints | Python 3.9+, `requirements.txt`, optional Ollama; OS firewall. |
| **Smartphone (browser)** | Lightweight client + **first sensor access via the web** (when the browser exposes APIs) | Same `mobile.html` / future extension; `sensor` object in WebSocket JSON ([README](../../README.md), v8). |
| **Smartphone (future native app)** | Low-level sensors, better latency, partial offline | Packaging contract (WebSocket/TLS), OS permissions, possible native bridge → JSON `sensor`. |
| **Other edge** | Small inference or relay only | [`conduct_guide_export`](../../src/modules/conduct_guide_export.py), distillation ([`context_distillation`](../../src/modules/context_distillation.py)), snapshot schema. |

**Principle:** **ethical logic** stays on the documented kernel paths; **compatibility layers** are transport, permissions, sensor format, network security, and packaging — each evolves per device class.

---

## 3. Immediate opportunity: diverse, coordinated perception (smartphone)

**Smartphone** hardware is the **nearest opportunity** for **first approximations** of **diverse, coordinated perception**:

- The protocol already allows a **`sensor`** object from the client (v8 situation: battery, noise, multimodal emergency cues, etc.).
- From the phone, in **thin-client** mode, those values can be **injected into the message** (when the UI or an intermediate layer fills them) and the kernel merges them into **sympathetic signals** without bypassing MalAbs.

**Current state:** `mobile.html` sends text; the **next product iteration** on this bridge is to enrich the mobile client to **map** available readings (web API or manual test input) to the `sensor` schema, and document per-browser limits.

---

## 4. Network scope and field testing

- **Today:** deployment is intended for a **trusted home LAN** (no TLS on the local hop; see [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md)).
- **Field testing on a safer network** (VPN, tunnel, TLS at a proxy, segmented network, etc.) is **pending operator policy** — enabled **when you choose**, so infrastructure hardening is not mixed with the same milestone as kernel ethical validation.

Until then, treat the LAN setup as a **controlled lab**, not open Internet production.

---

## 5. Cross-references

| Document | Related content |
|----------|-------------------|
| [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md) | Concrete PC + phone steps, firewall, `mobile.html` |
| [PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md](PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md) | HAL, dual runtime, transmutation |
| [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) | Sensor contract and situated layers |
| [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md) | P0–P3 path and operational risks |

---

*Ex Machina Foundation — PC–smartphone nomadic bridge; align substantive changes with CHANGELOG and HISTORY.*
