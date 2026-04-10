"""
Operational vitality hints (v8) — battery as a moral resource signal.

Does not change MalAbs or final_action by itself; feeds sympathetic merge and tone.

See docs/discusion/PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md §1–2
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .sensor_contracts import SensorSnapshot


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def critical_battery_threshold() -> float:
    """
    Below this fraction, battery is treated as **critically low** for signal merge.

    Env: ``KERNEL_VITALITY_CRITICAL_BATTERY`` (default ``0.05``). Invalid values use default.
    """

    raw = os.environ.get("KERNEL_VITALITY_CRITICAL_BATTERY", "").strip()
    if not raw:
        return 0.05
    try:
        return _clamp01(float(raw))
    except (TypeError, ValueError):
        return 0.05


@dataclass(frozen=True)
class VitalityAssessment:
    """Snapshot of vitality relevant to one chat turn."""

    battery_level: Optional[float]
    critical_threshold: float
    is_critical: bool

    def to_public_dict(self) -> dict:
        return {
            "battery_level": self.battery_level,
            "critical_threshold": self.critical_threshold,
            "is_critical": self.is_critical,
            "battery_unknown": self.battery_level is None,
        }


def assess_vitality(snapshot: Optional[SensorSnapshot]) -> VitalityAssessment:
    """Derive vitality from sensor snapshot (battery only in MVP)."""

    t = critical_battery_threshold()
    if snapshot is None:
        return VitalityAssessment(None, t, False)
    b = snapshot.battery_level
    if b is None:
        return VitalityAssessment(None, t, False)
    return VitalityAssessment(b, t, b < t)


def vitality_communication_hint(assessment: VitalityAssessment) -> str:
    """Optional line for LLM weakness context when battery is critical."""

    if not assessment.is_critical:
        return ""
    return (
        "Operational vitality is critically low; prioritize essential stewardship and "
        "honest limits on commitments until power is secured."
    )
