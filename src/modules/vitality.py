"""
Operational vitality hints (v8) — battery as a moral resource signal.

Does not change MalAbs or final_action by itself; feeds sympathetic merge and tone.

See docs/proposals/README.md §1–2
"""

from __future__ import annotations

import os
from dataclasses import dataclass

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


def critical_temperature_threshold() -> float:
    """
    Above this temperature (°C), somatic tension is treated as **critically high**.

    Env: ``KERNEL_VITALITY_CRITICAL_TEMP`` (default ``80.0``).
    """
    raw = os.environ.get("KERNEL_VITALITY_CRITICAL_TEMP", "").strip()
    if not raw:
        return 80.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 80.0


@dataclass(frozen=True)
class VitalityAssessment:
    """Snapshot of vitality relevant to one chat turn."""

    battery_level: float | None
    critical_threshold: float
    is_critical: bool

    # Phase 8: Somatic Infrastructure
    core_temperature: float | None
    temperature_threshold: float
    thermal_critical: bool

    def to_public_dict(self) -> dict:
        return {
            "battery_level": self.battery_level,
            "critical_threshold": self.critical_threshold,
            "is_critical": self.is_critical,
            "battery_unknown": self.battery_level is None,
            "core_temperature": self.core_temperature,
            "thermal_critical": self.thermal_critical,
        }


def assess_vitality(snapshot: SensorSnapshot | None) -> VitalityAssessment:
    """Derive vitality from sensor snapshot (battery & thermal)."""

    t_bat = critical_battery_threshold()
    t_temp = critical_temperature_threshold()

    if snapshot is None:
        return VitalityAssessment(None, t_bat, False, None, t_temp, False)

    b = snapshot.battery_level
    is_bat_critical = False if b is None else (b < t_bat)

    temp = snapshot.core_temperature
    is_temp_critical = False if temp is None else (temp >= t_temp)

    return VitalityAssessment(
        battery_level=b,
        critical_threshold=t_bat,
        is_critical=is_bat_critical,
        core_temperature=temp,
        temperature_threshold=t_temp,
        thermal_critical=is_temp_critical,
    )


def vitality_communication_hint(assessment: VitalityAssessment, trust_level: float = 1.0) -> str:
    """
    Optional line for LLM weakness context when resources are critical.
    Uchi-Soto Aware: modulates technical disclosure based on trust_level.
    """
    if not (assessment.is_critical or assessment.thermal_critical):
        return ""

    is_trusted = trust_level >= 0.5
    hints = []
    
    if assessment.is_critical:
        if is_trusted:
            hints.append("Operational battery is critically low (under threshold). Need charging area.")
        else:
            hints.append("Executing power management protocols; pending non-essential tasks.")

    if assessment.thermal_critical:
        if is_trusted:
            hints.append("Thermal critical: core temperature high. Processing power is degraded.")
        else:
            hints.append("System load management active; maintaining safety margins.")

    return " ".join(hints)
