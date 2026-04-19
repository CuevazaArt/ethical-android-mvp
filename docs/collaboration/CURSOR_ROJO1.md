# Cursor Rojo1 — adversarial validation lane (Team Cursor)

**Role:** Named execution slot on the **`master-Cursor`** hub for **red-team style** checks: adversarial prompts, integration gates, and documentation alignment with safety and operator expectations.

**Scope (non-exclusive):**

- Run `python scripts/eval/adversarial_suite.py` before promoting changes toward `master-antigravity` (see [`AGENTS.md`](../../AGENTS.md)).
- Keep [`ADVERSARIAL_ROBUSTNESS_PLAN.md`](../proposals/ADVERSARIAL_ROBUSTNESS_PLAN.md) and [`INPUT_TRUST_THREAT_MODEL.md`](../proposals/INPUT_TRUST_THREAT_MODEL.md) in mind when touching MalAbs, semantic gates, or chat surfaces.
- Prefer the **Cursor integration gate** ([`scripts/eval/run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py)) for cross-module regression on shared chat/kernel paths.

**Hierarchy:** Same as other L2 Cursor agents — [`ONBOARDING.md`](../../ONBOARDING.md); hub branch [`MULTI_OFFICE_GIT_WORKFLOW.md`](MULTI_OFFICE_GIT_WORKFLOW.md); English-only merged artifacts per [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

**Note:** “Rojo” here means the **adversarial / safety-validation** lane, not a separate Git branch unless your team creates one (e.g. topic branch off `master-Cursor`).
