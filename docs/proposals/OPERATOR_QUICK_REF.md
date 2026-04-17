# Operator quick reference — `KERNEL_*` families

**Canonical detail:** [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) · **profiles:** [`src/runtime_profiles.py`](../../src/runtime_profiles.py) · **one-shot bundle:** `ETHOS_RUNTIME_PROFILE=<name>` at chat server startup (fills unset/empty keys only) · **chat keys:** [`src/chat_server.py`](../../src/chat_server.py) docstring / README WebSocket section · **HTTP JSON routes (GET):** [`PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md) · **observability:** [Observability (metrics and logs)](#observability-metrics-and-logs) · **ADR:** [`0008`](../adr/0008-runtime-observability-prometheus-and-logs.md).

### Configuration cockpit CLI (KERNEL_* fatigue)

Use the **`ethos config`** command (after `pip install -e .` or `python -m src.ethos_cli config`) to **group** current `KERNEL_*` / related keys by **family**, see **policy violations**, **experimental-risk** heuristics (many flags set without `ETHOS_RUNTIME_PROFILE`), and **alignment scores** against nominal bundles (explicit env values only). **`ethos config --profiles`** lists `ETHOS_RUNTIME_PROFILE` names with one-line descriptions. **`ethos config --strict`** runs `validate_kernel_env(strict)` and exits non-zero on violations. Implementation: [`src/validators/kernel_env_operator.py`](../../src/validators/kernel_env_operator.py).

| Family | Prefix / examples | Typical role |
|--------|---------------------|--------------|
| Chat JSON telemetry | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | Include/omit WebSocket fields (UX only). |
| Chat concurrency | `KERNEL_CHAT_TURN_TIMEOUT`, `KERNEL_CHAT_THREADPOOL_WORKERS` | Async deadline per turn; optional dedicated thread pool ([ADR 0002](../adr/0002-async-orchestration-future.md)). |
| Persistence / handoff | `KERNEL_CHECKPOINT_*`, `KERNEL_CHECKPOINT_FERNET_KEY`, `KERNEL_CONDUCT_GUIDE_*` | Disk snapshots, encryption, conduct export. |
| Input / epistemics | `KERNEL_LIGHTHOUSE_KB_PATH`, `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION` | Lighthouse KB path; reality JSON in chat. |
| Guardian Angel | `KERNEL_GUARDIAN_MODE`, `KERNEL_GUARDIAN_ROUTINES*`, `KERNEL_CHAT_INCLUDE_GUARDIAN*` | Tone + optional routines JSON; static UI [`guardian.html`](../../landing/public/guardian.html). |
| Perception / sensors | `KERNEL_SENSOR_FIXTURE`, `KERNEL_SENSOR_PRESET`, `KERNEL_MULTIMODAL_*`, `KERNEL_PERCEPTION_BACKEND_POLICY` | Situated v8 snapshot merge; multimodal thresholds; degraded LLM perception policy (`template_local` / `fast_fail` / `session_banner`). |
| Governance / hub | `KERNEL_MORAL_HUB_*`, `KERNEL_DEONTIC_GATE`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS` | Hub, drafts, judicial, integrity audit. |
| Metaplan / drives | `KERNEL_METAPLAN_HINT`, `KERNEL_METAPLAN_DRIVE_FILTER`, `KERNEL_METAPLAN_DRIVE_EXTRA` | Owner goals hint; filter advisory `drive_intents` vs goals; extra coherence intent. |
| Swarm (lab stub) | `KERNEL_SWARM_STUB` | Offline verdict-digest helpers only; see [`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md). |
| LLM / variability | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GENERATIVE_*` (`KERNEL_GENERATIVE_LLM` = JSON candidates in perception); degradation: `KERNEL_LLM_TP_*`, `KERNEL_LLM_VERBAL_FAMILY_POLICY`, `KERNEL_LLM_GLOBAL_DEFAULT_POLICY`, legacy `KERNEL_PERCEPTION_BACKEND_POLICY` / `KERNEL_VERBAL_LLM_BACKEND_POLICY` | Backends, generative candidates, and **resolved** fallback policies on `GET /health` → `llm_degradation` ([`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md)). |
| Poles (linear) | `KERNEL_POLE_LINEAR_CONFIG` | JSON path for `LinearPoleEvaluator` (ADR 0004); default bundled. |
| Input (optional) | `KERNEL_SEMANTIC_CHAT_GATE`, `KERNEL_SEMANTIC_CHAT_EMBED_MODEL`, block/allow thresholds, `KERNEL_SEMANTIC_CHAT_LLM_ARBITER` | Lexical → embeddings → optional LLM; see [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md). Default cosine thresholds: evidence posture and guardrails — [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md). |
| **Mixture weights (episodic)** | `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` | When `1`, ethical mixture weights are nudged from recent episode scores (same context; not full Bayes). Default `0`. |
| **Temporal horizon** | `KERNEL_TEMPORAL_HORIZON_PRIOR`, `KERNEL_TEMPORAL_HORIZON_ALPHA` | Weeks / long-arc nudge to mixture ([`TEMPORAL_PRIOR_HORIZONS.md`](TEMPORAL_PRIOR_HORIZONS.md)). Default off. |
| **Temporal planning directive** | `KERNEL_TEMPORAL_BATTERY_MINUTES_AT_FULL`, `KERNEL_TEMPORAL_BATTERY_LOW_HORIZON_MIN`, `KERNEL_TEMPORAL_LAN_SYNC`, `KERNEL_TEMPORAL_DAO_SYNC` | Emits per-turn `temporal_context` + `temporal_sync` (processor delta, wall clock, ETA, battery horizon, sync readiness for LAN/DAO consumers). |
| **Observability** | `KERNEL_METRICS`, `KERNEL_LOG_JSON`, `KERNEL_LOG_DECISION_EVENTS`, `KERNEL_LOG_LEVEL` | Prometheus `GET /metrics` (off by default); JSON logs; optional per-decision JSON lines; log level. HTTP/WebSocket correlation via `X-Request-ID`. `GET /health` exposes uptime + observability flags. See [below](#observability-metrics-and-logs). |

**Rule:** if a combination is not a **named profile** and not covered by a **test**, treat it as experimental ([`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md)).

### Distributed justice (V11 — advisory / mock DAO)

- **Enable advisory path:** `KERNEL_JUDICIAL_ESCALATION=1`. **WebSocket JSON:** `KERNEL_CHAT_INCLUDE_JUDICIAL=1`. **Mock tribunal (simulation):** `KERNEL_JUDICIAL_MOCK_COURT=1`. Strikes / threshold: `KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER`, `KERNEL_JUDICIAL_RESET_IDLE_TURNS` — see [`PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) and [`MOCK_DAO_SIMULATION_LIMITS.md`](MOCK_DAO_SIMULATION_LIMITS.md).
- **Staged execution** (off-chain replay → LAN → optional anchors): [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md).
- **How to contribute** (tests, docs, backlog): [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md).

### LLM HTTP vs chat async deadline

`KERNEL_CHAT_TURN_TIMEOUT` bounds how long **asyncio** waits for each chat turn. **Default:** `process_chat_turn` runs in a worker thread; cooperative cancel skips **further** sync LLM HTTP after the deadline; the server also **abandons** the turn id so late workers skip STM / `wm.add_turn`; in-flight sync `httpx` still runs until read timeout — tune `OLLAMA_TIMEOUT` alongside chat deadlines. **Optional:** `KERNEL_CHAT_ASYNC_LLM_HTTP=1` runs `process_chat_turn_async` on the event loop with `httpx.AsyncClient` for Ollama/HTTP JSON so the async deadline can **cancel in-flight** LLM HTTP; the same cancel `Event` is passed into the thread that runs `EthicalKernel.process`, which can **exit cooperatively** at several checkpoints (still not preempted inside one long native call). Anthropic `api` mode: `AnthropicLLMBackend.acompletion` uses `AsyncAnthropic` when the SDK is present ([ADR 0002](../adr/0002-async-orchestration-future.md); G-05 in [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md)). When `KERNEL_METRICS=1`, see `ethos_kernel_chat_turn_async_timeouts_total`, `ethos_kernel_llm_cancel_scope_signals_total`, and `ethos_kernel_chat_turn_abandoned_effects_skipped_total` ([`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md) phase 3).

### LLM vertical operator recipes

Phased roadmap and evidence posture: [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md). Quick combinations (explicit env still overrides profile defaults):

| Recipe | `ETHOS_RUNTIME_PROFILE` (starting point) | Notes |
|--------|------------------------------------------|--------|
| LAN / phone staging | `lan_operational` or `lan_mobile_thin_client` | Bind + stoic JSON; tune `OLLAMA_TIMEOUT` with `KERNEL_CHAT_TURN_TIMEOUT`. |
| Airgap semantic (hash embeddings, no Ollama) | `untrusted_chat_input` | Pair with unreachable `OLLAMA_BASE_URL` + short `KERNEL_SEMANTIC_EMBED_*` timeouts for fast fail (see [`test_malabs_semantic_integration.py`](../../tests/test_malabs_semantic_integration.py)). |
| Generative candidates + semantic gate | `llm_integration_lab` | `KERNEL_GENERATIVE_LLM` + MalAbs hash fallback per [`runtime_profiles.py`](../../src/runtime_profiles.py). |
| Conservative LLM fallbacks (staging) | `llm_staging_conservative` | Perception `fast_fail`, verbal/narrate via `KERNEL_LLM_GLOBAL_DEFAULT_POLICY=canned_safe`, monologue `annotate_degraded`; pairs with semantic hash fallback. See matrix § operator bundle. |
| Perception hardening lab | `perception_hardening_lab` | Light risk + cross-check + uncertainty→delib; compose with `untrusted_chat_input` if you need semantic MalAbs too. |

### Perception observability contract (chat JSON)

When a chat turn includes `perception`, the server emits:

- `perception.coercion_report` with canonical keys (even if local heuristics were used).
- `perception_observability` summary: `uncertainty`, `dual_high_discrepancy`, `backend_degraded`, `metacognitive_doubt`.
- `perception_confidence`: unified confidence envelope (`score`, `band`, `reasons`) aggregated from coercion diagnostics, multimodal mismatch, epistemic dissonance, and vitality pressure.
- Optional `perception_backend_banner=true` when `session_banner_recommended` is active.

This contract is intended for operator dashboards and alerting stability across perception fallback modes.

### Temporal planning / sync contract (chat JSON)

When a chat turn returns, the server may emit:

- `temporal_context`: advisory timing envelope (`turn_index`, processor elapsed, turn delta, wall clock, ETA heuristic source, battery horizon).
- `temporal_sync`: compact synchronization fields for external coordinators (schema/version + turn/time + DAO/LAN readiness).

`temporal_sync` is designed for local-network and DAO-adjacent coordination without requiring external time services; use `sync_schema` to version consumers.

**Coercion:** `turn_index`, `processor_elapsed_ms`, and `turn_delta_ms` are emitted as non-negative integers; malformed or missing values in the internal public dict are coerced to `0` for stable WebSocket JSON (not an ethics policy change; see [`src/chat_server.py`](../../src/chat_server.py) `_coerce_public_int`).

**Sync degraded — local-safe mode (DJ-BL-03):** `temporal_sync.local_network_sync_ready` and `temporal_sync.dao_sync_ready` reflect **`KERNEL_TEMPORAL_LAN_SYNC`** and **`KERNEL_TEMPORAL_DAO_SYNC`** (default `1` = ready when unset; set `0` to mark not ready). These flags are **advisory** for coordinators — they do **not** disable MalAbs, the ethical cycle, or in-process **MockDAO** / **judicial** JSON when enabled via `KERNEL_JUDICIAL_*` / hub env. Treat as “no cross-node guarantee implied,” not “governance offline.” See [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) (Example B — DAO audit continues locally). WebSocket probe: [`tests/test_chat_server.py`](../../tests/test_chat_server.py) `test_websocket_temporal_sync_respects_env_toggles`.

### LAN governance batch merge — frontier hint and conflicts (DJ-BL-14)

- **Gate:** enable LAN merge with **`KERNEL_LAN_GOVERNANCE_MERGE_WS=1`**, plus the batch-specific flags (integrity / DAO vote / judicial / mock court) documented under *Governance / hub* and distributed-justice proposals.
- **Optional `merge_context.frontier_turn`:** on `lan_governance_integrity_batch`, `lan_governance_dao_batch`, `lan_governance_judicial_batch`, and `lan_governance_mock_court_batch` payloads (including the same object when embedded in `lan_governance_envelope.batch`). Events with `turn_index` **strictly less** than `frontier_turn` are dropped and listed under `event_conflicts` as `stale_event` (`reason: below_frontier_turn`). This value is an **operator-supplied session hint** — it is **not** a replicated consensus clock and does not imply cross-session agreement.
- **`event_conflicts`:** batch responses may include a non-empty array whose entries use stable `kind` values (`same_turn`, `different_clock`, `stale_event`). Semantics and evidence posture: [`PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md).
- **Hub coordinator:** `lan_governance_coordinator` responses may include **`aggregated_event_conflicts`** and **`aggregated_frontier_witness_resolutions`** (from inner-batch `merge_context_echo.frontier_witness_resolution`), flattening inner-batch diagnostics and adding `source_batch`, `envelope_fingerprint`, and `envelope_idempotency_token` for correlation where applicable.
- **Cross-session hint (non-consensus):** optional `merge_context.cross_session_hint` with `schema=lan_governance_cross_session_hint_v1` is **validated and echoed** (`merge_context_echo`); invalid hints yield `merge_context_warnings` only — see [`PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md). The kernel does **not** treat this as quorum or replicated frontier.
- **Frontier witnesses (advisory):** optional `merge_context.frontier_witnesses` — peer `observed_max_turn` claims deduped per `claimant_session_id`; echo `frontier_witness_resolution` with `advisory_max_observed_turn` and `evidence_posture=advisory_aggregate_not_quorum` — [`PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md`](PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md). Does **not** apply merge unless you also set `frontier_turn`.
- **Replay sidecar CLI:** [`scripts/eval/verify_lan_governance_replay_sidecar.py`](../../scripts/eval/verify_lan_governance_replay_sidecar.py) fingerprints or compares `lan_governance_replay_sidecar_v1` JSON (optional `--audit-ledger` vs embedded fingerprint) — [`PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md).
- **Anchor checkpoint CLI (Phase 3 stub, DJ-BL-17):** [`scripts/eval/compare_audit_ledger_anchor.py`](../../scripts/eval/compare_audit_ledger_anchor.py) — offline compare only (**no chain RPC**).

  **Usage:** `python scripts/eval/compare_audit_ledger_anchor.py <audit_export.json> <64-char-hex>`  
  **Exit codes:** `0` — fingerprint matches; `1` — mismatch (integrity signal; see Example C in [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md)); `2` — invalid `expected_hex`.

  **Safety posture:** the CLI **does not** mutate governance policy or bypass L0. On mismatch, retain the ledger export, re-run [`scripts/eval/verify_mock_dao_audit_replay.py`](../../scripts/eval/verify_mock_dao_audit_replay.py) for structural replay checks, and reconcile the expected hex **out-of-band** with your anchor source. On-chain verification and proof-grade frontier work stay **out of scope** until covered in *Pending gaps* on the staged execution proposal.

### Verbal LLM observability (chat JSON)

When a generative touchpoint falls back (**communicate**, **narrate**, or optional **monologue** enrich), the server may emit:

- `verbal_llm_observability`: `{ "degraded": true, "events": [ { "touchpoint", "failure_reason", "recovery_policy" } ] }`.

**Configuration precedence** (per path): `KERNEL_LLM_TP_<TOUCHPOINT>_POLICY` → `KERNEL_LLM_VERBAL_FAMILY_POLICY` (communicate + narrate only) → legacy `KERNEL_VERBAL_LLM_BACKEND_POLICY` or `KERNEL_PERCEPTION_BACKEND_POLICY` → optional `KERNEL_LLM_GLOBAL_DEFAULT_POLICY` (only where valid for that resolver) → built-in defaults — [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md). See also [`PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md`](PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md).

**Resolved policies on `/health`:** `GET /health` includes `llm_degradation` with `global_default_raw`, `global_default_effective`, and `resolved` `{ perception, communicate, narrate, monologue }` so dashboards match the same precedence as runtime (no secrets).

### Observability (metrics and logs)

Enable with `KERNEL_METRICS=1` (scrapes `http://<host>:<port>/metrics`). If `prometheus_client` is missing, the server returns HTTP 503 JSON for `/metrics` instead of crashing. Structured JSON logs: `KERNEL_LOG_JSON=1`; severity: `KERNEL_LOG_LEVEL` (e.g. `INFO`, `DEBUG`). Per-decision machine-readable lines (one JSON object per `EthicalKernel.process`): default **on** when JSON logging is on — disable with `KERNEL_LOG_DECISION_EVENTS=0`. **`GET /health`** returns `version`, `uptime_seconds`, an `observability` object (metrics/log flags, `prometheus_client` import status), **`chat_bridge`** (`kernel_chat_turn_timeout_seconds`, `kernel_chat_threadpool_workers`, `kernel_chat_json_offload` — see [`chat_settings.py`](../../src/chat_settings.py)), and a compact **`safety_defaults`** block (`kernel_env_validation_mode`, semantic gate/hash fallback toggles, perception fail-safe and parallel toggles) for quick operator diagnostics.

| Metric name | Type | Labels | Notes |
|--------------|------|--------|--------|
| `ethos_kernel_llm_completion_seconds` | Histogram | `operation` | `perceive`, `communicate`, `narrate`, or `completion` (default internal). Wall time for LLM `completion` calls. |
| `ethos_kernel_chat_turn_duration_seconds` | Histogram | `path` | End-to-end time for one `process_chat_turn` in the worker thread. `path` matches chat result (`light`, `heavy`, `safety_block`, `kernel_block`, …). |
| `ethos_kernel_chat_turns_total` | Counter | `path` | Count of completed turns per `path` (increments with the histogram observation). |
| `ethos_kernel_chat_turn_async_timeouts_total` | Counter | (none) | Increments when the async waiter hits `KERNEL_CHAT_TURN_TIMEOUT` (worker may still run until cooperative exit; see ADR 0002). |
| `ethos_kernel_chat_turn_abandoned_effects_skipped_total` | Counter | (none) | Increments when a late completion skips STM / post-turn effects after `abandon_chat_turn` (`turn_abandoned`). |
| `ethos_kernel_malabs_blocks_total` | Counter | `reason` | Coarse block reason; typically `safety_block` or `kernel_block` when the chat path indicates a block. |
| `ethos_kernel_dao_ws_operations_total` | Counter | `operation` | Mock DAO WebSocket actions, e.g. `list`, `submit_draft`, `vote`, `resolve`, `integrity_alert`, `nomad_migration`. |
| `ethos_kernel_embedding_errors_total` | Counter | `source` | Semantic MalAbs embedding tier: `http` (request/transport failure), `http_invalid` (bad payload), `backend` (adapter `embedding()` exception). |
| `ethos_kernel_semantic_malabs_outcomes_total` | Counter | `outcome` | Semantic tier path: `allow_low_similarity`, `block_high_similarity`, `embed_unavailable_defer`, `ambiguous_fail_safe_block`, `ambiguous_arbiter_*`, etc. ([`semantic_chat_gate.py`](../../src/modules/semantic_chat_gate.py)). |
| `ethos_kernel_kernel_decisions_total` | Counter | `action`, `certainty`, `blocked` | One increment per completed `EthicalKernel.process`. `action` is a coarse slug (bounded cardinality); `certainty` is `high` / `med` / `low` / `n_a` (inverse of uncertainty bands); `blocked` is `true` / `false`. |
| `ethos_kernel_kernel_process_seconds` | Histogram | (none) | Wall time for the full ethical cycle inside `process()`. |
| `ethos_kernel_perception_circuit_trips_total` | Counter | (none) | Increments once when **metacognitive doubt** activates (perception validation streak exceeds two stressed turns; see `perception_circuit.py`). |

Implementation: [`src/observability/metrics.py`](../../src/observability/metrics.py). Decision JSON lines: [`src/observability/decision_log.py`](../../src/observability/decision_log.py). Log field `request_id` is set when a correlation id exists ([`src/observability/logging_setup.py`](../../src/observability/logging_setup.py)).

**Prometheus alert rules (starter):** [`deploy/prometheus/ethos_kernel_alerts.yml`](../../deploy/prometheus/ethos_kernel_alerts.yml) — MalAbs block rate, `safety_block` rate, perception circuit trips. Tune thresholds and `for` duration per deployment; benign traffic spikes can false-positive. Load as `rule_files` in Prometheus; not the same as Grafana dashboard import.
