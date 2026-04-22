"""
Guardian Angel — Optional care routines and tone adjustment for vulnerable users.

Consolidated module for managing the KERNEL_GUARDIAN_MODE and its routines.
"""

from __future__ import annotations

import json
import os
import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)
_MAX_ROUTINES = 16
_ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,47}$")

@dataclass(frozen=True)
class GuardianRoutine:
    id: str
    title: str
    hint: str


def is_guardian_mode_active() -> bool:
    """Return True if Guardian Angel mode is enabled via KERNEL_GUARDIAN_MODE."""
    v = os.environ.get("KERNEL_GUARDIAN_MODE", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def guardian_routines_feature_enabled() -> bool:
    """Return True if KERNEL_GUARDIAN_ROUTINES is enabled."""
    v = os.environ.get("KERNEL_GUARDIAN_ROUTINES", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _parse_one_routine(raw: Any) -> GuardianRoutine | None:
    if not isinstance(raw, dict):
        return None
    rid = raw.get("id")
    if not isinstance(rid, str) or not _ID_RE.match(rid.strip().lower()):
        return None
    rid = rid.strip().lower()
    title = str(raw.get("title", "")).strip()[:120]
    hint = str(raw.get("hint", "")).strip()[:400]
    if not title or not hint:
        return None
    return GuardianRoutine(id=rid, title=title, hint=hint)


def load_guardian_routines_from_path(path: Path | str) -> list[GuardianRoutine]:
    p = Path(path)
    if not p.is_file():
        return []
    try:
        text = p.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return []

    items: Any
    if isinstance(data, dict) and "routines" in data:
        items = data.get("routines")
    elif isinstance(data, list):
        items = data
    else:
        return []

    if not isinstance(items, list):
        return []

    out: list[GuardianRoutine] = []
    for x in items:
        gr = _parse_one_routine(x)
        if gr:
            out.append(gr)
        if len(out) >= _MAX_ROUTINES:
            break
    return out


_cached_path: str = ""
_cached_routines: list[GuardianRoutine] = []


def get_guardian_routines() -> list[GuardianRoutine]:
    """Load routines from KERNEL_GUARDIAN_ROUTINES_PATH with caching."""
    global _cached_path, _cached_routines
    if not guardian_routines_feature_enabled():
        return []
    raw = os.environ.get("KERNEL_GUARDIAN_ROUTINES_PATH", "").strip()
    if not raw:
        return []
    if raw != _cached_path:
        _cached_routines = load_guardian_routines_from_path(raw)
        _cached_path = raw
    return _cached_routines


def guardian_mode_llm_context() -> str:
    """Return the context string to append to LLM prompts when in Guardian mode."""
    if not is_guardian_mode_active():
        return ""
    
    base = (
        "Operating mode: Guardian Angel — the audience may include children or vulnerable people. "
        "Use calm, reassuring, age-appropriate language; encourage respect and healthy habits; "
        "never claim medical, legal, or emergency authority; direct life-threatening situations to "
        "human emergency services. The ethical decision is already fixed."
    )
    
    routines = get_guardian_routines()
    if not routines:
        return base
        
    lines = [
        base,
        "",
        "Care routines registered by the operator (hints for supportive tone only):",
    ]
    for r in routines:
        lines.append(f"- [{r.id}] {r.title} — {r.hint}")
    return "\n".join(lines)


def public_routines_snapshot() -> list[dict[str, str]]:
    """Minimal JSON for WebSocket consumption."""
    if not guardian_routines_feature_enabled():
        return []
    return [{"id": r.id, "title": r.title} for r in get_guardian_routines()]
