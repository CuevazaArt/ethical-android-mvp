# ENV_VAR_CATALOG — Ethos Kernel environment variables

**ADR 0016 Axis B1 — 2026-04-15**

Complete inventory of every `KERNEL_*`, `OLLAMA_*`, and `ETHOS_*` environment
variable read by the codebase (`src/`). Variables are grouped by functional tier.

> **Governance:** variables marked ⚙ are in the DAO governable surface
> (`src/dao/governable_parameters.py`). Variables marked ⛔ are safety-critical
> and require elevated DAO quorum to change.  
> **Deprecated:** none yet — first deprecation pass is Axis B2 (future sprint).

---

## 1. Runtime profile & startup

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `ETHOS_RUNTIME_PROFILE` | `""` | str | Named bundle from `src/runtime_profiles.py`. Explicit env vars win per key. |
| `KERNEL_ENV_VALIDATION` | `"strict"` | str | `strict` → raise on violations; `warn` → log only; `off` → skip. Tests default to `warn`. |

---

## 2. LLM / Ollama backend

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `OLLAMA_BASE_URL` | `"http://localhost:11434"` | str | Ollama server base URL. |
| `OLLAMA_MODEL` | `"llama3"` | str | Primary LLM model name. |
| `OLLAMA_TIMEOUT` | `60` | float (s) | HTTP timeout for Ollama requests. |
| `KERNEL_LLM_MONOLOGUE` | `0` | bool | Include `monologue` field in WebSocket JSON. |
| `KERNEL_PERCEPTION_DUAL_VOTE` | `0` | bool | Run a second perception sample for cross-check. |
| `KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL` | `""` | str | Model for the second perception sample. |
| `KERNEL_PERCEPTION_DUAL_TEMP_SECOND` | `0.9` | float | Temperature for the second sample. |
| `KERNEL_PERCEPTION_DUAL_DISCREPANCY_MIN` | `0.4` | float | Min disagreement to trigger deliberation upgrade. |
| `KERNEL_PERCEPTION_CIRCUIT` | `0` | bool | Enable perception circuit-breaker. |
| `KERNEL_PERCEPTION_CROSS_CHECK` | `0` | bool | Enable lexical cross-check on perception output. |
| `KERNEL_PERCEPTION_FAILSAFE` | `0` | bool | Fail-safe fallback when perception parse fails. |
| `KERNEL_PERCEPTION_FAILSAFE_BLEND` | `0.5` | float | Blend factor for failsafe template. |
| `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL` | `0` | bool | Use local template on parse failure (no LLM retry). |
| `KERNEL_PERCEPTION_UNCERTAINTY_MIN` | `0.5` | float | Coercion uncertainty floor that upgrades D_fast → D_delib. |
| `KERNEL_GENERATIVE_ACTIONS_MAX` | `3` | int | Max generative candidates to propose via LLM. |
| `KERNEL_GENERATIVE_LLM` | `0` | bool | Enable generative candidate generation. |

---

