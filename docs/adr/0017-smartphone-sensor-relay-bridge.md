# ADR 0017 — Smartphone sensor relay bridge (PC ↔ phone, field tests)

**Status:** Proposed  
**Date:** 2026-04-15  
**Depends on:** —  
**Related:**
[ADR 0002](0002-async-orchestration-future.md) (thread offload),
[ADR 0008](0008-runtime-observability-prometheus-and-logs.md) (observability),
[`PROPOSAL_FIELD_TEST_PLAN.md`](../proposals/PROPOSAL_FIELD_TEST_PLAN.md),
[`src/modules/sensor_contracts.py`](../../src/modules/sensor_contracts.py),
[`src/modules/hardware_abstraction.py`](../../src/modules/hardware_abstraction.py),
[`src/real_time_bridge.py`](../../src/real_time_bridge.py),
[`src/chat_server.py`](../../src/chat_server.py).

---

## Context

The Ethos Kernel accepts physical-world sensor signals via the optional `sensor`
field on every `/ws/chat` WebSocket frame (`SensorSnapshot` in
`sensor_contracts.py`). Until now, sensors are either:

- **absent** (no `sensor` key in the client frame), or
- **simulated** via `KERNEL_SENSOR_FIXTURE` / `KERNEL_SENSOR_PRESET`.

Field tests (see `PROPOSAL_FIELD_TEST_PLAN.md`) require **real** sensor data
from a smartphone. The phone must relay battery, accelerometer jerk, ambient
microphone level, silence, and optionally coarse location or camera cues —
exactly the fields already declared in `SensorSnapshot`.

Two design pressures:

1. **No kernel logic on the phone.** All decisions stay on the PC. The phone is
   a **sensor relay and minimal UI** only, matching `ComputeTier.EDGE_MOBILE`
   as *device label* while the kernel runs at `SERVER_MID`.
2. **No new large surface.** The transport must reuse the existing WebSocket
   and FastAPI server, with the smallest possible addition.

### Alternatives considered

| Option | Rejected because |
|--------|-----------------|
| Native Android/iOS app | Distribution overhead; out of scope for field test phase. |
| Separate HTTP micro-service for sensor aggregation | Adds another port, process, and auth surface. |
| Polling REST endpoint on the phone | Race conditions with the per-turn sensor window; no real-time feel. |
| Fully async kernel (true push model) | ADR 0002 defers full async kernel; blocking on that blocks all field tests. |

**Decision: PWA served inline by `chat_server`, connecting over a single
LAN WebSocket session with a pairing token.**

---

## Decision

### 1. Phone client: inline PWA

`chat_server` gains one feature-flagged route (`KERNEL_FIELD_CONTROL=1`):

```
GET /phone   →  serves phone_relay.html (single-file PWA)
```

The HTML file is embedded as a Python string constant (no template engine,
no build step, < 400 lines). It handles:

- Pairing flow (posts token to `/control/pair`).
- `navigator.getBattery()`, `DeviceMotionEvent`, `AudioWorklet` (or
  `ScriptProcessorNode` fallback) → normalised `[0, 1]` floats.
- Periodic WebSocket frames to `/ws/chat` carrying the `sensor` JSON field.
  The frame also carries a sentinel `"role": "sensor_relay"` so the server
  can reject misrouted operator-chat messages from the phone.
- Four-button UI: *Start*, *Pause*, *End*, *Trusted place* toggle.
- Live readback: echoes the last `final_action` returned by the kernel.

No app-store submission. No native build. Works on iOS Safari ≥ 15 and
Android Chrome ≥ 95.

### 2. Minimal HTTP control surface (`/control/*`)

