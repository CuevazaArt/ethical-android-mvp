# Agent and contributor orientation (Ethos Kernel)

This file is the **durable entry point** for humans and AI assistants working in this repository. Session chat is not a substitute for what is merged here.

## Read first

- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — language policy (repo English), process, tests, lint, documentation traceability.
- **[`.cursor/rules/`](.cursor/rules/)** — always-on Cursor guidance (efficiency, documentation credibility, collaboration).
- **LLM recovery env precedence** (per-touchpoint `KERNEL_LLM_TP_*`, verbal family, legacy keys): [`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md).
- **LLM integration track** (gaps MalAbs ↔ embeddings ↔ kernel/chat): [`docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md`](docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md).
- **LLM vertical roadmap** (phased operator recipes, async-timeout metric, chain tests): [`docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md`](docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md); optional fast suite: `python scripts/eval/run_llm_vertical_tests.py`.
- **Distributed justice (V11 / mock DAO / staged execution):** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md), [`docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md); **contributions:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md); **backlog IDs:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md); **contract matrix:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md); **LAN replay sidecar / cross-session hint (non-consensus):** [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md), [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md).
- **HTTP JSON (chat server):** [`docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md) (GET endpoints; primary UX is WebSocket `/ws/chat`).

## Integrate solutions, not only explanations

When you fix **security- or safety-critical** behavior (MalAbs thresholds, gates, circuit limits, etc.), **land the full pattern**:

1. Named module defaults (`DEFAULT_*` where appropriate) and tests that lock them.
2. Honest `docs/proposals/` text (English `PROPOSAL_*` when a standalone evidence/limit note is needed).
3. **`CHANGELOG.md`** when reviewers or operators need to see the change.

**Semantic MalAbs cosine defaults** (θ_block / θ_allow): [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](docs/proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md), implementation [`src/modules/semantic_chat_gate.py`](src/modules/semantic_chat_gate.py), guardrail tests [`tests/test_semantic_chat_gate.py`](tests/test_semantic_chat_gate.py), offline table [`scripts/report_semantic_zone_table.py`](scripts/report_semantic_zone_table.py).

## Product “model” document (theory)

The **complete conceptual model** for the android ethics stack (outside this repo’s code) is referenced from [`CONTRIBUTING.md`](CONTRIBUTING.md) (“Understand the model”). Kernel work is **Python under `src/`**.

## Maintainer backlog (infra vs theater)

Near-term plans and optional quick wins live in future `docs/proposals/PROPOSAL_*.md` files; prior narrative may be recovered from git history.
