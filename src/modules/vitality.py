"""
Operational vitality hints (v8) — battery as a moral resource signal.

Does not change MalAbs or final_action by itself; feeds sympathetic merge and tone.

See docs/proposals/README.md §1–2
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, fields, replace
from typing import Any

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

    # Fase S: Impactos
    is_impacted: bool

    def to_public_dict(self) -> dict:
        return {
            "battery_level": self.battery_level,
            "critical_threshold": self.critical_threshold,
            "is_critical": self.is_critical,
            "battery_unknown": self.battery_level is None,
            "core_temperature": self.core_temperature,
            "thermal_critical": self.thermal_critical,
            "is_impacted": self.is_impacted,
        }


def _coerce_battery_fraction(v: Any) -> float | None:
    """Interpret battery as a [0,1] fraction; values in (1, 100] are treated as legacy percent."""

    if v is None:
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(x) or math.isinf(x):
        return None
    if 1.0 < x <= 100.0:
        x = x / 100.0
    return max(0.0, min(1.0, x))


def normalize_nomad_telemetry_for_sensor_merge(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Map common smartphone / Nomad LAN shorthand keys onto :class:`SensorSnapshot` field names
    before :meth:`SensorSnapshot.from_dict` (Module S.2.1 — Bloque S.2.1 calibration path).
    """

    out = dict(raw)

    if out.get("battery_level") is not None:
        out["battery_level"] = _coerce_battery_fraction(out.get("battery_level"))
    else:
        for key in ("battery", "battery_pct", "batt"):
            if key in out and out[key] is not None:
                out["battery_level"] = _coerce_battery_fraction(out[key])
                break

    if out.get("core_temperature") is None:
        for key in ("core_temperature_c", "temperature_c", "temp_c", "cpu_temp"):
            if key in out and out[key] is not None:
                out["core_temperature"] = out[key]
                break

    if out.get("accelerometer_jerk") is None:
        for key in ("jerk", "accel_jerk", "impact_jerk"):
            if key in out and out[key] is not None:
                out["accelerometer_jerk"] = out[key]
                break

    return out


def merge_nomad_telemetry_into_snapshot(
    snapshot: SensorSnapshot | None,
    nomad: dict[str, Any] | None,
) -> SensorSnapshot | None:
    """
    Module S.2.1 — Merge latest Nomad LAN ``telemetry`` payload into a sensor snapshot.

    Fields already present on ``snapshot`` (e.g. chat ``sensor`` JSON from the operator client)
    take precedence; Nomad only **fills gaps** so real device telemetry can backfill missing
    battery / thermal / jerk hints without overriding an explicit session.
    """
    if not nomad:
        return snapshot
    nomad = normalize_nomad_telemetry_for_sensor_merge(nomad)
    patch = SensorSnapshot.from_dict(nomad, strict=False)
    if snapshot is None:
        return patch

    overrides: dict[str, Any] = {}
    for f in fields(SensorSnapshot):
        name = f.name
        cur = getattr(snapshot, name)
        pat = getattr(patch, name)
        if name == "backup_just_completed":
            merged = bool(cur or pat)
            if merged is not cur:
                overrides[name] = merged
            continue
        if cur is None and pat is not None:
            overrides[name] = pat
    if not overrides:
        return snapshot
    return replace(snapshot, **overrides)


def assess_vitality(snapshot: SensorSnapshot | None) -> VitalityAssessment:
    """Derive vitality from sensor snapshot (battery & thermal)."""

    t_bat = critical_battery_threshold()
    t_temp = critical_temperature_threshold()

    if snapshot is None:
        return VitalityAssessment(None, t_bat, False, None, t_temp, False, False)

    b = snapshot.battery_level
    is_bat_critical = False if b is None else (b < t_bat)
    
    jerk = snapshot.accelerometer_jerk
    is_impacted = False if jerk is None else (jerk > 0.8)

    temp = snapshot.core_temperature
    is_temp_critical = False if temp is None else (temp >= t_temp)

    # Bloque S.2: Calibración de criticidad (Batería O Impacto O Térmico Extremo)
    is_critical_combined = is_bat_critical or is_impacted or is_temp_critical

    return VitalityAssessment(
        battery_level=b,
        critical_threshold=t_bat,
        is_critical=is_critical_combined,
        core_temperature=temp,
        temperature_threshold=t_temp,
        thermal_critical=is_temp_critical,
        is_impacted=is_impacted,
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
            hints.append("Operational battery or physical integrity is critically compromised. Need charging area or safe space.")
        else:
            hints.append("Executing power management or emergency physical protocols; pending non-essential tasks.")

    if assessment.thermal_critical:
        if is_trusted:
            hints.append("Thermal critical: core temperature high. Processing power is degraded.")
        else:
            hints.append("System load management active; maintaining safety margins.")

    return " ".join(hints)