## 3. Ethical scoring & Bayesian mixture (ADR 0012 / 0013)

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_BMA_ENABLED` | `0` | bool | Enable Bayesian Model Averaging win probabilities. |
| `KERNEL_BMA_ALPHA` | `"1.0,1.0,1.0"` | str | Dirichlet prior α for BMA (comma-separated floats). |
| `KERNEL_BMA_SAMPLES` | `1000` | int | Number of MC samples for BMA. |
| `KERNEL_BMA_SEED` | `""` | int | Random seed for BMA (empty = random). |
| `KERNEL_BAYESIAN_FEEDBACK` | `0` | bool | Enable Level 2 feedback posterior updates. |
| `KERNEL_BAYESIAN_CONTEXT_LEVEL3` | `0` | bool | Enable Level 3 per-context posteriors (ADR 0013). |
| `KERNEL_HIERARCHICAL_FEEDBACK` | `0` | bool | Enable HierarchicalUpdater (ADR 0013). |
| `KERNEL_ACTIVE_CONTEXT_TYPE` | `""` | str | Override context bucket for Level 3 inference. |
| `KERNEL_CONTEXT_KEYWORDS_JSON` | `""` | str | Path to JSON context keyword map. |
| `KERNEL_CONTEXT_SCENARIO_MAP_JSON` | `""` | str | Path to JSON scenario → context map. |
| `KERNEL_FEEDBACK_PATH` | `""` | str | Path to feedback JSONL for posterior updates. |
| `KERNEL_FEEDBACK_LIKELIHOOD` | `"softmax"` | str | Likelihood function: `softmax` or `importance_sampling`. |
| `KERNEL_FEEDBACK_TRUST_WEIGHT` | `1.0` | float | Weight applied to feedback before update. |
| `KERNEL_FEEDBACK_UPDATE_STRENGTH` | `1.0` | float | Scaling factor for posterior update magnitude. |
| `KERNEL_FEEDBACK_MAX_DRIFT` | `0.4` | float | Max allowed drift from prior per feedback batch. |
| `KERNEL_FEEDBACK_MC_SAMPLES` | `500` | int | MC samples for feedback posterior check. |
| `KERNEL_FEEDBACK_SEED` | `""` | int | Random seed for feedback MC. |
| `KERNEL_FEEDBACK_BETA_BIAS` | `0.0` | float | Sensitivity bias in beta-calibrated likelihood. |
| `KERNEL_FEEDBACK_BETA_GRID` | `20` | int | Grid resolution for beta calibration. |
| `KERNEL_FEEDBACK_SOFTMAX_BETA` | `1.0` | float | Softmax temperature β for feedback likelihood. |
| `KERNEL_FEEDBACK_DECAY_HALFLIFE` | `""` | float | Halflife (turns) for temporal feedback decay. |
| `KERNEL_FEEDBACK_POSTERIOR_CHECK` | `0` | bool | Enable posterior predictive check on feedback. |
| `KERNEL_FEEDBACK_CALIBRATION_MIN_SAMPLES` | `5` | int | Min samples before calibration kicks in. |
| `KERNEL_PSI_SLEEP_FEEDBACK_BLEND` | `0.3` | float | Blend factor from Psi Sleep counterfactual into posterior. |
| `KERNEL_POLE_LINEAR_CONFIG` | `""` | str | Path to JSON linear pole weights file. |
| `KERNEL_TEMPORAL_HORIZON_ALPHA` | `0.5` | float | Temporal prior alpha (ADR 0005). |
| `KERNEL_TEMPORAL_HORIZON_WEEKS_DAYS` | `""` | str | Override horizon weeks/days for temporal prior. |
| `KERNEL_TEMPORAL_REFERENCE_ETA_S` | `""` | float | Reference ETA in seconds for temporal modulation. |

---

## 4. Safety & MalAbs

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_SEMANTIC_CHAT_GATE` | `1` | bool ⛔ | Enable semantic (embedding) MalAbs gate. |
| `KERNEL_SEMANTIC_EMBED_HASH_SCOPE` | `""` | str | Hash scope for embedding fallback. |
| `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK` | `1` | bool | Use hash fallback when embedding server unavailable. |
| `KERNEL_SEMANTIC_CHAT_EMBED_MODEL` | `""` | str | Embedding model name for semantic gate. |
| `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` | `0.75` | float | Cosine similarity threshold for MalAbs pass. |
| `KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD` | `0.90` | float | Threshold above which input is hard-blocked. |
| `KERNEL_SEMANTIC_CHAT_LLM_ARBITER` | `0` | bool | Use LLM arbiter for borderline semantic cases. |
| `KERNEL_SEMANTIC_ANCHOR_CACHE_TTL_S` | `300` | int | TTL for semantic anchor cache (seconds). |
| `KERNEL_MALABS_LEET_FOLD` | `1` | bool | Fold leet-speak in lexical MalAbs check. |
| `KERNEL_MALABS_STRIP_BIDI` | `1` | bool | Strip Unicode bidirectional overrides before check. |
| `KERNEL_DEONTIC_GATE` | `0` | bool | Enable deontic gate post-MalAbs (V12.3). |
| `KERNEL_LIGHT_RISK_CLASSIFIER` | `0` | bool | Enable lightweight risk tier pre-classification. |
| `KERNEL_LOCAL_SOVEREIGNTY` | `1` | bool | Enable local sovereignty module (data minimization hints). |

