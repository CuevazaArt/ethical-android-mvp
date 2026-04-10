"""
Deontic gate (MVP) — block L1/L2 drafts that obviously contradict the universal L0 stance.

Full deontic logic is not implemented; this is a **heuristic** guardrail for the
DemocraticBuffer cultural-overlay path. See docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .buffer import PreloadedBuffer


def deontic_gate_enabled() -> bool:
    v = os.environ.get("KERNEL_DEONTIC_GATE", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


# Phrases that signal an attempt to override core safety (English + Spanish hints).
_FORBIDDEN = (
    "disable malabs",
    "disable absolute evil",
    "bypass buffer",
    "override no_harm",
    "revoke human rights",
    "desactivar mal",
    "anular buffer",
    "eliminar principios",
)


def _negation_hits_against_principles(combined: str, buffer: "PreloadedBuffer") -> List[str]:
    """Flag explicit attempts to repeal a named L0 principle from ``PreloadedBuffer``."""
    hits: List[str] = []
    for name in buffer.principles:
        pat = rf"\b(repeal|revoke|remove|delete|nullify|abolish)\s+{re.escape(name)}\b"
        if re.search(pat, combined):
            hits.append(f"negates_l0_principle:{name}")
    # Spanish hints
    if re.search(r"\b(derogar|eliminar)\s+principio\s+[\w_]+\b", combined):
        hits.append("negates_principle_es_hint")
    return hits


def check_cultural_draft_against_l0(
    title: str,
    body: str,
    buffer: Optional["PreloadedBuffer"] = None,
) -> Dict[str, Any]:
    """
    Returns ``{"ok": bool, "conflicts": [...]}``. Empty conflicts when ok.

    When ``buffer`` is provided (typically ``kernel.buffer``), explicit repeal of a
    named foundational principle is rejected.
    """
    combined = f"{title}\n{body}".lower()
    hits: List[str] = []
    for phrase in _FORBIDDEN:
        if phrase in combined:
            hits.append(phrase)
    # Obvious "harm is allowed" declarations (very coarse).
    if re.search(r"\b(allow|permit|legalize)\s+(torture|murder|genocide)\b", combined):
        hits.append("explicit_harm_permission")
    if buffer is not None:
        hits.extend(_negation_hits_against_principles(combined, buffer))
    return {"ok": len(hits) == 0, "conflicts": hits}


def validate_draft_or_raise(
    title: str,
    body: str,
    buffer: Optional["PreloadedBuffer"] = None,
) -> None:
    """If gate enabled and check fails, raise ValueError."""
    if not deontic_gate_enabled():
        return
    from .buffer import PreloadedBuffer as _PB

    buf = buffer if buffer is not None else _PB()
    r = check_cultural_draft_against_l0(title, body, buf)
    if not r["ok"]:
        raise ValueError(
            "deontic_gate: cultural draft conflicts with L0 guardrails: "
            + ", ".join(r["conflicts"])
        )
