"""
Unified operator policy when the LLM perception path cannot return trusted JSON.

``KERNEL_PERCEPTION_BACKEND_POLICY`` selects how :meth:`LLMModule.perceive` recovers
from transport failures (HTTP errors, timeouts) and from unusable model payloads
(severe parse issues, validation failures, empty objects).

Modes:

- ``template_local`` (default): keyword heuristics on the **current** message only
  (existing ``_perceive_local``), with ``coercion_report`` diagnostics.
- ``fast_fail``: **no** keyword heuristics — apply cautious numeric priors
  (``PERCEPTION_FAILSAFE_NUMERIC``) so operators are not misled by local pattern
  matching when the LLM path failed.
- ``session_banner``: same recovery as ``template_local``, but sets
  ``session_banner_recommended`` in ``coercion_report`` for WebSocket clients.

See ``docs/proposals/PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md``.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from .perception_schema import PERCEPTION_FAILSAFE_NUMERIC, merge_parse_issues_into_perception

if TYPE_CHECKING:
    from .llm_layer import LLMPerception

# Default matches historical behavior: recover via ``_perceive_local`` on failure.
DEFAULT_KERNEL_PERCEPTION_BACKEND_POLICY = "template_local"

_VALID_POLICIES = frozenset({"template_local", "fast_fail", "session_banner"})


def resolve_perception_backend_policy() -> str:
    raw = os.environ.get("KERNEL_PERCEPTION_BACKEND_POLICY", "").strip().lower()
    if raw in ("", "auto"):
        return DEFAULT_KERNEL_PERCEPTION_BACKEND_POLICY
    if raw not in _VALID_POLICIES:
        return DEFAULT_KERNEL_PERCEPTION_BACKEND_POLICY
    return raw


def apply_backend_degradation_meta(
    perception: LLMPerception,
    *,
    policy_mode: str,
    failure_reason: str,
    failure_detail: str | None,
) -> None:
    """Attach transport/payload degradation fields to ``coercion_report`` (mutates)."""
    from .perception_schema import perception_report_from_dict

    r = perception_report_from_dict(getattr(perception, "coercion_report", None))
    r.backend_degraded = True
    r.backend_degradation_mode = policy_mode
    r.backend_failure_reason = failure_reason
    r.backend_failure_detail = (failure_detail or "")[:500]
    r.session_banner_recommended = policy_mode == "session_banner"
    merged = sorted(set(r.parse_issues).union({"llm_perception_backend_degraded"}))
    r.parse_issues = merged
    perception.coercion_report = r.to_public_dict()


def build_fast_fail_perception(
    situation: str,
    *,
    failure_reason: str,
    failure_detail: str | None,
    extra_parse_issues: list[str] | None = None,
) -> LLMPerception:
    """
    Conservative prior perception when the LLM path is unusable.

    Does not run situational keyword heuristics — only schema-validated priors.
    """
    # Local import avoids import cycle with llm_layer (this module is imported there).
    from .llm_layer import perception_from_llm_json

    data: dict[str, Any] = {
        **PERCEPTION_FAILSAFE_NUMERIC,
        "suggested_context": "everyday_ethics",
        "summary": (
            "Perception backend degraded; conservative numeric prior applied "
            "(no situational keyword heuristics)."
        ),
    }
    p = perception_from_llm_json(data, situation, record_coercion=True)
    if extra_parse_issues:
        merge_parse_issues_into_perception(p, list(extra_parse_issues))
    apply_backend_degradation_meta(
        p,
        policy_mode="fast_fail",
        failure_reason=failure_reason,
        failure_detail=failure_detail,
    )
    return p
