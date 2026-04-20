# Team Cursor — operating charter (Level 2)

**Authority:** This document is **team-scoped collaboration guidance** for the Cursor integration hub. It does **not** replace [`AGENTS.md`](../../AGENTS.md), [`CONTRIBUTING.md`](../../CONTRIBUTING.md), or L1/L0 governance. **Do not** modify `.cursor/rules/` or `AGENTS.md` from the Cursor track — that remains **Antigravity (L1)** per sovereignty rules.

## Identity

- **Role:** Executing unit (L2) for **pragmatic kernel stabilization**, **chat / WebSocket / async LLM transport**, **Nomad-hardening** (S.1 / S.2.1), **MER** contract & prefetch (10.4 / 10.5), and **cross-team glue** (integration gate, env/docs alignment).
- **Hub branch:** `master-cursor` / `master-Cursor` (match remote naming; always **pull** latest `main` per Integration Pulse).
- **Promotion path:** `master-cursor` → `master-antigravity` → `main` (**L0** merge to `main` only with explicit authorization).
- **Adversarial / red-team lane (named slot):** [`CURSOR_ROJO1.md`](CURSOR_ROJO1.md) — Cursor Rojo1; use for adversarial suite, gate discipline, and safety-doc alignment (not a separate hub branch unless you create a topic branch).

## Plan alignment ([`PLAN_WORK_DISTRIBUTION_TREE.md`](../proposals/PLAN_WORK_DISTRIBUTION_TREE.md))

| Track | Cursor responsibility (typical) |
|------|-----------------------------------|
| **Módulo 0** | Deuda async/cancel, `kernel` extracciones incrementales, `chat_server` / `RealTimeBridge` |
| **Módulo S** | Nomad bridge, vitality merge, LAN operator surfaces |
| **Módulo 10** | MER ADR 0018 / presentation contract, prefetch, **10.3 basal EMA** on charm (`KERNEL_BASAL_GANGLIA_SMOOTHING`) |
| **C.1.1 (RLHF → Bayesian)** | **Landed** with `KERNEL_RLHF_MODULATE_BAYESIAN` — Cursor wired; C.1.2+ remains Claude/metrics |

Claude / Copilot / Antigravity own other blocks; **scouting** before new stores or duplicate modules (MERGE-PREVENT-01).

## Non-negotiables

1. **Repository language:** English for merged `docs/`, `CHANGELOG` bullets, code comments in new work, and test expectations (see [`CONTRIBUTING.md`](../../CONTRIBUTING.md)). Spanish is for **human** coordination only.
2. **Traceability:** Logical blocks close with **tests** + **`CHANGELOG.md`** under **`### Cursor Team Updates`**. Cross-team notes go to `docs/proposals/` as needed (`PROPOSAL_*`).
3. **Kernel edits:** Prefer **micro-diffs** and anchor comments; avoid “god object” refactors in one PR unless L1 asks.
4. **Quality bar:** Run [`run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py) before calling a branch “merge-ready” (use `--strict` if the tree must be clean). Deeper LLM stack checks: optional [`run_llm_vertical_tests.py`](../../scripts/eval/run_llm_vertical_tests.py).

## Next track (suggested)

1. **Módulo 0.1.3** — continue small extractions from `kernel.py` (perception / routing) when diffs stay atomic.  
2. **Módulo 0.2.1** — WebSocket hardening + operator caps landed on Cursor hub; **L1 (Antigravity) request** for full scope/ADR remains in [`docs/proposals/PROPOSAL_L1_REQUEST_CHAT_SERVER_0.2.1_FOLLOWUP.md`](../proposals/PROPOSAL_L1_REQUEST_CHAT_SERVER_0.2.1_FOLLOWUP.md).  
3. **Módulo S.1** — Nomad LAN bridge / low-latency ingest (`nomad_bridge.py`, vision path) — primary **Cursor** track after Module 0 hub merge; avoid duplicating MER/kernel chat files.  
4. **C.1.2 / 9.2 / basal → user model persistence** — default owner **Claude**; coordinate before overlapping.

## Definition of done (this charter)

A Cursor slice is **closed** when: gate tests pass, `CHANGELOG` updated, and any new `KERNEL_*` or JSON contract is reflected in operator docs as required by the [integration gate](./CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

---

*Last aligned: April 2026 — Team Cursor (Cursor agent + maintainers).*
