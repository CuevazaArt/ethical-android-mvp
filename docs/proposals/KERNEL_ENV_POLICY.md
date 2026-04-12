# `KERNEL_*` environment policy (Issue 7)

**Purpose:** Reduce **accidental combinatorics** of feature flags. The codebase is a **research lab**; this document defines **nominal profiles**, **groupings**, **combinations to avoid or treat as experimental**, and a **deprecation posture** without breaking existing env names.

**Canonical profile bundles:** [`src/runtime_profiles.py`](../src/runtime_profiles.py) — use these for demos, CI smoke, and operator docs. **`ETHOS_RUNTIME_PROFILE`** (e.g. `lan_operational`, `situated_v8_lan_demo`) applies a bundle at **chat server startup**; explicit env vars **win** over profile defaults for each key. **CI** runs the full `pytest tests/` suite, including **`tests/test_runtime_profiles.py`** (health + WebSocket roundtrip for **every** named profile). **Perception hardening (Fase 1):** nominal bundle **`perception_hardening_lab`** enables light risk tier, cross-check, uncertainty→delib, parse fail-local, and `light_risk_tier` in chat JSON. **Phase 2 bus spike:** **`phase2_event_bus_lab`** sets `KERNEL_EVENT_BUS=1` (ADR 0006).

**Full flag catalog:** [README](README.md) (WebSocket / runtime sections) and module docstrings in `src/chat_server.py`, `src/persistence/checkpoint.py`, etc.

---

## 1. Flag families (mental model)

