"""
Guardian care routines — public API surface for JSON-backed hints.

Implementation lives in :mod:`src.modules.guardian_mode`; this module exists so
imports stay stable for tests and callers (``src.modules.guardian_routines``).
"""
# Status: SCAFFOLD


from __future__ import annotations

from src.modules.safety.guardian_mode import (
    GuardianRoutine,
    get_guardian_routines,
    guardian_routines_feature_enabled,
    guardian_routines_llm_suffix,
    invalidate_guardian_routines_cache,
    load_guardian_routines_from_path,
    public_routines_snapshot,
)

__all__ = [
    "GuardianRoutine",
    "get_guardian_routines",
    "guardian_routines_feature_enabled",
    "guardian_routines_llm_suffix",
    "invalidate_guardian_routines_cache",
    "load_guardian_routines_from_path",
    "public_routines_snapshot",
]
