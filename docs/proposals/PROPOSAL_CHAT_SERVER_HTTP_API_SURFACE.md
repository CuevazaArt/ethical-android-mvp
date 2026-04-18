# Chat server — HTTP / REST-style JSON surface

**Status:** Reference (implements **read-mostly** JSON over HTTP; primary UX is WebSocket).  
**Language:** English (durable record per repository policy).  
**Implementation:** [`src/chat_server.py`](../../src/chat_server.py) — FastAPI.

An archived copy exists under [`docs/archive_v1-7/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](../archive_v1-7/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md); **this file is the canonical contract** for paths linked from [`AGENTS.md`](../../AGENTS.md) and operator docs.

---

## Summary

The kernel chat server exposes **GET** endpoints returning JSON (or Prometheus text for `/metrics`). There is **no** general REST CRUD API for ethics decisions; deliberation runs in **`process_chat_turn`** via **WebSocket** `/ws/chat`.

The **`nomad_bridge`** field on **`GET /health`** reflects the shared [`get_nomad_bridge()`](../../src/modules/nomad_bridge.py) singleton (queue stats, effective LAN payload **`limits`**, and last telemetry **key names** only — Module S.1 / S.2.1). The Nomad LAN WebSocket app (`/ws/nomad` on the `NomadBridge` FastAPI app) is deployed according to runtime layout; stats are still useful when the bridge process shares that singleton with the chat server.

---

## Endpoints

| Path | Method | Auth | Response |
|------|--------|------|----------|
| `/` | GET | None | JSON: `service`, `websocket`, pointers to other routes, optional `runtime_profile` |
| `/health` | GET | None | JSON: `status`, `version`, `uptime_seconds`, `observability`, `chat_bridge`, `safety_defaults`, `llm_degradation`, **`nomad_bridge`** (schema `nomad_bridge_queue_stats_v2`: queue depths + **`limits`** + `latest_telemetry_present` / `latest_telemetry_keys` — telemetry **values** not included), optional `runtime_profile` |
| `/metrics` | GET | None | Prometheus text if `KERNEL_METRICS=1` (includes `ethos_kernel_lan_envelope_replay_cache_events_total` for LAN envelope replay-cache activity); else 404 JSON; 503 if `prometheus_client` missing |
| `/constitution` | GET | None | L0 constitution JSON if `KERNEL_MORAL_HUB_PUBLIC=1`; else 404 JSON |
| `/dao/governance` | GET | None | JSON meta for DAO WebSocket messages (`dao_list`, `dao_vote`, …) |
| `/nomad/migration` | GET | None | JSON meta for nomad simulation WebSocket message shape |

---

## OpenAPI / Swagger

- **Off by default** (LAN posture). Set **`KERNEL_API_DOCS=1`** to expose `/docs`, `/redoc`, `/openapi.json` (see [`chat_server.py`](../../src/chat_server.py) docstring).

---

## WebSocket (not HTTP REST)

- **`/ws/chat`** — bidirectional JSON; see root `GET /` `protocol` field and README WebSocket section.
- **LAN integrity batch (DJ-BL-02):** ``lan_governance_integrity_batch`` when ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` and ``KERNEL_DAO_INTEGRITY_AUDIT_WS=1`` — see contract matrix.
- **LAN envelope (DJ-BL-07/08/09/10/11/12):** ``lan_governance_envelope`` (`schema=lan_governance_envelope_v1`) routes by `kind` to LAN batch handlers and returns ACK metadata (`fingerprint`, `audit_ledger_fingerprint`, `idempotency_token`, `ack`, optional `reject_reason`, and `cache` stats); duplicate envelopes in the same WebSocket session are short-circuited as `ack=already_seen` with TTL/LRU-bounded replay cache; when `KERNEL_METRICS=1`, replay-cache hits/misses/evictions also increment Prometheus counters (see `/metrics`).
- **LAN coordinator (DJ-BL-13):** ``lan_governance_coordinator`` (`schema=lan_governance_coordinator_v1`) carries an `items` array of inner ``lan_governance_envelope_v1`` objects; responses include `lan_governance.coordinator` with per-item apply results. When inner batches report merge conflicts (DJ-BL-14), the coordinator may add `aggregated_event_conflicts`; when inner batches echo frontier witness resolution (DJ-BL-16), it may add `aggregated_frontier_witness_resolutions`. Multiple LAN keys in one message shallow-merge under `lan_governance`.
- **LAN merge conflict taxonomy (DJ-BL-14):** integrity/DAO/judicial/mock-court LAN batches accept optional `merge_context` (`frontier_turn`, `cross_session_hint`, `frontier_witnesses`) and may return `event_conflicts` with `kind` in {`same_turn`, `different_clock`, `stale_event`}, plus optional `merge_context_echo` / `merge_context_warnings` — [`PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](../archive_v1-7/proposals/PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md), [`PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](../archive_v1-7/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md), [`PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md`](../archive_v1-7/proposals/PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md).
- **Replay sidecar (DJ-BL-15):** operators can build `lan_governance_replay_sidecar_v1` JSON from saved `lan_governance` fragments and fingerprint/compare via [`scripts/eval/verify_lan_governance_replay_sidecar.py`](../../scripts/eval/verify_lan_governance_replay_sidecar.py) — [`PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](../archive_v1-7/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md).
- **Frontier witnesses (DJ-BL-16):** optional `merge_context.frontier_witnesses` produces `merge_context_echo.frontier_witness_resolution` (`advisory_aggregate_not_quorum`) — [`PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md`](../archive_v1-7/proposals/PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md).
- **Anchor compare (DJ-BL-17):** [`scripts/eval/compare_audit_ledger_anchor.py`](../../scripts/eval/compare_audit_ledger_anchor.py) for checkpoint-style ledger vs expected fingerprint.

---

## Related

- [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) — `KERNEL_*` families and metrics.  
- [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](../archive_v1-7/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) — governance-related JSON keys.

---

## Changelog

- **2026-04-15:** Initial surface inventory for operator and cross-team contract reviews (see archive for full early log).
- **2026-04-17:** Canonical copy under `docs/proposals/`; **`GET /health`** documents **`nomad_bridge`** (`nomad_bridge_queue_stats_v2`) + Nomad singleton note in Summary; LAN/justice cross-links via `docs/archive_v1-7/proposals/` (not duplicated under `docs/proposals/`).
- **2026-04-17:** **`nomad_bridge.limits`** documented on **`GET /health`** (effective `KERNEL_NOMAD_MAX_*` caps echo; see [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md)).
