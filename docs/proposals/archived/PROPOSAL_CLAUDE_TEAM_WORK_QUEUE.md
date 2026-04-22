# Claude Team — work queue and integration gaps (April 2026)

**Audience:** Team Claude (`master-claude`), Antigravity (L1), Juan (L0).  
**Purpose:** Single place to pick up **pending PLAN items** without re-negotiating ownership. Aligns [`PLAN_WORK_DISTRIBUTION_TREE.md`](PLAN_WORK_DISTRIBUTION_TREE.md) with **what is actually wired** in `src/` today.

**Related:** [`CLAUDE_HEMISPHERE_INTEGRATION_SYNTHESIS.md`](CLAUDE_HEMISPHERE_INTEGRATION_SYNTHESIS.md) (Phase 3+ narrative), [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md) (LLM vertical).

---

## Executive snapshot

| Area | PLAN block | Responsibility | Integration status (repo scan) |
|------|------------|------------------|--------------------------------|
| RLHF → Bayesian priors | **C.1.1** | Claude | **Wired (April 2026):** with ``KERNEL_RLHF_MODULATE_BAYESIAN=1``, MalAbs ``rlhf_features`` feed ``maybe_modulate_bayesian_from_malabs`` → ``apply_rlhf_modulation`` after chat MalAbs (`kernel` + `aprocess_natural` path). Tests in [`tests/test_rlhf_reward_model.py`](../../tests/test_rlhf_reward_model.py) (`TestRlhfBayesianBridge`). |
| RLHF vs multipolar stage-3 | **C.1.2** | Claude | **Open:** needs explicit metrics/tests once C.1.1 feeds live scores. |
| Governance vote → MalAbs thresholds | **C.2.1** | Claude | **Partial:** [`multi_realm_governance.py`](../../src/modules/multi_realm_governance.py) + kernel [`governor`](../../src/kernel.py); **hot-reload of `semantic_chat_gate` θ** without process restart — verify event-bus path end-to-end vs PLAN wording. |
| Static limbic tension (persistent threat) | **9.2** | Claude | **Open:** PLAN asks for +5s same-stimulus escalation; needs design against current [`PerceptiveLobe`](../../src/kernel_lobes/perception_lobe.py) / [`BayesianEngine`](../../src/modules/bayesian_engine.py) / limbic tension fields. |
| Basal ganglia / affect smoothing | **10.3** (MER) | Claude (PLAN) | **Partial (April 2026):** [`charm_engine.py`](../../src/modules/charm_engine.py) optionally runs [`BasalGanglia.smooth`](../../src/modules/basal_ganglia.py) on warmth/mystery when `KERNEL_BASAL_GANGLIA_SMOOTHING=1`; tests [`tests/test_charm_engine_basal.py`](../../tests/test_charm_engine_basal.py). Further: wire ethical-lean targets from user model / decision context. |

**Coordination note (Cursor / other L2):** Module **S.1** (Nomad bridge), **0.x** (kernel de-monolith / chat server), and **10.5** MER ADR tests are **Cursor-heavy** in recent merges — avoid duplicating those files; branch from `master-claude` and land via **Integration Pulse** toward `master-antigravity`.

---

## Priority-ordered suggestions for Claude

1. **C.1.2 — Validate drift onto multipolar / stage-3 decisions**  
   - Extend metrics or regression tests once live RLHF priors influence visible [`KernelDecision`](../../src/kernel.py) outputs under controlled fixtures.

2. **C.2.1 — Close the “hot reload” loop**  
   - Document + test: successful `MultiRealmGovernor` vote → updated realm thresholds → **semantic** MalAbs tier reads new θ on **subsequent** turns (per synthesis: no mid-turn drift).  
   - Files: [`semantic_chat_gate.py`](../../src/modules/semantic_chat_gate.py), [`multi_realm_governance.py`](../../src/modules/multi_realm_governance.py), [`kernel_event_bus`](../../src/modules/kernel_event_bus.py) if used.

3. **10.3 — BasalGanglia remainder**  
   - Cursor wired EMA in [`charm_engine.py`](../../src/modules/charm_engine.py) (`KERNEL_BASAL_GANGLIA_SMOOTHING`); next: **persist** smoothed affect in `UserModelTracker` / per-agent state and tune EMA time constant for 3–5 turn transitions (PLAN).

4. **9.2 — Spec + thin spike**  
   - Time-to-stable “danger in view” signal from perception stream; agree with L1 on whether this belongs in `PerceptiveLobe`, a small daemon, or Bayesian metadata before coding large refactors.

---

## What Cursor is *not* claiming here

- No substitute for Claude’s **RLHF + governance** depth; this file only **unblocks prioritization** and records **measurable gaps** from static analysis.  
- Merge to `main` remains **L0** per governance; Claude should use **`master-claude` → `master-antigravity`**.

---

*Prepared as cross-team transparency (AGENTS.md); C.1.1 runtime wiring landed April 2026 (`KERNEL_RLHF_MODULATE_BAYESIAN`).*
