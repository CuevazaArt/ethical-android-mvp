# Operator quick reference — `KERNEL_*` families

**Canonical detail:** [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) · **profiles:** [`src/runtime_profiles.py`](../src/runtime_profiles.py) · **one-shot bundle:** `ETHOS_RUNTIME_PROFILE=<name>` at chat server startup (fills unset/empty keys only) · **chat keys:** [`src/chat_server.py`](../src/chat_server.py) docstring / README WebSocket section · **observability:** [Observability (metrics and logs)](#observability-metrics-and-logs) · **ADR:** [`0008`](../adr/0008-runtime-observability-prometheus-and-logs.md).

| Family | Prefix / examples | Typical role |
|--------|---------------------|--------------|
| Chat JSON telemetry | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | Include/omit WebSocket fields (UX only). |
| Persistence / handoff | `KERNEL_CHECKPOINT_*`, `KERNEL_CHECKPOINT_FERNET_KEY`, `KERNEL_CONDUCT_GUIDE_*` | Disk snapshots, encryption, conduct export. |
| Input / epistemics | `KERNEL_LIGHTHOUSE_KB_PATH`, `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION` | Lighthouse KB path; reality JSON in chat. |
| Guardian Angel | `KERNEL_GUARDIAN_MODE`, `KERNEL_GUARDIAN_ROUTINES*`, `KERNEL_CHAT_INCLUDE_GUARDIAN*` | Tone + optional routines JSON; static UI [`guardian.html`](../landing/public/guardian.html). |
| Perception / sensors | `KERNEL_SENSOR_FIXTURE`, `KERNEL_SENSOR_PRESET`, `KERNEL_MULTIMODAL_*` | Situated v8 snapshot merge; multimodal thresholds. |
| Governance / hub | `KERNEL_MORAL_HUB_*`, `KERNEL_DEONTIC_GATE`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS` | Hub, drafts, judicial, integrity audit. |
| Metaplan / drives | `KERNEL_METAPLAN_HINT`, `KERNEL_METAPLAN_DRIVE_FILTER`, `KERNEL_METAPLAN_DRIVE_EXTRA` | Owner goals hint; filter advisory `drive_intents` vs goals; extra coherence intent. |
| Swarm (lab stub) | `KERNEL_SWARM_STUB` | Offline verdict-digest helpers only; see [`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md). |
| LLM / variability | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GENERATIVE_*` (`KERNEL_GENERATIVE_LLM` = JSON candidates in perception) | Backends and generative candidates. |
| Poles (linear) | `KERNEL_POLE_LINEAR_CONFIG` | JSON path for `LinearPoleEvaluator` (ADR 0004); default bundled. |
| Input (optional) | `KERNEL_SEMANTIC_CHAT_GATE`, `KERNEL_SEMANTIC_CHAT_EMBED_MODEL`, block/allow thresholds, `KERNEL_SEMANTIC_CHAT_LLM_ARBITER` | Lexical → embeddings → optional LLM; see [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md). |
| **Bayesian episodic** | `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` | When `1`, mixture weights are nudged from recent episode scores (same context). Default `0`. |
| **Temporal horizon** | `KERNEL_TEMPORAL_HORIZON_PRIOR`, `KERNEL_TEMPORAL_HORIZON_ALPHA` | Weeks / long-arc nudge to mixture ([`TEMPORAL_PRIOR_HORIZONS.md`](TEMPORAL_PRIOR_HORIZONS.md)). Default off. |
| **Observability** | `KERNEL_METRICS`, `KERNEL_LOG_JSON`, `KERNEL_LOG_LEVEL` | Prometheus `GET /metrics` (off by default); JSON logs; log level. HTTP/WebSocket correlation via `X-Request-ID`. See [below](#observability-metrics-and-logs). |

**Rule:** if a combination is not a **named profile** and not covered by a **test**, treat it as experimental ([`ESTRATEGIA_Y_RUTA.md`](ESTRATEGIA_Y_RUTA.md)).

### Observability (metrics and logs)

Enable with `KERNEL_METRICS=1` (scrapes `http://<host>:<port>/metrics`). If `prometheus_client` is missing, the server returns HTTP 503 JSON for `/metrics` instead of crashing. Structured JSON logs: `KERNEL_LOG_JSON=1`; severity: `KERNEL_LOG_LEVEL` (e.g. `INFO`, `DEBUG`).

| Metric name | Type | Labels | Notes |
|--------------|------|--------|--------|
| `ethos_kernel_llm_completion_seconds` | Histogram | `operation` | `perceive`, `communicate`, `narrate`, or `completion` (default internal). Wall time for LLM `completion` calls. |
| `ethos_kernel_chat_turn_duration_seconds` | Histogram | `path` | End-to-end time for one `process_chat_turn` in the worker thread. `path` matches chat result (`light`, `heavy`, `safety_block`, `kernel_block`, …). |
| `ethos_kernel_chat_turns_total` | Counter | `path` | Count of completed turns per `path` (increments with the histogram observation). |
| `ethos_kernel_malabs_blocks_total` | Counter | `reason` | Coarse block reason; typically `safety_block` or `kernel_block` when the chat path indicates a block. |
| `ethos_kernel_dao_ws_operations_total` | Counter | `operation` | Mock DAO WebSocket actions, e.g. `list`, `submit_draft`, `vote`, `resolve`, `integrity_alert`, `nomad_migration`. |
| `ethos_kernel_embedding_errors_total` | Counter | `source` | Semantic MalAbs embedding tier: `http` (request/transport failure), `http_invalid` (bad payload), `backend` (adapter `embedding()` exception). |
| `ethos_kernel_semantic_malabs_outcomes_total` | Counter | `outcome` | Semantic tier path: `allow_low_similarity`, `block_high_similarity`, `embed_unavailable_defer`, `ambiguous_fail_safe_block`, `ambiguous_arbiter_*`, etc. ([`semantic_chat_gate.py`](../../src/modules/semantic_chat_gate.py)). |

Implementation: [`src/observability/metrics.py`](../src/observability/metrics.py). Log field `request_id` is set when a correlation id exists ([`src/observability/logging_setup.py`](../src/observability/logging_setup.py)).
