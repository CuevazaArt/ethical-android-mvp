# Proposal — unified perception backend degradation policy

**Cross-touchpoint precedence:** [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) — `KERNEL_LLM_TP_PERCEPTION_POLICY` overrides `KERNEL_PERCEPTION_BACKEND_POLICY` when set and valid.

## Problem

Local inference (Ollama and similar) can fail or return unusable structured output. Operators need a **single, documented recovery posture** instead of ad-hoc silent fallbacks.

## Decision (implemented)

Introduce ``KERNEL_PERCEPTION_BACKEND_POLICY`` with three modes:

| Mode | Recovery | Session banner |
|------|----------|----------------|
| ``template_local`` (default) | Keyword heuristics on the **current** message only (``LLMModule._perceive_local``), plus ``coercion_report`` diagnostics | Off |
| ``fast_fail`` | **No** keyword heuristics — cautious numeric priors from ``PERCEPTION_FAILSAFE_NUMERIC`` | Off |
| ``session_banner`` | Same as ``template_local`` | Sets ``session_banner_recommended``; WebSocket JSON may include ``perception_backend_banner`` |

Invalid or empty env values fall back to ``template_local``.

## Code

| Piece | Role |
|--------|------|
| [`src/modules/perception_backend_policy.py`](../../src/modules/perception_backend_policy.py) | ``DEFAULT_KERNEL_PERCEPTION_BACKEND_POLICY``, ``resolve_perception_backend_policy``, ``build_fast_fail_perception``, ``apply_backend_degradation_meta`` |
| [`src/modules/llm_layer.py`](../../src/modules/llm_layer.py) | ``LLMModule.perceive`` uses policy on transport errors and unusable payloads |
| [`src/modules/perception_schema.py`](../../src/modules/perception_schema.py) | ``PerceptionCoercionReport`` fields: ``backend_degraded``, ``backend_failure_reason``, ``session_banner_recommended``, uncertainty bump |
| [`src/chat_server.py`](../../src/chat_server.py) | Optional top-level ``perception_backend_banner`` when ``session_banner_recommended`` |

## Failure reasons (stable strings)

Recorded in ``coercion_report.backend_failure_reason``:

- ``llm_completion_exception`` — HTTP/backend error during completion
- ``llm_payload_severe_parse`` — severe parse issues with ``KERNEL_PERCEPTION_PARSE_FAIL_LOCAL``
- ``llm_payload_validate_exception`` — Pydantic/validation failure after parse
- ``llm_payload_empty_or_invalid`` — empty or non-object JSON payload

## Evidence posture

Default numeric priors are **engineering choices** (same family as fail-safe priors), not an external benchmark. The policy improves **operator honesty** (visible degradation) rather than claiming new calibration.

## Tests

- [`tests/test_perception_backend_policy.py`](../../tests/test_perception_backend_policy.py)