| Family | Prefix / examples | Role |
|--------|-------------------|------|
| **Chat JSON telemetry** | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | Omit or include **UX fields** in WebSocket payloads — **no** ethical veto. |
| **Governance / hub** | `KERNEL_MORAL_HUB_*`, `KERNEL_DEONTIC_GATE`, `KERNEL_LOCAL_SOVEREIGNTY`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS` | Demos, audits, mock court — **not** on-chain consensus ([GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md)). `KERNEL_LOCAL_SOVEREIGNTY=0` disables L0 heuristic scan on JSON calibration payloads (`local_sovereignty.py`). |
| **Persistence / handoff** | `KERNEL_CHECKPOINT_*`, `KERNEL_CHECKPOINT_FERNET_KEY`, `KERNEL_CONDUCT_GUIDE_*` | Disk / encryption / export — **confidentiality**, not ethics. |
| **Perception / sensors** | `KERNEL_SENSOR_*`, `KERNEL_MULTIMODAL_*`, `KERNEL_VITALITY_*`, `KERNEL_PERCEPTION_UNCERTAINTY_DELIB`, `KERNEL_PERCEPTION_UNCERTAINTY_MIN`, `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`, `KERNEL_PERCEPTION_FAILSAFE`, `KERNEL_PERCEPTION_FAILSAFE_BLEND`, `KERNEL_LIGHT_RISK_CLASSIFIER`, `KERNEL_PERCEPTION_CROSS_CHECK`, `KERNEL_CROSS_CHECK_HIGH_MAX_CALM`, `KERNEL_CROSS_CHECK_HIGH_MIN_RISK`, `KERNEL_CROSS_CHECK_MED_MAX_CALM`, `KERNEL_CROSS_CHECK_MED_MIN_RISK`, `KERNEL_CHAT_INCLUDE_LIGHT_RISK` | Bounds and tuning — **heuristic** ([INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)). **`KERNEL_PERCEPTION_UNCERTAINTY_*`:** when `DELIB=1` and coercion uncertainty ≥ `MIN` (default `0.35`), **`D_fast` → `D_delib`**. **`KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`:** on `json_decode_error` / `non_object_payload` / `empty_response`, skip trusting empty parsed dict and go straight to local heuristics while retaining **parse issue codes** in `coercion_report`. **`KERNEL_PERCEPTION_FAILSAFE`:** when coercion diagnostics indicate unreliable LLM JSON, blend numeric perception toward cautious priors (`perception_schema.py`; default on). **`KERNEL_LIGHT_RISK_CLASSIFIER`:** offline lexical **low/medium/high** tier (not MalAbs). **`KERNEL_PERCEPTION_CROSS_CHECK`:** if tier is medium/high and numeric perception looks “too calm” vs that tier, set `cross_check_discrepancy` and raise uncertainty (pairs with uncertainty→delib). **`KERNEL_CHAT_INCLUDE_LIGHT_RISK`:** add `light_risk_tier` to WebSocket JSON (default off). |
| **MalAbs lexical (chat)** | `KERNEL_MALABS_LEET_FOLD`, `KERNEL_MALABS_STRIP_BIDI` | Digit/symbol → letter fold and bidirectional-override strip before substring MalAbs (`input_trust.normalize_text_for_malabs`; default **on**). |
| **MalAbs semantic (chat)** | `KERNEL_SEMANTIC_CHAT_GATE`, `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK`, … | **Defaults:** gate and hash fallback **on** when unset — embedding tier after lexical; hash vectors if Ollama unavailable ([MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md), ADR 0003). Set `GATE=0` for lexical-only. |
| **LLM / variability** | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GENERATIVE_*` (`KERNEL_GENERATIVE_LLM` = parse extra candidates from perception JSON) | Tone and candidate lists — MalAbs still gates actions. |
| **Poles (linear)** | `KERNEL_POLE_LINEAR_CONFIG` | Path to JSON for `LinearPoleEvaluator` (ADR 0004); default `pole_linear_default.json` in package. |
| **Input trust (embedding transport)** | `KERNEL_SEMANTIC_CHAT_EMBED_MODEL`, `KERNEL_SEMANTIC_CHAT_SIM_*`, `KERNEL_SEMANTIC_CHAT_LLM_ARBITER`, `KERNEL_SEMANTIC_EMBED_*` (timeouts, circuit, hash dim/scope in `semantic_embedding_client`) | Tuning for the semantic tier ([`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md), ADR 0003). Gate + hash defaults are summarized in **MalAbs semantic** row above. |
| **Psi Sleep feedback (lab)** | `KERNEL_FEEDBACK_CALIBRATION`, `KERNEL_PSI_SLEEP_UPDATE_MIXTURE`, `KERNEL_FEEDBACK_CALIBRATION_MIN_SAMPLES`, `KERNEL_PSI_SLEEP_FEEDBACK_BLEND` | WebSocket `operator_feedback` records labels for the last turn’s regime; `execute_sleep` may apply a **bounded** `hypothesis_weights` nudge (genome drift cap). See [`PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md`](PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md) (B1). |
| **Guardian Angel** | `KERNEL_GUARDIAN_MODE`, `KERNEL_GUARDIAN_ROUTINES`, `KERNEL_GUARDIAN_ROUTINES_PATH`, `KERNEL_CHAT_INCLUDE_GUARDIAN`, `KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES` | Protective tone + optional JSON care routines (hints only); [`landing/public/guardian.html`](../landing/public/guardian.html). |
| **Bayesian mixture (lab)** | `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` | When `1`, nudges discrete mixture weights from recent `NarrativeMemory` episodes **in the same context** before scoring; default **off** (fixed mixture). |
| **Temporal horizon prior** | `KERNEL_TEMPORAL_HORIZON_PRIOR`, `KERNEL_TEMPORAL_HORIZON_ALPHA`, `KERNEL_TEMPORAL_HORIZON_WEEKS_DAYS` | After episodic step: extra nudge from weeks/long-arc signals ([`TEMPORAL_PRIOR_HORIZONS.md`](TEMPORAL_PRIOR_HORIZONS.md), ADR 0005); default **off**. |
| **Nomad / identity** | `KERNEL_NOMAD_*`, `KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY` | Lab simulation + JSON — **stubs** where noted in docs. |
| **Metaplan / drives (advisory)** | `KERNEL_METAPLAN_HINT`, `KERNEL_METAPLAN_DRIVE_FILTER`, `KERNEL_METAPLAN_DRIVE_EXTRA` | Owner goals in LLM tone; optional filter of `drive_intents` vs goal wording; optional coherence hint — **no** ethics veto. |
| **Swarm stub (lab)** | `KERNEL_SWARM_STUB` | Enables optional use of `swarm_peer_stub` digest helpers in tooling — **no** P2P stack, **no** kernel change ([`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md)). |
| **Extension seam (Phase 2)** | `KERNEL_EVENT_BUS` | When `1`, `EthicalKernel` builds `KernelEventBus` and publishes **`kernel.decision`** / **`kernel.episode_registered`** (sync, best-effort handlers). See [ADR 0006](../adr/0006-phase2-core-boundary-and-event-bus.md), [`PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md`](PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md), profile **`phase2_event_bus_lab`**. |

---

## 2. Unsupported or “lab only” combinations

These are **not** forbidden by code, but **not CI-guaranteed** unless a profile or test is added:

| Pattern | Risk |
|---------|------|
| **Many `KERNEL_CHAT_INCLUDE_*=0`** plus **full relational** expectations | Clients may assume keys exist; document minimal JSON for your UI. |
| **`KERNEL_LIGHTHOUSE_KB_PATH` unset** + **`KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`** | Lighthouse may no-op; verify fixture path for demos. JSON schema and limits: [LIGHTHOUSE_KB.md](LIGHTHOUSE_KB.md). |
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

## 4. Relation to [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md)

Section **4** lists **nominal profiles**; this file is the **policy** layer (what “unsupported” means, how families fit together). Issue 7 acceptance: ESTRATEGIA updated + CI green on `tests/test_runtime_profiles.py`.

---

*MoSex Macchina Lab — critique roadmap Issue 7.*
