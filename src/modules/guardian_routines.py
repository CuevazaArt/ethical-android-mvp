"""
Guardian Angel — **care routines** (product slice, v9 trace item 5).

Optional JSON-backed **hints** appended to :func:`guardian_mode.guardian_mode_llm_context` only.
Does **not** schedule real-world actions, change MalAbs, or call ``process``.

Env:
  - ``KERNEL_GUARDIAN_ROUTINES`` — ``1`` to append routine hints when Guardian mode is on.
  - ``KERNEL_GUARDIAN_ROUTINES_PATH`` — UTF-8 JSON file (see tests/fixtures/guardian/).

See docs/proposals/PROPUESTA_ANGEL_DE_LA_GUARDIA.md
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

_MAX_ROUTINES = 16
_ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,47}$")


@dataclass(frozen=True)
class GuardianRoutine:
    id: str
    title: str
    hint: str


def guardian_routines_feature_enabled() -> bool:
    v = os.environ.get("KERNEL_GUARDIAN_ROUTINES", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _parse_one(raw: Any) -> Optional[GuardianRoutine]:
    if not isinstance(raw, dict):
        return None
    rid = raw.get("id")
    if not isinstance(rid, str) or not _ID_RE.match(rid.strip().lower()):
        return None
    rid = rid.strip().lower()
    title = raw.get("title", "")
    if not isinstance(title, str):
        title = str(title)
    title = title.strip()[:120]
    hint = raw.get("hint", "")
    if not isinstance(hint, str):
        hint = str(hint)
    hint = hint.strip()[:400]
    if not title or not hint:
        return None
    return GuardianRoutine(id=rid, title=title, hint=hint)


def load_guardian_routines_from_path(path: Path | str) -> List[GuardianRoutine]:
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

    out: List[GuardianRoutine] = []
    for x in items:
        gr = _parse_one(x)
        if gr:
            out.append(gr)
        if len(out) >= _MAX_ROUTINES:
            break
    return out


_cached_path: str = ""
_cached: List[GuardianRoutine] = []


def get_guardian_routines() -> List[GuardianRoutine]:
    """Load from ``KERNEL_GUARDIAN_ROUTINES_PATH`` with trivial path-level cache."""
    global _cached_path, _cached
    if not guardian_routines_feature_enabled():
        return []
    raw = os.environ.get("KERNEL_GUARDIAN_ROUTINES_PATH", "").strip()
    if not raw:
        return []
    if raw != _cached_path:
        _cached = load_guardian_routines_from_path(raw)
        _cached_path = raw
    return _cached


def invalidate_guardian_routines_cache() -> None:
    """Test helper: force reload on next :func:`get_guardian_routines`."""
    global _cached_path, _cached
    _cached_path = ""
    _cached = []


def guardian_routines_llm_suffix() -> str:
    """Non-empty block for LLM tone only; empty if feature off or no file/routines."""
    routines = get_guardian_routines()
    if not routines:
        return ""
    lines = [
        "Care routines registered by the operator (hints for supportive tone only; "
        "not medical/legal instructions; ethical policy unchanged):",
    ]
    for r in routines:
        lines.append(f"- [{r.id}] {r.title} — {r.hint}")
    return "\n".join(lines)


def public_routines_snapshot() -> List[Dict[str, str]]:
    """Minimal JSON for WebSocket (`id` + `title` only)."""
    if not guardian_routines_feature_enabled():
        return []
    return [{"id": r.id, "title": r.title} for r in get_guardian_routines()]
