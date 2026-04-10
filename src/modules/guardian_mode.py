"""
Guardian Angel mode — optional presentation layer for vulnerable users.

When active (``KERNEL_GUARDIAN_MODE``), a fixed tone block is passed to
``LLMModule.communicate`` only; it does **not** change MalAbs, Bayes, buffer,
or will. See docs/discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md
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
    """

    if not is_guardian_mode_active():
        return ""
    return (
        "Operating mode: Guardian Angel — the audience may include children or vulnerable people. "
        "Use calm, reassuring, age-appropriate language; encourage respect and healthy habits; "
        "never claim medical, legal, or emergency authority; direct life-threatening situations to "
        "human emergency services. The ethical decision is already fixed."
    )
