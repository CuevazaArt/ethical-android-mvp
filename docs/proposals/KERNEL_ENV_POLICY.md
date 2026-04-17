# `KERNEL_*` environment policy (Issue 7)

**Purpose:** Reduce **accidental combinatorics** of feature flags. The codebase is a **research lab**; this document defines **nominal profiles**, **groupings**, **combinations to avoid or treat as experimental**, and a **deprecation posture** without breaking existing env names.

### Implementation status (April 2026)

| Piece | Location |
|-------|----------|
| Partition + rules | [`src/validators/env_policy.py`](../../src/validators/env_policy.py) — `SUPPORTED_COMBOS`, `collect_env_violations()`, `validate_kernel_env()`, `DEPRECATION_ROADMAP` |
| Typed cross-flag rules | [`src/validators/kernel_public_env.py`](../../src/validators/kernel_public_env.py) — `KernelPublicEnv.consistency_violations()` |
| Chat startup | [`src/chat_server.py`](../../src/chat_server.py) — validation after profile merge |
| Regression | [`tests/test_env_policy.py`](../../tests/test_env_policy.py) — strict rejects bad combos; `warn`/`off` paths; partition = `runtime_profiles` |
| CI | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) **windows-smoke** — `tests/test_runtime_profiles.py` + `tests/test_env_policy.py` |
| Shell | `python -m src.cli check-config` / `ethos config` (see [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md)) |

