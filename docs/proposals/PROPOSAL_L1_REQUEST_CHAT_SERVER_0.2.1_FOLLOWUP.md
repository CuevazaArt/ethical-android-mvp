# L1 request: Chat server / WebSocket (Block 0.2.1) — follow-up decisions

**Audience:** Antigravity (L1), Juan (L0) as needed.  
**From:** Team Cursor (L2).  
**Status:** Request for planning / ADR / prioritization; **not** a claim that L1 must implement.

## Context (executed on Cursor track, April 2026)

L2 has landed **defensive** changes aligned with 0.2.1 (event-loop safety and operator bounds):

- [`src/real_time_bridge.py`](../../src/real_time_bridge.py): `CHAT_THREADPOOL_MAX_WORKERS` — `KERNEL_CHAT_THREADPOOL_WORKERS` is clamped so a bad env cannot spawn an oversized `ThreadPoolExecutor`.
- [`src/kernel_utils.py`](../../src/kernel_utils.py): I5 temporal modulation — `KERNEL_TEMPORAL_REFERENCE_ETA_S` parsed with `kernel_env_float` (clamped, finite); `perception_uncertainty` / `urgency` merge paths tolerate non-numeric signal values; non-finite ETAs short-circuit without mutating `signals`.
- **Planned in same slice:** WebSocket **inbound** message size cap via `KERNEL_CHAT_WS_MAX_MESSAGE_BYTES` (default 2 MiB, hard cap 32 MiB; values below 64 bytes fall back to default) to limit memory/CPU from malicious or accidental huge JSON before `json.loads`.

These are **hardening** steps. They do **not** complete the plan line “redesign WebSocket layer for pure concurrency / non-blocking loop.”

## What we ask L1 (Antigravity) to decide or schedule

1. **Scope of 0.2.1 “redesign”**  
   - Is the target a **full** contract pass (per-message back-pressure, backpressure on `send_json`, worker isolation for *all* CPU-heavy JSON on the hot path), or a **phased** approach (hardening first, then optional `uvloop` / ASGI tuning)?

2. **ADR for WebSocket + async kernel**  
   - Single ADR that locks: which operations **must** stay on the asyncio loop (`process_chat_turn_stream`, async LLM), which **may** use `RealTimeBridge` / `run_in_threadpool`, and how `KERNEL_CHAT_ASYNC_LLM_HTTP` + tri-lobe interact with deadlines (see ADR 0002). L2 will follow the ADR once published.

3. **Inbound payload policy**  
   - Confirm default **max message bytes** (L2 default 2 MiB) and whether **per-route** limits (e.g. LAN governance batches vs. simple `text` chat) should differ in a later phase.

4. **Kernel init on connect**  
   - `EthicalKernel()` + checkpoint load on each WebSocket session runs on the event loop today. If L1 wants that **off the loop** (thread / process pool), L1 should specify the **contract** (e.g. kernel must be constructible only once per process vs. per connection) so L2 does not fork behavior silently.

5. **Integration funnel**  
   - After L1 response, align `PLAN_WORK_DISTRIBUTION_TREE.md` Block 0.2.1 and [`CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md) “Next track” with the decided phases.

## Out of scope for this request

- DAO / governance contract changes.  
- Replacing FastAPI/Starlette (unless L1 explicitly adds that to 0.2.1).

## References

- [`PLAN_WORK_DISTRIBUTION_TREE.md`](./PLAN_WORK_DISTRIBUTION_TREE.md) — Module 0, Block 0.2.1.  
- [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) — test gate for chat / bridge.  
- ADR 0002 (RealTimeBridge / cooperative cancel) — in-repo cross-references from `src/real_time_bridge.py`.

---

*This proposal exists so L1 has a single, English, reviewable anchor for what L2 already shipped and what still needs L1 direction.*
