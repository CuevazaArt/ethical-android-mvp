"""
Perception validation circuit breaker (metacognitive doubt).

When ``KERNEL_PERCEPTION_CIRCUIT`` is on (default), consecutive **stressed** perception
parses (from ``coercion_report`` — includes Pydantic validation failures via
``pydantic_emergency_fallback`` in :mod:`perception_schema`) increment a streak. After **more than two** consecutive
stressed turns (third hit), the kernel enters **metacognitive doubt**: DAO calibration line, optional Prometheus counter, WebSocket flag, ``gray_zone`` communication mode, and a
caution hint for the LLM communicator.

Streak resets on any non-stressed turn; metacognitive doubt clears when the streak resets.
"""

from __future__ import annotations

import os
from typing import Any

from src.modules.governance.hub_audit import register_hub_calibration


def perception_circuit_enabled() -> bool:
    v = os.environ.get("KERNEL_PERCEPTION_CIRCUIT", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _is_stress_turn(cr: dict[str, Any] | None) -> bool:
    if not isinstance(cr, dict):
        return False
    if cr.get("non_dict_payload"):
        return True
    if cr.get("pydantic_emergency_fallback"):
        return True
    pi = cr.get("parse_issues") or []
    fd = cr.get("fields_defaulted") or []
    if isinstance(pi, list) and len(pi) > 2:
        return True
    if isinstance(fd, list) and len(fd) > 2:
        return True
    u = cr.get("uncertainty")
    try:
        if u is not None and float(u) >= 0.55:
            return True
    except (TypeError, ValueError):
        pass
    return False


def update_perception_circuit(kernel: Any, perception: Any) -> tuple[bool, bool]:
    """
    Update streak / doubt from ``perception.coercion_report``.

    Returns:
        ``(metacognitive_doubt_active, just_tripped_this_turn)``.
    """
    if not perception_circuit_enabled():
        kernel._perception_validation_streak = 0
        kernel._perception_metacognitive_doubt = False
        return False, False

    cr = getattr(perception, "coercion_report", None)
    crd = cr if isinstance(cr, dict) else None
    if _is_stress_turn(crd):
        kernel._perception_validation_streak = (
            int(getattr(kernel, "_perception_validation_streak", 0)) + 1
        )
    else:
        kernel._perception_validation_streak = 0
        kernel._perception_metacognitive_doubt = False

    just_tripped = False
    if kernel._perception_validation_streak > 2:
        if not bool(getattr(kernel, "_perception_metacognitive_doubt", False)):
            just_tripped = True
        kernel._perception_metacognitive_doubt = True

    return bool(kernel._perception_metacognitive_doubt), just_tripped


def emit_metacognitive_doubt_signals(kernel: Any, *, streak: int) -> None:
    """Audit + metrics when the circuit trips (once per trip)."""
    from src.observability.metrics import record_perception_circuit_trip

    register_hub_calibration(
        kernel.dao,
        "metacognitive_doubt",
        {
            "reason": "perception_validation_streak",
            "streak": streak,
            "note": "Perception parses showed repeated validation stress; tone forced to gray_zone.",
        },
    )
    record_perception_circuit_trip()
