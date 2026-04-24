"""
Recovery when generative LLM calls for **communication** or **narrative** fail or return unusable JSON.

Parallels :mod:`perception_backend_policy` (perception uses structured priors + ``coercion_report``).
Here, recovery is template text only (no ethics impact on ``final_action``).

Precedence for **communicate** and **narrate** is documented in
``docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md``:

1. ``KERNEL_LLM_TP_COMMUNICATE_POLICY`` / ``KERNEL_LLM_TP_NARRATE_POLICY``
2. ``KERNEL_LLM_VERBAL_FAMILY_POLICY`` (applies when a per-touchpoint key is unset)
3. ``KERNEL_VERBAL_LLM_BACKEND_POLICY`` (legacy)
4. ``KERNEL_LLM_GLOBAL_DEFAULT_POLICY`` when valid for verbal (``template_local`` / ``canned_safe``)
5. default ``template_local``

**Policy values**

- ``template_local`` (default): existing rich templates via :meth:`LLMModule._communicate_local`
  / :meth:`LLMModule._narrate_local`.
- ``canned_safe``: short, explicitly degraded English copy when the remote path fails or JSON is
  unusable — avoids relying on keyword heuristics in templates for operators who want a **narrow**
  verbal surface on LLM outage (similar spirit to perception ``fast_fail``).

Degradation events are logged on :class:`LLMModule` for WebSocket observability (see ``kernel`` /
``chat_server``).
"""
# Status: SCAFFOLD

from __future__ import annotations

import os

from src.modules.cognition.llm_touchpoint_policies import (
    ENV_VERBAL_FAMILY_POLICY,
    TOUCHPOINT_COMMUNICATE,
    TOUCHPOINT_NARRATE,
    raw_global_default_policy,
    raw_touchpoint_policy,
)

# Default matches historical behavior: full local templates on generative failure.
DEFAULT_KERNEL_VERBAL_LLM_BACKEND_POLICY = "template_local"

_VALID_POLICIES = frozenset({"template_local", "canned_safe"})


def resolve_verbal_llm_backend_policy(*, touchpoint: str = "communicate") -> str:
    """Resolve verbal JSON policy for ``communicate`` or ``narrate``."""
    slug = touchpoint.strip().lower()
    if slug not in (TOUCHPOINT_COMMUNICATE, TOUCHPOINT_NARRATE):
        slug = TOUCHPOINT_COMMUNICATE
    tp = raw_touchpoint_policy(slug)
    if tp and tp in _VALID_POLICIES:
        return tp
    fam = os.environ.get(ENV_VERBAL_FAMILY_POLICY, "").strip().lower()
    if fam and fam in _VALID_POLICIES:
        return fam
    raw = os.environ.get("KERNEL_VERBAL_LLM_BACKEND_POLICY", "").strip().lower()
    if raw in _VALID_POLICIES:
        return raw
    # Legacy unset, auto, or invalid → optional global default, then built-in default.
    g = raw_global_default_policy()
    if g and g in _VALID_POLICIES:
        return g
    return DEFAULT_KERNEL_VERBAL_LLM_BACKEND_POLICY


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
            "Estoy procediendo con el curso de acción comprometido. "
            "La ruta del modelo de lenguaje no estaba disponible, por lo que esta respuesta utiliza una frase segura fija."
        )
        tone = "calm"
        hax = "Postura firme; ancho de banda expresivo limitado."
    elif mode == "gray_zone":
        message = (
            "Mantengo la incertidumbre deliberadamente y me moveré con cuidado. "
            "La redacción generativa está degradada; las afirmaciones se mantienen acotadas."
        )
        tone = "narrative"
        hax = "Luz tenue, gestos medidos."
    else:
        message = (
            f"Me he comprometido a: {readable}. "
            "La redacción narrativa completa no está disponible; esta es una respuesta concisa de respaldo."
        )
        tone = "narrative"
        hax = "Manos abiertas, cadencia constante."

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
