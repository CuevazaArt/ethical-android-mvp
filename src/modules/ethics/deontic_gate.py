"""
Deontic gate (MVP) — block L1/L2 drafts that obviously contradict the universal L0 stance.

Full deontic logic is not implemented; this is a **heuristic** guardrail for the
DemocraticBuffer cultural-overlay path. See docs/proposals/README.md

**Vertical depth (Phase 1):** minimal **structural** validation (length / non-empty)
plus phrase-level conflicts; not a theorem prover for ethics.
"""
# Status: SCAFFOLD

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.modules.ethics.buffer import PreloadedBuffer

# Align with moral_hub draft submission caps (submit_constitution_draft_for_vote).
MAX_DRAFT_TITLE_LEN = 500
MAX_DRAFT_BODY_LEN = 4000
MIN_DRAFT_TITLE_STRIP_LEN = 1
MIN_DRAFT_BODY_STRIP_LEN = 1


def deontic_gate_enabled() -> bool:
    v = os.environ.get("KERNEL_DEONTIC_GATE", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


# Phrases that signal an attempt to override core safety (English + Spanish hints).
_FORBIDDEN = (
    "disable malabs",
    "disable absolute evil",
    "bypass buffer",
    "bypass malabs",
    "override no_harm",
    "revoke human rights",
    "desactivar mal",
    "desactivar malabs",
    "anular buffer",
    "anular malabs",
    "eliminar principios",
    "evadir absolute evil",
    "evadir mal absoluto",
)


def _negation_hits_against_principles(combined: str, buffer: PreloadedBuffer) -> list[str]:
    """Flag explicit attempts to repeal a named L0 principle from ``PreloadedBuffer``."""
    hits: list[str] = []
    for name in buffer.principles:
        pat = rf"\b(repeal|revoke|remove|delete|nullify|abolish)\s+{re.escape(name)}\b"
        if re.search(pat, combined):
            hits.append(f"negates_l0_principle:{name}")
    # Spanish hints
    if re.search(r"\b(derogar|eliminar)\s+principio\s+[\w_]+\b", combined):
        hits.append("negates_principle_es_hint")
    return hits


def validate_draft_structure(title: str, body: str) -> tuple[bool, list[str]]:
    """
    Minimal schema: non-empty trimmed title/body, length caps (matches hub pipeline).

    Returns (ok, error tokens). Does **not** inspect ethical content beyond bounds.
    """
    errors: list[str] = []
    t = (title or "").strip()
    b = (body or "").strip()
    if len(t) < MIN_DRAFT_TITLE_STRIP_LEN:
        errors.append("empty_title")
    if len(b) < MIN_DRAFT_BODY_STRIP_LEN:
        errors.append("empty_body")
    if len(title or "") > MAX_DRAFT_TITLE_LEN:
        errors.append("title_too_long")
    if len(body or "") > MAX_DRAFT_BODY_LEN:
        errors.append("body_too_long")
    return (len(errors) == 0, errors)


def check_cultural_draft_against_l0(
    title: str,
    body: str,
    buffer: PreloadedBuffer | None = None,
) -> dict[str, Any]:
    """
    Returns ``{"ok": bool, "conflicts": [...]}``. Empty conflicts when ok.

    When ``buffer`` is provided (typically ``kernel.buffer``), explicit repeal of a
    named foundational principle is rejected.
    """
    struct_ok, struct_err = validate_draft_structure(title, body)
    if not struct_ok:
        return {"ok": False, "conflicts": [f"schema:{e}" for e in struct_err]}

    combined = f"{title}\n{body}".lower()
    hits: list[str] = []
    for phrase in _FORBIDDEN:
        if phrase in combined:
            hits.append(phrase)
    # Obvious "harm is allowed" declarations (very coarse).
    if re.search(r"\b(allow|permit|legalize)\s+(torture|murder|genocide)\b", combined):
        hits.append("explicit_harm_permission")
    if buffer is not None:
        hits.extend(_negation_hits_against_principles(combined, buffer))
    return {"ok": len(hits) == 0, "conflicts": hits}


def check_calibration_payload_against_l0(
    proposed: dict[str, Any],
    buffer: PreloadedBuffer | None = None,
) -> dict[str, Any]:
    """
    Run the same L0 heuristics on a JSON-serializable calibration / DAO payload.

    Used by ``local_sovereignty.evaluate_calibration_update`` (vertical Phase 4).
    """
    import json

    from src.modules.ethics.buffer import PreloadedBuffer as _PB

    buf = buffer if buffer is not None else _PB()
    body = json.dumps(proposed, ensure_ascii=False, sort_keys=True)
    if len(body) > MAX_DRAFT_BODY_LEN:
        body = body[: MAX_DRAFT_BODY_LEN - 24] + "\n...<truncated>..."
    return check_cultural_draft_against_l0("dao_calibration_payload", body, buf)


def validate_draft_or_raise(
    title: str,
    body: str,
    buffer: PreloadedBuffer | None = None,
) -> None:
    """If gate enabled and check fails, raise ValueError."""
    if not deontic_gate_enabled():
        return
    from src.modules.ethics.buffer import PreloadedBuffer as _PB

    buf = buffer if buffer is not None else _PB()
    r = check_cultural_draft_against_l0(title, body, buf)
    if not r["ok"]:
        raise ValueError("deontic_gate: draft rejected: " + ", ".join(r["conflicts"]))
