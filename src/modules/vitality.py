"""
Operational vitality hints (v8) — battery as a moral resource signal.

Does not change MalAbs or final_action by itself; feeds sympathetic merge and tone.

**Module S.2.1 (Nomad):** ``merge_nomad_telemetry_into_snapshot`` backfills :class:`SensorSnapshot`
from the latest LAN ``telemetry`` dict (keys aligned with ``SensorSnapshot.from_dict``). This
module treats non-finite floats as missing so thermal / battery alerts never fire on NaN/Inf.

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


def _finite_clamp01(x: float | None) -> float | None:
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    return _clamp01(v)


def _finite_celsius(x: float | None) -> float | None:
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    return v


def _finite_jerk(x: Any) -> float | None:
    """Accelerometer jerk may exceed 1.0; only reject non-finite values (S.2.1)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    return v


def critical_battery_threshold() -> float:
    """
    Below this fraction, battery is treated as **critically low** for signal merge.

    Env: ``KERNEL_VITALITY_CRITICAL_BATTERY`` (default ``0.05``). Invalid values use default.
    """

    raw = os.environ.get("KERNEL_VITALITY_CRITICAL_BATTERY", "").strip()
    if not raw:
        return 0.05
    try:
        t = float(raw)
        if not math.isfinite(t):
            return 0.05
        return _clamp01(t)
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
        v = float(raw)
    except (TypeError, ValueError):
        return 80.0
    if not math.isfinite(v) or v <= 0.0:
        return 80.0
    return v


def thermal_warn_threshold() -> float:
    """
    At or above this core temperature (°C), the device is **thermally elevated** (advisory) but not
    yet critical, using telemetría merged from Nomad (Module S.2.1).

    Env: ``KERNEL_VITALITY_THERMAL_WARN_C`` (default ``70.0``). If the value is not finite, or
    the resolved warn threshold is not strictly below the critical threshold, the warn level is
    coerced to ``max(0, critical - 5.0)`` °C.
    """
    raw = os.environ.get("KERNEL_VITALITY_THERMAL_WARN_C", "").strip()
    if not raw:
        w = 70.0
    else:
        try:
            w = float(raw)
        except (TypeError, ValueError):
            w = 70.0
    if not math.isfinite(w):
        w = 70.0
    c = critical_temperature_threshold()
    if w >= c:
        return max(0.0, c - 5.0)
    return w


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

    # Between warn and critical (Module S.2.1) — e.g. sustained load before throttling
    thermal_elevated: bool
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
            "thermal_elevated": self.thermal_elevated,
            "is_impacted": self.is_impacted,
        }


def _first_finite_number(d: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for k in keys:
        v = d.get(k)
        if v is None:
            continue
        try:
            x = float(v)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(x):
            continue
        return x
    return None


def _coerce_nomad_telemetry_for_snapshot(nomad: dict[str, Any]) -> dict[str, Any]:
    """
    Map common handset / bridge field names to :class:`SensorSnapshot` before ``from_dict``.

    Fills only keys that are still useful for :func:`assess_vitality`; does not override explicit
    ``core_temperature`` if already set.
    """
    d = dict(nomad)
    if d.get("core_temperature") is None:
        t = _first_finite_number(
            d,
            (
                "device_temp_c",
                "cpu_temp_c",
                "cpu_temp",
                "skin_temp_c",
                "thermal_c",
                "temp_c",
            ),
        )
        if t is not None:
            d["core_temperature"] = t
    if d.get("battery_level") is None:
        b = _first_finite_number(d, ("battery", "batt_level", "batt"))
        if b is not None:
            if b > 1.0:
                b = max(0.0, min(1.0, b / 100.0))
            else:
                b = max(0.0, min(1.0, b))
            d["battery_level"] = b
    if d.get("accelerometer_jerk") is None:
        j = _first_finite_number(d, ("jerk", "accel_jerk", "shock"))
        if j is not None:
            # Match :func:`assess_vitality` / :func:`_finite_jerk` — keep finite magnitude, no 0–1 clamp.
            d["accelerometer_jerk"] = j
    return d


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
    patch = SensorSnapshot.from_dict(_coerce_nomad_telemetry_for_snapshot(nomad), strict=False)
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

    if not math.isfinite(t_bat):
        t_bat = 0.05
    if not math.isfinite(t_temp):
        t_temp = 80.0

    if snapshot is None:
        return VitalityAssessment(None, t_bat, False, None, t_temp, False, False, False)

    b = _finite_clamp01(snapshot.battery_level)
    is_bat_critical = False if b is None else (b < t_bat)

    jerk = _finite_jerk(snapshot.accelerometer_jerk)
    is_impacted = False if jerk is None else (jerk > 0.8)

    t_warn = thermal_warn_threshold()
    if not math.isfinite(t_warn):
        t_warn = max(0.0, t_temp - 5.0)
    if t_warn >= t_temp:
        t_warn = max(0.0, t_temp - 5.0)

    temp = _finite_celsius(snapshot.core_temperature)
    is_temp_critical = False if temp is None else (temp >= t_temp)
    is_temp_elevated = (
        False
        if temp is None
        else ((not is_temp_critical) and (float(temp) >= t_warn))
    )

    return VitalityAssessment(
        battery_level=b,
        critical_threshold=t_bat,
        is_critical=is_bat_critical or is_impacted,
        core_temperature=temp,
        temperature_threshold=t_temp,
        thermal_critical=is_temp_critical,
        thermal_elevated=is_temp_elevated,
        is_impacted=is_impacted,
    )


def vitality_communication_hint(assessment: VitalityAssessment, trust_level: float = 1.0) -> str:
    """
    Optional line for LLM weakness context when resources are critical.
    Uchi-Soto Aware: modulates technical disclosure based on trust_level.
    """
    if not (
        assessment.is_critical
        or assessment.thermal_critical
        or assessment.thermal_elevated
    ):
        return ""

    try:
        t_trust = float(trust_level)
    except (TypeError, ValueError):
        t_trust = 0.0
    t_clamp = _finite_clamp01(t_trust)
    is_trusted = t_clamp is not None and t_clamp >= 0.5
    hints = []

    if assessment.is_critical:
        if is_trusted:
            hints.append("Operational battery or physical integrity is critically compromised. Need charging area or safe space.")
        else:
            hints.append("Executing power management or emergency physical protocols; pending non-essential tasks.")

    if assessment.thermal_elevated and not assessment.thermal_critical:
        if is_trusted:
            hints.append("Thermal load elevated: consider reducing sustained compute; monitoring heat.")
        else:
            hints.append("Load management: thermal headroom is reduced; deferring non-urgent work.")

    if assessment.thermal_critical:
        if is_trusted:
            hints.append("Thermal critical: core temperature high. Processing power is degraded.")
        else:
            hints.append("System load management active; maintaining safety margins.")

    return " ".join(hints)
