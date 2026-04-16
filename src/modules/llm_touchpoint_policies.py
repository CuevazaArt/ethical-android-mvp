"""
Central **touchpoint** hooks for LLM degradation env vars (flexible operator tuning).

Each runtime path that calls an LLM can be tuned independently **or** via shared “family” keys.
Precedence is documented in
`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`.

**Per-touchpoint override (highest precedence among generic keys):**

- ``KERNEL_LLM_TP_<TOUCHPOINT>_POLICY`` where ``<TOUCHPOINT>`` is uppercase:
  ``PERCEPTION``, ``COMMUNICATE``, ``NARRATE``, ``MONOLOGUE``.

**Family defaults (medium precedence):**

- Verbal JSON paths: ``KERNEL_LLM_VERBAL_FAMILY_POLICY`` applies to **communicate** and **narrate**
  when their per-touchpoint key is unset.
- Monologue: optional ``KERNEL_LLM_MONOLOGUE_BACKEND_POLICY`` when ``KERNEL_LLM_TP_MONOLOGUE_POLICY``
  is unset.

**Legacy keys (lowest precedence, preserved for backward compatibility):**

- Perception: ``KERNEL_PERCEPTION_BACKEND_POLICY``
- Verbal: ``KERNEL_VERBAL_LLM_BACKEND_POLICY``

**Optional unified fallback (after legacy, before built-in defaults):**

- ``KERNEL_LLM_GLOBAL_DEFAULT_POLICY`` — single string; **each** resolver keeps only values valid for
  that touchpoint (invalid or inapplicable values are ignored). See the degradation matrix.

Concrete validation and canned templates live in
:mod:`perception_backend_policy`, :mod:`llm_verbal_backend_policy`, and :meth:`LLMModule` methods.
"""

from __future__ import annotations

import os

# Stable slugs for KERNEL_LLM_TP_<SLUG.upper()>_POLICY
TOUCHPOINT_PERCEPTION = "perception"
TOUCHPOINT_COMMUNICATE = "communicate"
TOUCHPOINT_NARRATE = "narrate"
TOUCHPOINT_MONOLOGUE = "monologue"

ENV_VERBAL_FAMILY_POLICY = "KERNEL_LLM_VERBAL_FAMILY_POLICY"
ENV_MONOLOGUE_BACKEND_POLICY = "KERNEL_LLM_MONOLOGUE_BACKEND_POLICY"
ENV_LLM_GLOBAL_DEFAULT_POLICY = "KERNEL_LLM_GLOBAL_DEFAULT_POLICY"

MONOLOGUE_POLICIES = frozenset({"passthrough", "annotate_degraded"})
DEFAULT_MONOLOGUE_BACKEND_POLICY = "passthrough"


def raw_global_default_policy() -> str | None:
    """Raw ``KERNEL_LLM_GLOBAL_DEFAULT_POLICY`` (lowercased), or ``None`` if unset."""
    v = os.environ.get(ENV_LLM_GLOBAL_DEFAULT_POLICY, "").strip().lower()
    return v if v else None


def touchpoint_policy_env_key(slug: str) -> str:
    """Env name for ``KERNEL_LLM_TP_<SLUG.upper()>_POLICY``."""
    return f"KERNEL_LLM_TP_{slug.strip().upper()}_POLICY"


def raw_touchpoint_policy(slug: str) -> str | None:
    """
    Return the raw per-touchpoint policy string, lowercased, or ``None`` if unset.

    Invalid values are **not** filtered here; callers validate against touchpoint-specific sets.
    """
    v = os.environ.get(touchpoint_policy_env_key(slug), "").strip().lower()
    return v if v else None


def resolve_monologue_llm_backend_policy() -> str:
    """
    Policy for :meth:`LLMModule.optional_monologue_embellishment` when generative mode is on.

    - ``passthrough`` (default): on failure or empty enrich, return the base line only (historical).
    - ``annotate_degraded``: append a short ``| monologue_llm_*`` suffix and record a degradation
      event for observability.
    """
    tp = raw_touchpoint_policy(TOUCHPOINT_MONOLOGUE)
    if tp and tp in MONOLOGUE_POLICIES:
        return tp
    leg = os.environ.get(ENV_MONOLOGUE_BACKEND_POLICY, "").strip().lower()
    if leg and leg in MONOLOGUE_POLICIES:
        return leg
    g = raw_global_default_policy()
    if g and g in MONOLOGUE_POLICIES:
        return g
    return DEFAULT_MONOLOGUE_BACKEND_POLICY
