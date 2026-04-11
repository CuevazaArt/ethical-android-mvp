# Runtime contract (Phase 1)

The **runtime** is the process that keeps the service alive (e.g. FastAPI + WebSocket). It does **not** redefine ethics.

## Source of ethical truth

- Only `EthicalKernel.process`, `EthicalKernel.process_chat_turn`, `EthicalKernel.process_natural` (and documented paths that delegate to them) determine actions and modes.
- The LLM **does not** set policy.
- **Module-level map (MalAbs → Bayes → action id):** [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) — which stages may veto or select `final_action` vs read-only layers.
- **MockDAO vs L0:** in-memory governance simulation does **not** equal distributed consensus; foundational buffer principles are **not** overridden by votes at runtime — [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md).

## What the runtime may do without breaking the contract

| Allowed | Example |
|---------|---------|
| Start ASGI / uvicorn with the same `app` | `python -m src.runtime`, `python -m src.chat_server`, `uvicorn src.chat_server:app` |
| Async tasks that are **read-only** on the kernel | `src.runtime.telemetry.advisory_loop` (only `DriveArbiter.evaluate`); optional per WebSocket session if `KERNEL_ADVISORY_INTERVAL_S` > 0 |
| Health checks, logs, metrics | `GET /health` |
| Timers that call **only** APIs documented as safe | e.g. invoke `execute_sleep` in a process that owns an explicit kernel (future design; does not inject actions) |

## Forbidden in the background

- Create `CandidateAction` instances and apply them without going through `process` / `process_chat_turn`.
- Replace MalAbs, buffer, or Bayes with LLM or augenesis outputs.
- A loop that “speaks for” the user or modifies DAO/narrative without going through the kernel on the intended paths.

## Augenesis

Remains **optional** and off the default loop ([THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)).

## Unified entrypoint

- **`python -m src.runtime`** — same server as `python -m src.chat_server` (`CHAT_HOST`, `CHAT_PORT`).

## Persistence (confidentiality, not ethics)

Saving or restoring snapshots **does not** change the kernel’s decision rules. In the MVP, checkpoints are **unencrypted**; for sensitive deployments, at-rest encryption is **planned** (e.g. Python `cryptography`) and is described in [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md), not in this contract.

## System integrity (future; not normative ethics)

**Metacontrol / robustness** layers (e.g. drift monitoring, manipulation, leaks) can help the runtime **preserve operational coherence** without replacing MalAbs or the buffer. Design discussion: [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md); not part of the contract until implemented and tested.
