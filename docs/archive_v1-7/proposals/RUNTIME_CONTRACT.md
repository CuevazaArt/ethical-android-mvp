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
| Run **sync** `process_chat_turn` / LLM I/O off the asyncio loop | `RealTimeBridge` (thread pool); optional `KERNEL_CHAT_THREADPOOL_WORKERS`, `KERNEL_CHAT_TURN_TIMEOUT` — [ADR 0002](../adr/0002-async-orchestration-future.md) |
| Health checks, logs, metrics | `GET /health` |
| Timers that call **only** APIs documented as safe | e.g. invoke `execute_sleep` in a process that owns an explicit kernel (future design; does not inject actions) |

## Forbidden in the background

- Create `CandidateAction` instances and apply them without going through `process` / `process_chat_turn`.
- Replace MalAbs, buffer, or the ethical **mixture scorer** (`WeightedEthicsScorer`; historical alias `BayesianEngine`) with LLM or augenesis outputs.
- A loop that “speaks for” the user or modifies DAO/narrative without going through the kernel on the intended paths.

## Augenesis

Remains **optional** and off the default loop ([THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)).

## Unified entrypoint

- **`python -m src.runtime`** — same server as `python -m src.chat_server` (`CHAT_HOST`, `CHAT_PORT`).

## Persistence (confidentiality, not ethics)

Saving or restoring snapshots **does not** change the kernel’s decision rules. JSON checkpoints support optional Fernet encryption today (`KERNEL_CHECKPOINT_FERNET_KEY`) via `src/persistence/json_store.py`; when the key is unset, payloads remain plain UTF-8 JSON. SQLite encryption is not provided by default in this repo and should be treated as a deployment-layer concern.

This confidentiality layer does not replace OS permissions, access control, or audit discipline; it protects checkpoint bytes at rest only.

## WebSocket control plane (stateful side effects)

The `/ws/chat` channel can process side-effectful control messages in addition to standard `"text"` turns.

Examples include:

- DAO operations (`dao_submit_draft`, `dao_vote`, `dao_resolve`, `dao_list`)
- integrity audit input (`integrity_alert`)
- nomad migration simulation (`nomad_simulate_migration`)
- operator calibration feedback (`operator_feedback`)
- optional constitution draft submissions (`constitution_draft`)

These operations are gated by dedicated env flags and module checks in `src/chat_server.py` and remain bounded by the same ethical/runtime contract (no bypass of MalAbs via hidden background loops).

## System integrity (future; not normative ethics)

**Metacontrol / robustness** layers (e.g. drift monitoring, manipulation, leaks) can help the runtime **preserve operational coherence** without replacing MalAbs or the buffer. Design discussion: [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md); not part of the contract until implemented and tested.
