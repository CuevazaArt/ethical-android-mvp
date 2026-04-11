# `KERNEL_*` environment policy (Issue 7)

**Purpose:** Reduce **accidental combinatorics** of feature flags. The codebase is a **research lab**; this document defines **nominal profiles**, **groupings**, **combinations to avoid or treat as experimental**, and a **deprecation posture** without breaking existing env names.

**Canonical profile bundles:** [`src/runtime_profiles.py`](../src/runtime_profiles.py) — use these for demos, CI smoke, and operator docs.

**Full flag catalog:** [README](../README.md) (WebSocket / runtime sections) and module docstrings in `src/chat_server.py`, `src/persistence/checkpoint.py`, etc.

---

## 1. Flag families (mental model)

| Family | Prefix / examples | Role |
|--------|-------------------|------|
| **Chat JSON telemetry** | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | Omit or include **UX fields** in WebSocket payloads — **no** ethical veto. |
| **Governance / hub** | `KERNEL_MORAL_HUB_*`, `KERNEL_DEONTIC_GATE`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS` | Demos, audits, mock court — **not** on-chain consensus ([GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md)). |
| **Persistence / handoff** | `KERNEL_CHECKPOINT_*`, `KERNEL_CHECKPOINT_FERNET_KEY`, `KERNEL_CONDUCT_GUIDE_*` | Disk / encryption / export — **confidentiality**, not ethics. |
| **Perception / sensors** | `KERNEL_SENSOR_*`, `KERNEL_MULTIMODAL_*`, `KERNEL_VITALITY_*` | Bounds and tuning — **heuristic** ([INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)). |
| **LLM / variability** | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GUARDIAN_MODE`, `KERNEL_GENERATIVE_*` | Tone and candidate lists — MalAbs still gates actions. |
| **Nomad / identity** | `KERNEL_NOMAD_*`, `KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY` | Lab simulation + JSON — **stubs** where noted in docs. |

---

## 2. Unsupported or “lab only” combinations

These are **not** forbidden by code, but **not CI-guaranteed** unless a profile or test is added:

| Pattern | Risk |
|---------|------|
| **Many `KERNEL_CHAT_INCLUDE_*=0`** plus **full relational** expectations | Clients may assume keys exist; document minimal JSON for your UI. |
| **`KERNEL_LIGHTHOUSE_KB_PATH` unset** + **`KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`** | Lighthouse may no-op; verify fixture path from repo root for demos. |
| **`KERNEL_MORAL_HUB_PUBLIC=0`** but enabling **DAO WebSocket vote paths** that assume hub | Use `hub_dao_demo` or `moral_hub_extended` as baseline. |
| **`KERNEL_API_DOCS=1`** on **LAN bind** (`0.0.0.0`) | Exposes OpenAPI — intentional only for trusted networks ([SECURITY.md](SECURITY.md)). |
| **Arbitrary** `KERNEL_SENSOR_FIXTURE` + **`KERNEL_SENSOR_PRESET`** + client `sensor` | Merge order is documented; conflicting keys confuse debugging. |

**Rule of thumb:** if it is not a **named profile** in `runtime_profiles.py` and not covered by a **dedicated test**, treat it as **experimental**.

---

## 3. Deprecation posture (future)

- **Today:** no `KERNEL_*` names are removed; README remains the exhaustive list for edge flags.
- **Future:** redundant toggles may be **aliased** (same behavior, one canonical name) with a **CHANGELOG** entry and a **transition window** — prefer **profiles** over one-off env soup for new features.
- **New features:** add **tests** + consider a **profile slice** if the feature is demo-critical.

---

## 4. Relation to [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md)

Section **4** lists **nominal profiles**; this file is the **policy** layer (what “unsupported” means, how families fit together). Issue 7 acceptance: ESTRATEGIA updated + CI green on `tests/test_runtime_profiles.py`.

---

*MoSex Macchina Lab — critique roadmap Issue 7.*
