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
| `/metrics` | GET | None | Prometheus text if `KERNEL_METRICS=1`; else 404 JSON; 503 if `prometheus_client` missing |
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
- **LAN envelope (DJ-BL-07):** ``lan_governance_envelope`` (`schema=lan_governance_envelope_v1`) routes by `kind` to LAN batch handlers.

---

## Related

- [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) — `KERNEL_*` families and metrics.  
- [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) — governance-related JSON keys.

---

## Changelog

- **2026-04-15:** Initial surface inventory for operator and cross-team contract reviews.
- **2026-04-15:** WebSocket note for ``lan_governance_integrity_batch``.
- **2026-04-15:** WebSocket note for ``lan_governance_envelope``.
