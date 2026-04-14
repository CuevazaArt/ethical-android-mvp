# Proposal: verbal / narrative LLM degradation policy

**Status:** Implemented baseline — `KERNEL_VERBAL_LLM_BACKEND_POLICY`, `llm_verbal_backend_policy.py`, `LLMModule` event log, WebSocket `verbal_llm_observability`.

**Team reference (precedence + all touchpoints):** [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md).

## Problem

[`PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md`](PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md) unifies **perception** recovery. **Communication** and **narrative** still used silent `except` + template fallback without a stable operator contract or an optional “narrow verbal surface” mode when the model path fails.

## Policy

| Value | Behavior on generative failure or unusable JSON |
|--------|--------------------------------------------------|
| `template_local` (default) | Existing `_communicate_local` / `_narrate_local` templates. |
| `canned_safe` | Short, explicit degraded English copy (no scenario-specific template heuristics). |

## Observability

- `LLMModule` records `touchpoint` (`communicate` | `narrate`), `failure_reason`, and `recovery_policy` per event (cleared at the start of each chat / `process_natural` turn).
- WebSocket chat JSON: `verbal_llm_observability` when any event exists (see [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md)).

## Evidence posture

This is **engineering / operator-visibility** hardening, not an empirical study of user trust. Defaults preserve historical template behavior.

## Related

- [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3 (aspirational single policy across all LLM touchpoints; perception + verbal baselines now documented separately).
- [`MODEL_CRITICAL_BACKLOG.md`](MODEL_CRITICAL_BACKLOG.md).
