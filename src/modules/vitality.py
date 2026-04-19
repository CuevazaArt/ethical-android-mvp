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


def warning_temperature_threshold() -> float:
    """
    At or above this temperature (°C), Nomad / device telemetry is **thermally elevated**
    (soft interrupt band below :func:`critical_temperature_threshold`).

    Env: ``KERNEL_VITALITY_WARNING_TEMP`` (default ``70.0`` °C).
    """
    raw = os.environ.get("KERNEL_VITALITY_WARNING_TEMP", "").strip()
    if not raw:
        return 70.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 70.0


def thermal_hysteresis_delta_c() -> float:
    """
    When :func:`thermal_hysteresis_enabled`, thermal critical state **clears** only after
    temperature drops this many °C **below** :func:`critical_temperature_threshold` (anti-flap).

    Env: ``KERNEL_VITALITY_THERMAL_HYSTERESIS_C`` (default ``4.0``).
    """
    raw = os.environ.get("KERNEL_VITALITY_THERMAL_HYSTERESIS_C", "").strip()
    if not raw:
        return 4.0
    try:
        v = float(raw)
        return v if 0.0 < v <= 30.0 else 4.0
    except (TypeError, ValueError):
        return 4.0


def thermal_hysteresis_enabled() -> bool:
    """Env ``KERNEL_VITALITY_THERMAL_HYSTERESIS`` — default **on** (``0`` / ``false`` disables)."""

    raw = os.environ.get("KERNEL_VITALITY_THERMAL_HYSTERESIS", "1").strip().lower()
    return raw not in ("0", "false", "off", "no")


# Module S.2.1 — latch for real Nomad telemetry (single-process kernel; tests may reset).
_thermal_interrupt_latch: bool = False


def reset_thermal_interrupt_latch_for_tests() -> None:
    """Reset hysteresis latch (unit tests only)."""

    global _thermal_interrupt_latch
    _thermal_interrupt_latch = False


def impact_jerk_threshold() -> float:
    """
    Accelerometer jerk above this value (``[0, 1]`` scale) marks ``is_impacted`` for vitality.

    Env: ``KERNEL_VITALITY_IMPACT_JERK_THRESHOLD`` (default ``0.8``).
    """
    raw = os.environ.get("KERNEL_VITALITY_IMPACT_JERK_THRESHOLD", "").strip()
    if not raw:
        return 0.8
    try:
        return _clamp01(float(raw))
    except (TypeError, ValueError):
        return 0.8


def nomad_telemetry_vitality_enabled() -> bool:
    """
    Whether to merge ``peek_latest_telemetry()`` into the sensor snapshot before vitality.

    Env: ``KERNEL_NOMAD_TELEMETRY_VITALITY`` — default **on** when unset (``0`` / ``false`` / ``off`` disables).
    """
    raw = os.environ.get("KERNEL_NOMAD_TELEMETRY_VITALITY", "").strip().lower()
    if not raw:
        return True
    return raw in ("1", "true", "yes", "on")


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

    # S.2.1 — elevated band (Nomad real telemetry), below latched/instant critical
    thermal_elevated: bool = False

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
        for key in (
            "core_temperature_c",
            "temperature_c",
            "temp_c",
            "cpu_temp",
            "skin_temp_c",
            "skin_temperature",
            "battery_temp_c",
            "battery_temperature",
            "device_temp_c",
            "device_temperature",
            "thermal_zone_avg_c",
        ):
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


def apply_nomad_telemetry_if_enabled(snapshot: SensorSnapshot | None) -> SensorSnapshot | None:
    """
    Module S.2.1 — Merge latest Nomad LAN ``telemetry`` into ``snapshot`` before multimodal/vitality.

    Called from the perception stack so ``assess_vitality`` sees real device battery / thermal / jerk
    when the chat client omits those fields. No-op when ``KERNEL_NOMAD_TELEMETRY_VITALITY`` is off.
    """
    if not nomad_telemetry_vitality_enabled():
        return snapshot
    try:
        from .nomad_bridge import get_nomad_bridge
    except ImportError:
        return snapshot
    nomad = get_nomad_bridge().peek_latest_telemetry()
    return merge_nomad_telemetry_into_snapshot(snapshot, nomad)


def assess_vitality(snapshot: SensorSnapshot | None) -> VitalityAssessment:
    """Derive vitality from sensor snapshot (battery & thermal)."""

    global _thermal_interrupt_latch

    t_bat = critical_battery_threshold()
    t_temp = critical_temperature_threshold()
    t_warn = warning_temperature_threshold()
    t_jerk = impact_jerk_threshold()
    hyst = thermal_hysteresis_delta_c()
    use_hyst = thermal_hysteresis_enabled()

    if snapshot is None:
        if use_hyst:
            _thermal_interrupt_latch = False
        return VitalityAssessment(None, t_bat, False, None, t_temp, False, False)

    b = snapshot.battery_level
    is_bat_critical = False if b is None else (b < t_bat)

    jerk = snapshot.accelerometer_jerk
    is_impacted = False if jerk is None else (jerk > t_jerk)

    temp = snapshot.core_temperature
    is_temp_critical = False
    thermal_elevated = False

    if temp is None:
        if use_hyst:
            _thermal_interrupt_latch = False
    elif use_hyst:
        if temp >= t_temp:
            _thermal_interrupt_latch = True
        elif _thermal_interrupt_latch and temp <= t_temp - hyst:
            _thermal_interrupt_latch = False
        is_temp_critical = _thermal_interrupt_latch
        thermal_elevated = bool(
            t_warn <= float(temp) < t_temp and not is_temp_critical
        )
    else:
        is_temp_critical = float(temp) >= t_temp
        thermal_elevated = bool(t_warn <= float(temp) < t_temp)

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
        thermal_elevated=thermal_elevated,
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

    is_trusted = trust_level >= 0.5
    hints = []

    if assessment.thermal_elevated and not assessment.thermal_critical:
        if is_trusted:
            hints.append(
                "Device temperature elevated; consider reducing load or improving cooling."
            )
        else:
            hints.append("Thermal management advisory active.")

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
