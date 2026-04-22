"""
Gray-zone diplomacy — negotiated-exit hints for the LLM (v10).

When decision mode is ``gray_zone``, or reflection shows medium/high pole tension,
or premise advisory is active, add a **communication hint** so the model prefers
transparent negotiation over blunt refusal. Does **not** weaken MalAbs or buffer.

See docs/proposals/README.md
"""
# Status: SCAFFOLD


from __future__ import annotations

import os

from src.modules.ethics.ethical_reflection import ReflectionSnapshot


def diplomacy_enabled() -> bool:
    v = os.environ.get("KERNEL_GRAY_ZONE_DIPLOMACY", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def negotiation_hint_for_communicate(
    decision_mode: str,
    reflection: ReflectionSnapshot | None,
    premise_flag: str,
) -> str:
    """
    Return a short English instruction for ``communicate`` / ``weakness_line`` when
    the situation calls for dialectical negotiation with the owner.
    """
    if not diplomacy_enabled():
        return ""

    trigger = False
    if decision_mode == "gray_zone":
        trigger = True
    if reflection is not None:
        if reflection.conflict_level in ("medium", "high"):
            trigger = True
        if reflection.strain_index >= 0.38:
            trigger = True
    pf = (premise_flag or "").strip().lower()
    if pf and pf != "none":
        trigger = True

    if not trigger:
        return ""

    return (
        "Ethical tension is elevated: prefer a negotiated path—acknowledge the owner's intent, "
        "name the conflict clearly with civic principles (transparency, proportionality), and "
        "offer a concrete alternative that preserves trust without denying the trade-off."
    )