Three new HTTP endpoints, all gated behind `KERNEL_FIELD_CONTROL=1`:

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/control/pair` | Accepts `{"token": "…"}`, returns a short-lived session credential (`field_session_id`). Token must match `KERNEL_FIELD_PAIRING_TOKEN` env var. |
| `GET`  | `/control/status` | Returns `{state, session_id, last_sensor_ts, uptime_s, decision_count}`. |
| `POST` | `/control/session` | Accepts `{"action": "pause"|"resume"|"end"}`. On `end`: flushes session manifest to `experiments/out/field/<session_id>/manifest.json` and closes the phone WebSocket. |

Credentials are `itsdangerous.URLSafeTimedSerializer` tokens (HMAC, 1 h TTL)
signed with `SECRET_KEY` env var. If `itsdangerous` is absent the server logs
a warning and falls back to a plain-token compare (lab-only degradation).

### 3. Sensor frame rate limiting

A **token-bucket** guard in `RealTimeBridge` limits inbound sensor frames from
field relay sessions:

```python
KERNEL_FIELD_SENSOR_HZ = int(os.getenv("KERNEL_FIELD_SENSOR_HZ", "2"))
```

Default: 2 Hz (one frame every 500 ms). Frames arriving faster are silently
dropped; only the most recent snapshot in the window is applied to the next
`process_chat_turn` call. This prevents a misbehaving phone from saturating
the chat thread pool.

### 4. Session manifest

On `end` (or server shutdown with an active field session), the server writes:

```json
{
  "schema": "field_session_manifest_v1",
  "session_id": "…",
  "commit": "…",
  "profile": "…",
  "phone_ua": "…",
  "started_at": "ISO-8601",
  "ended_at": "ISO-8601",
  "decision_count": 42,
  "sensor_frames_received": 480,
  "sensor_frames_applied": 84,
  "env_overrides": ["KERNEL_MULTIMODAL_AUDIO_STRONG", "…"],
  "output_files": ["decisions.jsonl", "sidecar.jsonl"]
}
```

The manifest is **not committed** to the repo; it stays under
`experiments/out/field/` (gitignored for the `out/` subtree per field test
policy).

### 5. Audit integration

When `KERNEL_AUDIT_SIDECAR_PATH` is set, `MockDAO.register_audit` emits an
extra line for each event:

- `field_session_paired` — phone connected, token validated.
- `field_session_sensor_hz_capped` — frame dropped by token bucket.
- `field_session_ended` — normal or server-shutdown.

This keeps the governance ledger continuous with the session lifecycle.

### 6. Security constraints (lab scope)

- LAN-only. `KERNEL_FIELD_ALLOW_WAN=0` (default) rejects non-RFC-1918 source
  IPs at the pairing endpoint.
- Pairing token printed once to stdout, never echoed in logs.
- Credentials have a 1-hour TTL; re-pairing is required per session.
- No raw audio, video frames, or biometric data is persisted — only the scalar
  summaries already defined in `SensorSnapshot`.
- HTTPS is **not required** for F0–F3 field tests (see
  `PROPOSAL_FIELD_TEST_PLAN.md`). The manifest records the TLS state.
- Future production use **must** add TLS and a proper secret store before
  exposing beyond a trusted LAN.

---

## Consequences

**Positive:**
- Reuses the existing WebSocket path, thread pool, and sensor merge logic
  without changes to `EthicalKernel` or `SensorSnapshot`.
- No new runtime dependencies beyond optional `itsdangerous`.
- The phone client is a single HTML file — reviewable in one sitting.
- All field-test behaviour is behind `KERNEL_FIELD_CONTROL=1`; default
  deployments are unaffected.

**Negative / risks:**
- DeviceMotion and microphone access require HTTPS or `localhost` in most
  browsers. Lab field tests on a LAN IP must either use a self-signed cert or
  accept that the jerk / noise channels may be unavailable on some handsets.
  Mitigation: document this in the phone UI; gracefully degrade to `null`
  fields which `SensorSnapshot.from_dict` already handles.
- The inline PWA string constant will become hard to maintain if the UI grows.
  If the phone client exceeds ~600 lines, move it to `src/static/phone_relay.html`
  and load with `pathlib.Path.read_text()`.
- Token-bucket rate limiting is per-bridge-instance; a multi-process deploy
  (e.g., multiple uvicorn workers) would need a shared counter. Not a concern
  for single-process field tests.

---

## Implementation checklist

- [ ] `src/chat_server.py` — add `GET /phone`, `/control/*` under
      `KERNEL_FIELD_CONTROL` guard.
- [ ] `src/real_time_bridge.py` — add `FieldSensorRateLimiter` (token bucket).
- [ ] `src/static/phone_relay.html` (or inline string) — PWA implementation.
- [ ] `src/modules/hardware_abstraction.py` — add `EDGE_MOBILE_RELAY` label
      constant for the `HardwareContext` emitted when a phone relay is active.
- [ ] `src/modules/mock_dao.py` — add three field-session audit event types.
- [ ] `tests/test_field_control.py` — unit tests: pairing, rate limiter,
      manifest flush.
- [ ] `experiments/out/field/.gitignore` — exclude `*.jsonl`, `manifest.json`.
- [ ] `.env.example` — document `KERNEL_FIELD_CONTROL`, `KERNEL_FIELD_PAIRING_TOKEN`,
      `KERNEL_FIELD_SENSOR_HZ`, `KERNEL_FIELD_ALLOW_WAN`.
