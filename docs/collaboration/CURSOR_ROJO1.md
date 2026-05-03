# Cursor Rojo1 — adversarial validation lane (Team Cursor)

**Role:** Named execution slot on the **`master-Cursor`** hub for **red-team style** checks: adversarial prompts, integration gates, and documentation alignment with safety and operator expectations.

**Scope (non-exclusive):**

- Run `python scripts/eval/adversarial_suite.py` before promoting changes toward `master-antigravity` (see [`AGENTS.md`](../../AGENTS.md)).
- Keep [`ADVERSARIAL_ROBUSTNESS_PLAN.md`](../proposals/ADVERSARIAL_ROBUSTNESS_PLAN.md) and [`INPUT_TRUST_THREAT_MODEL.md`](../proposals/INPUT_TRUST_THREAT_MODEL.md) in mind when touching MalAbs, semantic gates, or chat surfaces.
- Prefer the **Cursor integration gate** ([`scripts/eval/run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py)) for cross-module regression on shared chat/kernel paths.

**Hierarchy:** Same as other L2 Cursor agents — [`ONBOARDING.md`](../../ONBOARDING.md); hub branch [`MULTI_OFFICE_GIT_WORKFLOW.md`](MULTI_OFFICE_GIT_WORKFLOW.md); English-only merged artifacts per [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

**Note:** “Rojo” here means the **adversarial / safety-validation** lane, not a separate Git branch unless your team creates one (e.g. topic branch off `master-Cursor`).

## Worktrees

Git **worktrees** (multiple working directories, one `.git`) are optional. They do **not** change hub rules: cut topic branches from **`master-Cursor`**, sync peers per Rule C‑1 ([`MULTI_OFFICE_GIT_WORKFLOW.md`](MULTI_OFFICE_GIT_WORKFLOW.md)), and use the merge/hub quick reference ([`MERGE_AND_HUB_DECISION_TREE.md`](MERGE_AND_HUB_DECISION_TREE.md)). Promotion readiness is unchanged: [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) (pytest gate + adversarial suite). Branch naming examples (including `claude/<worktree-name>`) are in [`docs/CONTRIBUTING.md`](../CONTRIBUTING.md) — distinct from the root [`CONTRIBUTING.md`](../../CONTRIBUTING.md) language/process entry.

## Roadmap index (where “what’s next” lives)

| Doc | Role |
|-----|------|
| [`STRATEGY_AND_ROADMAP.md`](../proposals/STRATEGY_AND_ROADMAP.md) | Product/ops synthesis, risks, high-level readjustment (English). |
| [`ROADMAP_PRACTICAL_PHASES.md`](../ROADMAP_PRACTICAL_PHASES.md) | Practical phased checklist (eval runners, CI-oriented notes); complements the two above. |
| [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](../proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md) | LLM stack vertical (touchpoints, async-timeout, optional `run_llm_vertical_tests.py`); cross-check with integration gate lists. |
| [`MERGE_AND_HUB_DECISION_TREE.md`](MERGE_AND_HUB_DECISION_TREE.md) | Where daily work lands (`master-*`, peers, `main`). |
