# Proposal — perception observability contract for chat JSON

## Goal

Provide a stable operator-facing contract for perception diagnostics regardless of LLM/backend fallback mode.

## Decision (implemented baseline)

When a chat turn includes perception, the WebSocket JSON payload includes:

1. `perception.coercion_report` with canonical keys (normalized from any partial report, including local heuristic paths).
2. `perception_observability` summary:
   - `uncertainty`
   - `dual_high_discrepancy`
   - `backend_degraded`
   - `metacognitive_doubt`
3. Optional `perception_backend_banner=true` when `session_banner_recommended` is set by degradation policy.

## Why

- Avoid schema drift across fallback paths.
- Keep operator dashboards stable.
- Make degraded perception states explicit and machine-consumable.

## Code and tests

- Implementation: [`src/chat_server.py`](../../src/chat_server.py)
- Canonical report normalization: [`src/modules/perception_schema.py`](../../src/modules/perception_schema.py)
- Tests: [`tests/test_perception_observability_contract.py`](../../tests/test_perception_observability_contract.py)

## Scope note

This is a baseline for the perception path. Future revisions may extend the same contract style to other LLM touchpoints.