---

## 5. Sensors & multimodal (ADR 0017)

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_SENSOR_FIXTURE` | `""` | str | Path to JSON sensor fixture file (static test data). |
| `KERNEL_SENSOR_PRESET` | `""` | str | Named preset from `perceptual_abstraction.SENSOR_PRESETS`. |
| `KERNEL_MULTIMODAL_AUDIO_STRONG` | `0.75` | float ⚙ | Audio emergency threshold for strong alarm. |
| `KERNEL_MULTIMODAL_VISION_SUPPORT` | `0.60` | float ⚙ | Vision corroboration threshold. |
| `KERNEL_MULTIMODAL_SCENE_SUPPORT` | `0.50` | float | Scene coherence support threshold. |
| `KERNEL_MULTIMODAL_VISION_CONTRADICT` | `0.30` | float | Vision contradiction threshold. |
| `KERNEL_MULTIMODAL_SCENE_CONTRADICT` | `0.25` | float | Scene contradiction threshold. |
| `KERNEL_EPISTEMIC_AUDIO_MIN` | `""` | float | Min audio score for epistemic dissonance check. |
| `KERNEL_EPISTEMIC_MOTION_MAX` | `""` | float | Max jerk for epistemic dissonance pass. |
| `KERNEL_EPISTEMIC_VISION_LOW` | `""` | float | Low vision threshold for dissonance. |
| `KERNEL_VITALITY_CRITICAL_BATTERY` | `0.15` | float ⚙ | Battery fraction below which guardian mode activates. |
| `KERNEL_FIELD_CONTROL` | `0` | bool | Enable phone-relay field test control surface (ADR 0017). |
| `KERNEL_FIELD_PAIRING_TOKEN` | `""` | str | One-time token for phone pairing. Keep secret. |
| `KERNEL_FIELD_SENSOR_HZ` | `2` | int ⚙ | Max sensor frame rate from phone relay (Hz). |
| `KERNEL_FIELD_ALLOW_WAN` | `0` | bool | Allow non-LAN connections to `/control/pair` (lab only). |

---

## 6. Narrative & UX

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_GUARDIAN_MODE` | `0` | bool ⚙ | Enable protective/guardian tone in LLM layer. |
| `KERNEL_GUARDIAN_ROUTINES` | `0` | bool | Enable guardian care routines. |
| `KERNEL_GUARDIAN_ROUTINES_PATH` | `""` | str | Path to JSON guardian routines file. |
| `KERNEL_NARRATIVE_IDENTITY_POLICY` | `""` | str | Narrative identity lean policy name. |
| `KERNEL_SOMATIC_MARKERS` | `1` | bool | Enable somatic marker module. |
| `KERNEL_GRAY_ZONE_DIPLOMACY` | `1` | bool | Enable gray-zone diplomacy hints in responses. |
| `KERNEL_METAPLAN_HINT` | `""` | str | Override metaplan directive. |
| `KERNEL_METAPLAN_DRIVE_FILTER` | `""` | str | Filter drives by name (comma-separated). |
| `KERNEL_METAPLAN_DRIVE_EXTRA` | `""` | str | Extra drive names to inject. |
| `KERNEL_SWARM_STUB` | `0` | bool | Enable swarm peer stub digest (lab). |
| `KERNEL_ADVISORY_INTERVAL_S` | `""` | float | Interval (s) for advisory telemetry loop per session. |

---

