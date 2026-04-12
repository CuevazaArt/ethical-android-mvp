"""
Guardian Angel mode — optional presentation layer for vulnerable users.

When active (``KERNEL_GUARDIAN_MODE``), a fixed tone block is passed to
``LLMModule.communicate`` only; it does **not** change MalAbs, Bayes, buffer,
or will. See docs/proposals/PROPOSAL_GUARDIAN_ANGEL.md
"""

from __future__ import annotations

import os


def is_guardian_mode_active() -> bool:
    """
    Return True if Guardian Angel mode is enabled for this process.

    Env: ``KERNEL_GUARDIAN_MODE`` — ``1`` / ``true`` / ``yes`` / ``on`` to enable;
    default **off** (explicit opt-in for child-/vulnerability-oriented tone).
    """

    v = os.environ.get("KERNEL_GUARDIAN_MODE", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def guardian_mode_llm_context() -> str:
    """
    Non-empty only when :func:`is_guardian_mode_active` is True.

    Appended to the LLM user block as style guidance; empty string when mode off.
    Optionally appends **care routines** from :mod:`guardian_routines` when enabled.
    """

    if not is_guardian_mode_active():
        return ""
    base = (
        "Operating mode: Guardian Angel — the audience may include children or vulnerable people. "
        "Use calm, reassuring, age-appropriate language; encourage respect and healthy habits; "
        "never claim medical, legal, or emergency authority; direct life-threatening situations to "
        "human emergency services. The ethical decision is already fixed."
    )
    try:
        from .guardian_routines import guardian_routines_llm_suffix
    except ImportError:
        return base
    extra = guardian_routines_llm_suffix()
    if not extra:
        return base
    return f"{base}\n\n{extra}"
