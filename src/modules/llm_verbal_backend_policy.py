"""
Recovery when generative LLM calls for **communication** or **narrative** fail or return unusable JSON.

Parallels :mod:`perception_backend_policy` (perception uses structured priors + ``coercion_report``).
Here, recovery is template text only (no ethics impact on ``final_action``).

``KERNEL_VERBAL_LLM_BACKEND_POLICY``:

- ``template_local`` (default): existing rich templates via :meth:`LLMModule._communicate_local`
  / :meth:`LLMModule._narrate_local`.
- ``canned_safe``: short, explicitly degraded English copy when the remote path fails or JSON is
  unusable — avoids relying on keyword heuristics in templates for operators who want a **narrow**
  verbal surface on LLM outage (similar spirit to perception ``fast_fail``).

Degradation events are logged on :class:`LLMModule` for WebSocket observability (see ``kernel`` /
``chat_server``).
"""

from __future__ import annotations

import os

# Default matches historical behavior: full local templates on generative failure.
DEFAULT_KERNEL_VERBAL_LLM_BACKEND_POLICY = "template_local"

_VALID_POLICIES = frozenset({"template_local", "canned_safe"})


def resolve_verbal_llm_backend_policy() -> str:
    raw = os.environ.get("KERNEL_VERBAL_LLM_BACKEND_POLICY", "").strip().lower()
    if raw in ("", "auto"):
        return DEFAULT_KERNEL_VERBAL_LLM_BACKEND_POLICY
    if raw not in _VALID_POLICIES:
        return DEFAULT_KERNEL_VERBAL_LLM_BACKEND_POLICY
    return raw


def canned_verbal_communication_fields(
    *,
    mode: str,
    action: str,
    failure_reason: str,
) -> dict[str, str]:
    """Short operator-visible lines when ``canned_safe`` recovery is active."""
    readable = (action or "").replace("_", " ") or "the selected action"
    if mode == "D_fast":
        message = (
            "I'm proceeding with the committed course. "
            "The language model path was unavailable, so this reply uses a fixed safe phrasing."
        )
        tone = "calm"
        hax = "Steady posture; limited expressive bandwidth."
    elif mode == "gray_zone":
        message = (
            "I'm holding uncertainty deliberately and will move carefully. "
            "Generative wording is degraded; claims stay narrow."
        )
        tone = "narrative"
        hax = "Dim light, measured gestures."
    else:
        message = (
            f"I've committed to: {readable}. "
            "Full narrative phrasing is unavailable; this is a concise fallback."
        )
        tone = "narrative"
        hax = "Open hands, steady cadence."

    inner = (
        f"[verbal_llm_degraded] reason={failure_reason!r} policy=canned_safe "
        f"mode={mode!r} action={action!r}"
    )
    return {
        "message": message,
        "tone": tone,
        "hax_mode": hax,
        "inner_voice": inner,
    }


def canned_rich_narrative_fields(
    *,
    action: str,
    failure_reason: str,
) -> dict[str, str]:
    readable = (action or "").replace("_", " ") or "this choice"
    note = (
        "Narrative generation was unavailable; this is a uniform degraded placeholder "
        "until the model path recovers."
    )
    line = f"Regarding {readable}: {note}"
    return {
        "compassionate": line,
        "conservative": line,
        "optimistic": line,
        "synthesis": f"Values still attach to {readable}; generative morals deferred ({failure_reason}).",
    }