## 7. WebSocket JSON output flags

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_CHAT_EXPOSE_MONOLOGUE` | `1` | bool | Include `monologue` in chat JSON (privacy flag). |
| `KERNEL_CHAT_INCLUDE_HOMEOSTASIS` | `1` | bool | Include `affective_homeostasis` in JSON. |
| `KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST` | `1` | bool | Include `experience_digest` (Psi Sleep summary). |
| `KERNEL_CHAT_INCLUDE_USER_MODEL` | `1` | bool | Include `user_model` snapshot. |
| `KERNEL_CHAT_INCLUDE_CHRONO` | `1` | bool | Include `chronobiology` field. |
| `KERNEL_CHAT_INCLUDE_PREMISE` | `1` | bool | Include `premise_advisory`. |
| `KERNEL_CHAT_INCLUDE_TELEOLOGY` | `1` | bool | Include `teleology_branches`. |
| `KERNEL_CHAT_INCLUDE_MULTIMODAL` | `1` | bool | Include `multimodal_trust`. |
| `KERNEL_CHAT_INCLUDE_VITALITY` | `1` | bool | Include `vitality` snapshot. |
| `KERNEL_CHAT_INCLUDE_GUARDIAN` | `1` | bool | Include `guardian_mode` flag. |
| `KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES` | `0` | bool | Include `guardian_routines` list. |
| `KERNEL_CHAT_INCLUDE_EPISTEMIC` | `1` | bool | Include `epistemic_dissonance`. |
| `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION` | `0` | bool | Include `reality_verification`. |
| `KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY` | `0` | bool | Include `nomad_identity`. |
| `KERNEL_CHAT_INCLUDE_LIGHT_RISK` | `0` | bool | Include `light_risk_tier`. |
| `KERNEL_CHAT_INCLUDE_JUDICIAL` | `0` | bool | Include `judicial_escalation`. |
| `KERNEL_CHAT_INCLUDE_CONSTITUTION` | `0` | bool | Include `constitution` in JSON. |
| `KERNEL_CHAT_INCLUDE_TRANSPARENCY_S10` | `1` | bool | Include optional `transparency_s10` (embodied sociability narration / withdrawal / discomfort / help codes). |

---

## 8. Performance & chat bridge

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_CHAT_THREADPOOL_WORKERS` | `""` | int | Dedicated thread pool size for chat turns (0 = Starlette default). |
| `KERNEL_CHAT_TURN_TIMEOUT` | `""` | float (s) | Async timeout per chat turn. |
| `KERNEL_API_DOCS` | `0` | bool | Expose `/docs`, `/redoc`, `/openapi.json`. |
| `KERNEL_METRICS` | `0` | bool | Enable Prometheus `/metrics` endpoint. |
| `KERNEL_LOG_JSON` | `0` | bool | Emit structured JSON logs. |
| `KERNEL_LOG_LEVEL` | `"INFO"` | str | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `KERNEL_LOG_DECISION_EVENTS` | `0` | bool | Log per-turn decision events to decision log. |
| `KERNEL_EVENT_BUS` | `0` | bool | Enable `KernelEventBus` (ADR 0006). |

---

## 9. Persistence & checkpoint

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_CHECKPOINT_PATH` | `""` | str | Path for JSON checkpoint file. |
| `KERNEL_CHECKPOINT_FERNET_KEY` | `""` | str | Fernet key for encrypted checkpoint. **Secret — never log.** |
| `KERNEL_CHECKPOINT_LOAD` | `1` | bool | Load checkpoint on session start if path set. |
| `KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT` | `1` | bool | Save checkpoint on WebSocket disconnect. |
| `KERNEL_CHECKPOINT_EVERY_N_EPISODES` | `""` | int | Save checkpoint every N episodes (0 = off). |
| `KERNEL_CONDUCT_GUIDE_PATH` | `""` | str | Path to existing conduct guide JSON to load. |
| `KERNEL_CONDUCT_GUIDE_EXPORT_PATH` | `""` | str | Path to write conduct guide JSON on disconnect. |
| `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT` | `1` | bool | Auto-export conduct guide on disconnect. |
| `KERNEL_AUDIT_CHAIN_PATH` | `""` | str | Path for append-only HMAC audit chain. |
| `KERNEL_AUDIT_HMAC_SECRET` | `""` | str | Secret for audit chain HMAC. **Never log.** |
| `KERNEL_AUDIT_SIDECAR_PATH` | `""` | str ⚙ | Path for append-only MockDAO audit sidecar. |

---

## 10. Governance & DAO (V12)

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_MORAL_HUB_PUBLIC` | `0` | bool | Expose `GET /constitution` (L0 JSON). |
| `KERNEL_MORAL_HUB_DAO_VOTE` | `0` | bool | Enable DAO WebSocket actions (`dao_vote`, `dao_resolve`, …). |
| `KERNEL_MORAL_HUB_DRAFT_WS` | `0` | bool | Enable constitution draft WebSocket. |
| `KERNEL_DEMOCRATIC_BUFFER_MOCK` | `0` | bool | Enable mock DemocraticBuffer proposals. |
| `KERNEL_ETHOS_PAYROLL_MOCK` | `0` | bool | Append mock EthosPayroll ledger on connect. |
| `KERNEL_TRANSPARENCY_AUDIT` | `0` | bool | Log transparency events on WebSocket connect. |
| `KERNEL_DAO_INTEGRITY_AUDIT_WS` | `0` | bool | Emit integrity alert to MockDAO on WebSocket. |
| `KERNEL_REPARATION_VAULT_MOCK` | `0` | bool | Enable reparation vault mock. |
| `KERNEL_ML_ETHICS_TUNER_LOG` | `0` | bool | Log gray-zone tuning opportunities for future calibration. |
| `KERNEL_JUDICIAL_ESCALATION` | `0` | bool | Enable judicial escalation advisory (V11). |
| `KERNEL_JUDICIAL_MOCK_COURT` | `0` | bool | Run simulated DAO court after dossier (V11 Phase 3). |
| `KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER` | `2` | int ⚙ | Session strikes before escalation dossier. |
| `KERNEL_JUDICIAL_RESET_IDLE_TURNS` | `5` | int | Idle turns before judicial strike counter resets. |