**Remaining (not this milestone):** single-prefix rename for all LLM-related `KERNEL_*` knobs — [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §3; partial mitigation `KERNEL_LLM_GLOBAL_DEFAULT_POLICY` ([PROPOSAL_LLM_INTEGRATION_TRACK.md](PROPOSAL_LLM_INTEGRATION_TRACK.md) G-04).

---

**Canonical profile bundles:** [`src/runtime_profiles.py`](../../src/runtime_profiles.py) — use these for demos, CI smoke, and operator docs. **`ETHOS_RUNTIME_PROFILE`** (e.g. `lan_operational`, `situated_v8_lan_demo`) applies a bundle at **chat server startup**; explicit env vars **win** over profile defaults for each key. **CI** runs the full `pytest tests/` suite, including **`tests/test_runtime_profiles.py`** (health + WebSocket roundtrip for **every** named profile) and **`tests/test_env_policy.py`** (partition check + zero rule violations per nominal profile). **Perception hardening (Fase 1):** nominal bundle **`perception_hardening_lab`** enables light risk tier, cross-check, uncertainty→delib, parse fail-local, and `light_risk_tier` in chat JSON. **LLM integration lab:** **`llm_integration_lab`** turns on semantic MalAbs (hash fallback) + generative candidates from perception JSON (`KERNEL_GENERATIVE_LLM`). **LLM staging (conservative fallbacks):** **`llm_staging_conservative`** sets perception `fast_fail`, global verbal `canned_safe`, monologue `annotate_degraded` — see [PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md). **Phase 2 bus spike:** **`phase2_event_bus_lab`** sets `KERNEL_EVENT_BUS=1` (ADR 0006).

**Rule validation (not full Cartesian enumeration):** [`src/validators/env_policy.py`](../../src/validators/env_policy.py) defines **`SUPPORTED_COMBOS`** (`production` / `demo` / `lab`) as a **partition** of named profiles, **`collect_env_violations()`** for inconsistent flag *pairs* (e.g. mock court without judicial escalation), and **`validate_kernel_env()`** at chat import time. **`python -m src.cli check-config`** (optionally **`--strict`**) runs the same partition + consistency checks from the shell. **Default:** when `KERNEL_ENV_VALIDATION` is **unset**, validation mode is **`strict`** (fail fast on violations). When `ETHOS_RUNTIME_PROFILE` is set, [`apply_named_runtime_profile_to_environ()`](../../src/runtime_profiles.py) may still set **`warn`** or **`strict`** via [`default_env_validation_for_profile()`](../../src/validators/env_policy.py) if validation remains unset after merging the profile dict (**lab** → `warn`, **demo/production** → `strict`). Set **`warn`** or **`off`** explicitly if you need a different mode. This does not prove every arbitrary `KERNEL_*` combination is safe — only **nominal profiles** are CI-guaranteed **viable** (no rule violations).

**Typed layer (Pydantic):** cross-flag rules are evaluated on [`KernelPublicEnv`](../../src/validators/kernel_public_env.py) — see [KERNEL_ENV_TYPED_PUBLIC_API.md](KERNEL_ENV_TYPED_PUBLIC_API.md) for phased migration and CI vs production notes.

**Operator cockpit:** `ethos config` (see [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) § Configuration cockpit CLI) groups live env by family, flags experimental combinations, and scores overlap with nominal profiles — use alongside `validate_kernel_env()`.

**Full flag catalog:** [README](README.md) (WebSocket / runtime sections) and module docstrings in `src/chat_server.py`, `src/persistence/checkpoint.py`, etc.

**Docker deploy:** [production-ish compose merge](../../deploy/COMPOSE_PRODISH.md) (`docker-compose.prodish.yml`, optional `docker-compose.metrics.yml`, `.env` for secrets; build context excludes `.env` via `.dockerignore`).

---

## 1. Flag families (mental model)

| Family | Prefix / examples | Role |
|--------|-------------------|------|
| **Chat JSON telemetry** | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | Omit or include **UX fields** in WebSocket payloads — **no** ethical veto. |
| **Chat async bridge** | `KERNEL_CHAT_TURN_TIMEOUT`, `KERNEL_CHAT_THREADPOOL_WORKERS`, `KERNEL_CHAT_JSON_OFFLOAD` | Per-turn **async** deadline (JSON `chat_turn_timeout`); optional dedicated thread pool; default **on** JSON offload so WebSocket response build (incl. optional `KERNEL_LLM_MONOLOGUE`) does not block the event loop ([ADR 0002](../adr/0002-async-orchestration-future.md), [PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md](PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md)). |
| **Governance / hub** | `KERNEL_MORAL_HUB_*`, `KERNEL_DEONTIC_GATE`, `KERNEL_LOCAL_SOVEREIGNTY`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS`, `KERNEL_LAN_GOVERNANCE_MERGE_WS`, `KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS`, `KERNEL_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES`, `KERNEL_AUDIT_SIDECAR_PATH` | Demos, audits, mock court — **not** on-chain consensus ([GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md)). `KERNEL_LOCAL_SOVEREIGNTY=0` disables L0 heuristic scan on JSON calibration payloads (`local_sovereignty.py`). **`KERNEL_DAO_INTEGRITY_AUDIT_WS`:** WebSocket `integrity_alert`. **`KERNEL_LAN_GOVERNANCE_MERGE_WS`:** enables LAN batch handlers (`lan_governance_integrity_batch`, `lan_governance_dao_batch`, `lan_governance_judicial_batch`, `lan_governance_mock_court_batch`), the versioned envelope `lan_governance_envelope` (`schema=lan_governance_envelope_v1`) that routes by `kind`, and the hub coordinator `lan_governance_coordinator` (`schema=lan_governance_coordinator_v1`); see `moral_hub.py`, `lan_governance_envelope.py`, `lan_governance_coordinator.py`, and `chat_server.py`. **`KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS` / `KERNEL_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES`:** per-session replay cache bounds for duplicate envelope ACKs (`ack=already_seen`) with TTL/LRU eviction. **`KERNEL_AUDIT_SIDECAR_PATH`:** append-only JSONL mirror of `MockDAO.register_audit` rows for operator log separation (not a signed service). |
| **Persistence / handoff** | `KERNEL_CHECKPOINT_*`, `KERNEL_CHECKPOINT_FERNET_KEY`, `KERNEL_CONDUCT_GUIDE_*` | Disk / encryption / export — **confidentiality**, not ethics. |
| **Perception / sensors** | `KERNEL_SENSOR_*`, `KERNEL_MULTIMODAL_*`, `KERNEL_VITALITY_*`, optional tri-lobe **`KERNEL_PERCEPTIVE_LOBE_PROBE_URL`** (async `httpx` GET in `kernel_lobes.perception_lobe` — unset = no outbound probe), `KERNEL_PERCEPTION_CIRCUIT`, `KERNEL_PERCEPTION_UNCERTAINTY_DELIB`, `KERNEL_PERCEPTION_UNCERTAINTY_MIN`, `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`, `KERNEL_PERCEPTION_FAILSAFE`, `KERNEL_PERCEPTION_FAILSAFE_BLEND`, `KERNEL_LIGHT_RISK_CLASSIFIER`, `KERNEL_PERCEPTION_CROSS_CHECK`, `KERNEL_PERCEPTION_DUAL_VOTE`, `KERNEL_PERCEPTION_DUAL_DISCREPANCY_MIN`, `KERNEL_PERCEPTION_DUAL_TEMP_SECOND`, `KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL`, `KERNEL_CROSS_CHECK_HIGH_MAX_CALM`, `KERNEL_CROSS_CHECK_HIGH_MIN_RISK`, `KERNEL_CROSS_CHECK_MED_MAX_CALM`, `KERNEL_CROSS_CHECK_MED_MIN_RISK`, `KERNEL_CHAT_INCLUDE_LIGHT_RISK` | Bounds and tuning — **heuristic** ([INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)). **`KERNEL_PERCEPTION_CIRCUIT`:** when `1` (default), consecutive stressed `coercion_report` turns trip **metacognitive doubt** (`perception_circuit.py`): `gray_zone` communication, WebSocket `metacognitive_doubt`, HubAudit line, Prometheus counter. Set `0` to disable. **`KERNEL_PERCEPTION_UNCERTAINTY_*`:** when `DELIB=1` and coercion uncertainty ≥ `MIN` (default `0.35`), **`D_fast` → `D_delib`**. **`KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`:** on `json_decode_error` / `non_object_payload` / `empty_response`, skip trusting empty parsed dict and go straight to local heuristics while retaining **parse issue codes** in `coercion_report`. **`KERNEL_PERCEPTION_FAILSAFE`:** when coercion diagnostics indicate unreliable LLM JSON, blend numeric perception toward cautious priors (`perception_schema.py`; default on). **`KERNEL_LIGHT_RISK_CLASSIFIER`:** offline lexical **low/medium/high** tier (not MalAbs). **`KERNEL_PERCEPTION_CROSS_CHECK`:** if tier is medium/high and numeric perception looks “too calm” vs that tier, set `cross_check_discrepancy` and raise uncertainty (pairs with uncertainty→delib). **`KERNEL_PERCEPTION_DUAL_VOTE`:** second LLM perception sample (temperature / optional second Ollama model); large hostility or risk gap vs primary raises coercion uncertainty (`perception_dual_vote.py`). **`KERNEL_CHAT_INCLUDE_LIGHT_RISK`:** add `light_risk_tier` to WebSocket JSON (default off). |
| **MalAbs lexical (chat)** | `KERNEL_MALABS_LEET_FOLD`, `KERNEL_MALABS_STRIP_BIDI` | Digit/symbol → letter fold and bidirectional-override strip before substring MalAbs (`input_trust.normalize_text_for_malabs`; default **on**). |
| **MalAbs semantic (chat)** | `KERNEL_SEMANTIC_CHAT_GATE`, `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK`, … | **Defaults:** gate and hash fallback **on** when unset — embedding tier after lexical; hash vectors if Ollama unavailable ([MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md), ADR 0003). Set `GATE=0` for lexical-only. **θ_block / θ_allow** defaults are engineering priors (not an in-repo benchmark); tests lock constants — [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md). |
| **LLM / variability** | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GENERATIVE_*` (`KERNEL_GENERATIVE_LLM` = parse extra candidates from perception JSON); **touchpoint degradation:** `KERNEL_LLM_TP_*`, `KERNEL_LLM_VERBAL_FAMILY_POLICY`, `KERNEL_LLM_MONOLOGUE_BACKEND_POLICY`, optional unified fallback `KERNEL_LLM_GLOBAL_DEFAULT_POLICY` (applied only where valid for each resolver), plus legacy `KERNEL_PERCEPTION_BACKEND_POLICY` / `KERNEL_VERBAL_LLM_BACKEND_POLICY` (see [PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md)) | Tone and candidate lists — MalAbs still gates actions. Per-touchpoint LLM recovery precedence is documented in the matrix. |
| **Poles (linear)** | `KERNEL_POLE_LINEAR_CONFIG` | Path to JSON for `LinearPoleEvaluator` (ADR 0004); default `pole_linear_default.json` in package. |
| **Input trust (embedding transport)** | `KERNEL_SEMANTIC_CHAT_EMBED_MODEL`, `KERNEL_SEMANTIC_CHAT_SIM_*`, `KERNEL_SEMANTIC_CHAT_LLM_ARBITER`, `KERNEL_SEMANTIC_EMBED_*` (timeouts, circuit, hash dim/scope in `semantic_embedding_client`) | Tuning for the semantic tier ([`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md), ADR 0003). Gate + hash defaults are summarized in **MalAbs semantic** row above. **`SIM_*` numeric defaults:** see [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md); intentional changes need review + tests. |
| **Psi Sleep feedback (lab)** | `KERNEL_FEEDBACK_CALIBRATION`, `KERNEL_PSI_SLEEP_UPDATE_MIXTURE`, `KERNEL_FEEDBACK_CALIBRATION_MIN_SAMPLES`, `KERNEL_PSI_SLEEP_FEEDBACK_BLEND` | WebSocket `operator_feedback` records labels for the last turn’s regime; `execute_sleep` may apply a **bounded** `hypothesis_weights` nudge (genome drift cap). See [`PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md`](PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md) (B1). |
| **Guardian Angel** | `KERNEL_GUARDIAN_MODE`, `KERNEL_GUARDIAN_ROUTINES`, `KERNEL_GUARDIAN_ROUTINES_PATH`, `KERNEL_CHAT_INCLUDE_GUARDIAN`, `KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES` | Protective tone + optional JSON care routines (hints only); [`landing/public/guardian.html`](../../landing/public/guardian.html). |
| **Mixture weights / Bayesian engine mode** | `KERNEL_BAYESIAN_MODE`, `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`, `KERNEL_BAYESIAN_ASSISTED_BLEND`, … | `KERNEL_BAYESIAN_MODE` selects `BayesianInferenceEngine` mode: `disabled` (default), `telemetry_only`, `posterior_assisted`, `posterior_driven`. **Invalid values fall back to `disabled`** with a warning ([`bayesian_engine.py`](../../src/modules/bayesian_engine.py)). Aliases `off` / `none` / `0` / `false` → `disabled`. When `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` is `1`, nudges discrete mixture weights from recent `NarrativeMemory` episodes **in the same context** before scoring; default **off**; **not** full Bayesian inference ([ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md)). |
| **Temporal horizon prior** | `KERNEL_TEMPORAL_HORIZON_PRIOR`, `KERNEL_TEMPORAL_HORIZON_ALPHA`, `KERNEL_TEMPORAL_HORIZON_WEEKS_DAYS` | After episodic step: extra nudge from weeks/long-arc signals ([`TEMPORAL_PRIOR_HORIZONS.md`](TEMPORAL_PRIOR_HORIZONS.md), ADR 0005); default **off**. |
| **Temporal planning directive** | `KERNEL_TEMPORAL_BATTERY_MINUTES_AT_FULL`, `KERNEL_TEMPORAL_BATTERY_LOW_HORIZON_MIN`, `KERNEL_TEMPORAL_LAN_SYNC`, `KERNEL_TEMPORAL_DAO_SYNC` | Per-turn temporal context for planning (`temporal_context` / `temporal_sync`): processor delta, human wall-clock, battery horizon, task ETA heuristic, and DAO/LAN sync-readiness flags (advisory only; no policy override). |
| **Nomad / identity** | `KERNEL_NOMAD_*`, `KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY` | Lab simulation + JSON — **stubs** where noted in docs. |
| **Metaplan / drives (advisory)** | `KERNEL_METAPLAN_HINT`, `KERNEL_METAPLAN_DRIVE_FILTER`, `KERNEL_METAPLAN_DRIVE_EXTRA` | Owner goals in LLM tone; optional filter of `drive_intents` vs goal wording; optional coherence hint — **no** ethics veto. |
| **Swarm stub (lab)** | `KERNEL_SWARM_STUB` | Enables optional use of `swarm_peer_stub` digest helpers in tooling — **no** P2P stack, **no** kernel change ([`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md)). |
| **Extension seam (Phase 2)** | `KERNEL_EVENT_BUS` | When `1`, `EthicalKernel` builds `KernelEventBus` and publishes **`kernel.decision`** / **`kernel.episode_registered`** (sync, best-effort handlers). See [ADR 0006](../adr/0006-phase2-core-boundary-and-event-bus.md), [`PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md`](PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md), profile **`phase2_event_bus_lab`**. |

### LLM touchpoint index (readability; single-prefix unification deferred)

Renaming every LLM-related knob under one `KERNEL_LLM_*` prefix is **deferred** ([`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3; [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md) G-04). Until then, map **concerns → §1 rows** above:

| Concern | Where to look |
|--------|----------------|
| Chat **completion** JSON (perceive / communicate / narrate), touchpoint degradation | **LLM / variability** row; [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) |
| **Semantic** MalAbs (embeddings) | **MalAbs semantic (chat)** + **Input trust (embedding transport)** rows; [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md) |
| Structured **perception** (parse, dual vote, cross-check) | **Perception / sensors** row; [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md) |

**Nominal lab bundle** combining semantic gate + generative parsing from perception JSON: **`llm_integration_lab`** in [`runtime_profiles.py`](../../src/runtime_profiles.py).

**Phased expansion (operator recipes, async-timeout metric, chain tests):** [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md).

---

## 2. Explicitly rejected combinations (when `KERNEL_ENV_VALIDATION=strict`)

| Pattern | Why |
|---------|-----|
| `KERNEL_JUDICIAL_MOCK_COURT=1` with judicial escalation **off** | Mock court is wired after escalation; enabling only mock court is misleading. |
| `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1` with **no** `KERNEL_LIGHTHOUSE_KB_PATH` | Reality verification may no-op; set a KB path for meaningful demos. |
| `KERNEL_SEMANTIC_CHAT_GATE` explicitly **off** while judicial escalation, mock court, or **`KERNEL_MORAL_HUB_DAO_VOTE`** is **on** | Lexical-only MalAbs with governance demos is an airgap trade-off; strict mode flags it for externally reachable stacks. |

With **`KERNEL_ENV_VALIDATION=warn`**, violations are **logged** only (no raise). When unset, the process default is **`strict`** (see opening paragraph); **`lab`** profiles merged via `ETHOS_RUNTIME_PROFILE` also receive **`warn`** from profile application when validation was unset.

---

## 3. Unsupported or “lab only” combinations

These are **not** forbidden by code, but **not CI-guaranteed** unless a profile or test is added:

| Pattern | Risk |
|---------|------|
| **Many `KERNEL_CHAT_INCLUDE_*=0`** plus **full relational** expectations | Clients may assume keys exist; document minimal JSON for your UI. |
| **`KERNEL_LIGHTHOUSE_KB_PATH` unset** + **`KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`** | Lighthouse may no-op; verify fixture path for demos. JSON schema and limits: [LIGHTHOUSE_KB.md](LIGHTHOUSE_KB.md). |
| **`KERNEL_MORAL_HUB_PUBLIC=0`** but enabling **DAO WebSocket vote paths** that assume hub | Use `hub_dao_demo` or `moral_hub_extended` as baseline. |
| **`KERNEL_API_DOCS=1`** on **LAN bind** (`0.0.0.0`) | Exposes OpenAPI — intentional only for trusted networks ([SECURITY.md](SECURITY.md)). |
| **Arbitrary** `KERNEL_SENSOR_FIXTURE` + **`KERNEL_SENSOR_PRESET`** + client `sensor` | Merge order is documented; conflicting keys confuse debugging. |
| **`KERNEL_SENSOR_INPUT_STRICT=1`** + messy client `sensor` | Strict validation rejects unknown keys / bad types before coercion; WebSocket returns `sensor_payload_invalid` ([`PROPOSAL_SENSOR_FUSION_NORMALIZATION.md`](PROPOSAL_SENSOR_FUSION_NORMALIZATION.md)). |

**Rule of thumb:** if it is not a **named profile** in `runtime_profiles.py` and not covered by a **dedicated test**, treat it as **experimental**.

---

## 4. Deprecation posture (roadmap)

- **Today:** deprecated `KERNEL_*` names remain **functional** during the transition window; [`check_deprecated_flags()`](../../src/validators/deprecation_warnings.py) emits `DeprecationWarning` at kernel startup when a deprecated flag is set (not a hard block).
- **`DEPRECATION_ROADMAP`** in [`src/validators/env_policy.py`](../../src/validators/env_policy.py) — short **migration hint** per flag (human-readable). **`DEPRECATED_FLAGS`** in [`deprecation_warnings.py`](../../src/validators/deprecation_warnings.py) — **removal_version** + longer replacement text. **Keys must match** (regression: [`tests/test_deprecation_warnings.py`](../../tests/test_deprecation_warnings.py)).
- **When removing a flag from code:** **CHANGELOG.md** entry + migration note; align with the **removal_version** string already on the flag (research track may stay at **`0.0.0`** in [`pyproject.toml`](../../pyproject.toml) until a semver release is cut — removals are still documented in CHANGELOG).
- **v0.2+ (placeholder policy):** prefer **`ETHOS_RUNTIME_PROFILE`** + documented bundles over ad-hoc long `KERNEL_*` lists; redundant toggles may be **aliased** before removal.
- **New features:** add **tests** + a **profile slice** if the feature is demo-critical.

---

## 5. Relation to [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md)

Section **4** lists **nominal profiles**; this file is the **policy** layer (what “unsupported” means, how families fit together). Issue 7: strategy doc + CI green on `tests/test_runtime_profiles.py` and `tests/test_env_policy.py`.

---

*MoSex Macchina Lab — critique roadmap Issue 7.*
