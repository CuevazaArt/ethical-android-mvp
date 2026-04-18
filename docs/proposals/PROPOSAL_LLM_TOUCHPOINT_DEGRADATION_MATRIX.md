# LLM touchpoint degradation matrix (operator + contributor reference)

**Language:** English (durable record per repository policy).

This path is the **canonical URL** referenced from [`AGENTS.md`](../../AGENTS.md), [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md), [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md), and related docs. The **full precedence tables, embedding-vs-completion notes, and touchpoint matrix** live in:

**[`docs/archive_v1-7/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](../archive_v1-7/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md)**

Edit the archive copy when changing operator semantics; keep this stub until L1 consolidates LLM operator prose under `docs/proposals/`.

---

## Summary (non-authoritative)

- **Runtime implementation:** [`src/modules/llm_touchpoint_policies.py`](../../src/modules/llm_touchpoint_policies.py), perception/verbal resolvers, [`src/modules/llm_layer.py`](../../src/modules/llm_layer.py).
- **Health payload:** `GET /health` → `llm_degradation` matches resolver precedence — see archive body.