---

## 11. Identity & nomadics

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_NOMAD_SIMULATION` | `0` | bool | Enable nomadic HAL migration simulation. |
| `KERNEL_NOMAD_MIGRATION_AUDIT` | `0` | bool | Append DAO calibration line on migration. |
| `KERNEL_NOMAD_TELEMETRY_VITALITY` | `1` | bool | Merge latest Nomad `telemetry` into the sensor snapshot before `assess_vitality` when fields are missing (`0` disables). |
| `KERNEL_NOMADIC_ED25519_PRIVATE_KEY` | `""` | str | Ed25519 private key for nomadic identity signing. **Secret.** |
| `KERNEL_NOMADIC_ED25519_PUBLIC_KEY` | `""` | str | Ed25519 public key. |
| `KERNEL_ETHICAL_GENOME_MAX_DRIFT` | `0.2` | float | Maximum allowed genome drift before identity alert. |
| `KERNEL_LIGHTHOUSE_KB_PATH` | `""` | str | Path to JSON lighthouse knowledge base (reality verification). |

---

## 12. Cross-check & miscellaneous

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `KERNEL_CROSS_CHECK_HIGH_MIN_RISK` | `0.7` | float | Risk floor for high-stress cross-check. |
| `KERNEL_CROSS_CHECK_HIGH_MAX_CALM` | `0.3` | float | Calm ceiling for high-stress cross-check. |
| `KERNEL_CROSS_CHECK_MED_MIN_RISK` | `0.4` | float | Risk floor for medium-stress cross-check. |
| `KERNEL_CROSS_CHECK_MED_MAX_CALM` | `0.5` | float | Calm ceiling for medium-stress cross-check. |

---

## Secrets (never log, never commit)

| Variable | Notes |
|----------|-------|
| `KERNEL_CHECKPOINT_FERNET_KEY` | Fernet symmetric key |
| `KERNEL_AUDIT_HMAC_SECRET` | HMAC audit chain secret |
| `KERNEL_NOMADIC_ED25519_PRIVATE_KEY` | Identity signing key |
| `KERNEL_FIELD_PAIRING_TOKEN` | Phone pairing token |
| `SECRET_KEY` | (future) HMAC signing for field session credentials (ADR 0017) |

---

## Legend

- ⚙ — Governable via DAO proposal (`src/dao/governable_parameters.py`)
- ⛔ — Safety-critical; requires elevated DAO quorum
- **Bold** — Used in `conftest.py` test isolation

*Last updated: 2026-04-17 (Nomad S.2.1 vitality merge + S10 chat flag)*
