# Chat server — HTTP / REST-style JSON surface

**Status:** Reference (implements **read-mostly** JSON over HTTP; primary UX is WebSocket).  
**Language:** English (durable record per repository policy).  
**Implementation:** [`src/chat_server.py`](../../src/chat_server.py) — FastAPI.

---

## Summary

The kernel chat server exposes **GET** endpoints returning JSON (or Prometheus text for `/metrics`). There is **no** general REST CRUD API for ethics decisions; deliberation runs in **`process_chat_turn`** via **WebSocket** `/ws/chat`.

---

## Endpoints

| Path | Method | Auth | Response |
|------|--------|------|----------|
| `/` | GET | None | JSON: `service`, `websocket`, pointers to other routes, optional `runtime_profile` |
| `/health` | GET | None | JSON: `status`, `version`, `uptime_seconds`, `observability`, `chat_bridge`, `safety_defaults`, optional `runtime_profile` |
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
- **LAN coordinator (DJ-BL-13):** ``lan_governance_coordinator`` (`schema=lan_governance_coordinator_v1`) carries an `items` array of inner ``lan_governance_envelope_v1`` objects; responses include `lan_governance.coordinator` with per-item apply results. Multiple LAN keys in one message shallow-merge under `lan_governance`.
- **LAN merge conflict taxonomy (DJ-BL-14):** integrity/DAO/judicial/mock-court LAN batches accept optional `merge_context.frontier_turn` and may return `event_conflicts` with `kind` in {`same_turn`, `different_clock`, `stale_event`} — [`PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md).

---

## Related

- [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) — `KERNEL_*` families and metrics.  
- [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) — governance-related JSON keys.

---

## Changelog

- **2026-04-15:** Initial surface inventory for operator and cross-team contract reviews.
- **2026-04-15:** WebSocket note for ``lan_governance_integrity_batch``.
- **2026-04-15:** WebSocket note for ``lan_governance_envelope``.
- **2026-04-15:** Envelope ACK fields note (`idempotency_token`, `ack`, `reject_reason`).
- **2026-04-15:** Envelope replay cache note (`ack=already_seen`).
- **2026-04-15:** Envelope replay cache bounds + ACK cache telemetry.
- **2026-04-15:** `/metrics` note for `ethos_kernel_lan_envelope_replay_cache_events_total` (DJ-BL-12).
- **2026-04-15:** WebSocket note for ``lan_governance_coordinator`` (DJ-BL-13).
- **2026-04-15:** LAN batch `event_conflicts` + `merge_context` note (DJ-BL-14).
