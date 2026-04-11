# First nomadic bridge: PC ↔ smartphone and layers by hardware class

This document sets the **framework** for nomadic capability between **PC (brain / compute)** and **smartphone (light body / sensors)**, without conflating the current MVP with the final deployment. Complements [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md), [PROPOSAL_NOMADIC_CONSCIOUSNESS_HAL.md](PROPOSAL_NOMADIC_CONSCIOUSNESS_HAL.md), and [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

---

## 1. What the "first bridge" is

Today the repository offers:

- **Transport:** WebSocket + HTTP on LAN (`CHAT_HOST`, `mobile.html`, checkpoints and conduct guide on session close).
- **Ethics:** the same `EthicalKernel` on the server; the mobile **does not** replace the normative core.

That ensemble is the **first operational bridge** toward **PC–smartphone nomadic capability**: same dialogue protocol, optional disk continuity on the PC, and foundation to add **sensory body** and **runtime jumps** without redefining MalAbs.

Each **hardware class** (desktop PC, laptop, Android/iOS smartphone, future wearables, dedicated edge) will have **its specific development** and **its compatibility layers** to build: there is no single universal binary; there is a **common contract** (messages, snapshot, HAL) and **platform adapters**.

---

## 2. Hardware classes and compatibility layers (to develop)

| Class | Typical role | Compatibility layers (examples, not exhaustive) |
|-------|------------|---------------------------------------------------|
| **PC / workstation** | Full kernel, heavy LLM, disk checkpoints | Python 3.9+, `requirements.txt` dependencies, optional Ollama; OS firewall. |
| **Smartphone (browser)** | Light client + **first sensor access via web** (when browser exposes APIs) | Same `mobile.html` page / future extension; `sensor` object in WebSocket JSON ([README](README.md), v8). |
| **Smartphone (future native app)** | Low-level sensors, better latency, partial offline | Contract for packaging (WebSocket/TLS), OS permissions, possible native bridge → JSON `sensor`. |
| **Other edge** | Small inference only or relay | [conduct_guide_export](../src/modules/conduct_guide_export.py), distillation ([context_distillation](../src/modules/context_distillation.py)), snapshot schema. |

**Principle:** the **ethical logic** remains on the kernel's documented paths; the **compatibility layers** are transport, permissions, sensor format, network security, and packaging — each evolves per device class.

---

## 3. Immediate opportunity: diverse and coordinated sensory perception (smartphone)

The **smartphone** hardware is the **immediate opportunity** for the **first approaches** to **diverse and coordinated sensory perception**:

- The protocol already admits a **`sensor`** object in the client (v8 situation: battery, noise, multimodal emergency signals, etc.).
- From the mobile, in **thin client** mode, those values can be **injected into the message** (when the UI or an intermediate layer fills them) and the kernel fuses them into **sympathetic signals** with no MalAbs bypass.

**Current status:** `mobile.html` sends text; the **next product iteration** on this bridge is to enrich the mobile client to **map** available readings (web API, or manual test input) to the `sensor` schema, and document limits per browser.

---

## 4. Network scope and field testing

- **Today:** deployment designed for **trusted home LAN** (no TLS on the local link; see [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md)).
- **Field testing on a more secure network** (VPN, tunnel, TLS terminated on proxy, segmented network, etc.) remains **pending operator decision** — will be activated **when indicated**, to avoid mixing kernel ethical validation with infrastructure hardening in the same milestone.

Until then, documentation treats the LAN environment as a **controlled lab**, not as production exposed to open Internet.

---

## 5. Cross-references

| Document | Related content |
|-----------|------------------------|
| [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md) | Concrete steps PC + mobile, firewall, `mobile.html` |
| [PROPOSAL_NOMADIC_CONSCIOUSNESS_HAL.md](PROPOSAL_NOMADIC_CONSCIOUSNESS_HAL.md) | HAL, dual runtime, transmutation |
| [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) | Sensory contract and situated layers |
| [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md) | P0–P3 route and operational risks |

---

*Ex Machina Foundation — nomadic PC–smartphone bridge; align with CHANGELOG and HISTORY.*
