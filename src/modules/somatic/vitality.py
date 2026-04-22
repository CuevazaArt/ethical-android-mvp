"""
Operational vitality hints (v8) — battery as a moral resource signal.

Does not change MalAbs or final_action by itself; feeds sympathetic merge and tone.

See docs/proposals/README.md §1–2
"""
# Status: SCAFFOLD


from __future__ import annotations

import asyncio
import logging
import math
import os
import time
from dataclasses import dataclass, fields, replace
from typing import Any

from src.modules.perception.sensor_contracts import SensorSnapshot

_log = logging.getLogger(__name__)
_thermal_interrupt_latch = False


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

    Phase 12.2: Uses dynamic baseline if available (μ + 4σ), otherwise falls back to env/default.
    """
    from src.modules.perception.sensor_calibration import get_sensor_calibrator

    calibrator = get_sensor_calibrator()
    if calibrator.is_complete:
        return calibrator.get_threshold("core_temperature", sigma=4.0, default=80.0)

    raw = os.environ.get("KERNEL_VITALITY_CRITICAL_TEMP", "").strip()
    if not raw:
        return 80.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 80.0


def critical_jerk_threshold() -> float:
    """
    Above this accelerometer jerk (m/s³), somatic impact is treated as **critical**.

    Phase 12.2: Uses dynamic baseline if available (μ + 5σ), otherwise falls back to default.
    """
    from src.modules.perception.sensor_calibration import get_sensor_calibrator

    calibrator = get_sensor_calibrator()
    if calibrator.is_complete:
        # High sigma for jerk to allow common movement but catch impacts
        return calibrator.get_threshold("accelerometer_jerk", sigma=5.0, default=0.8)

    raw = os.environ.get("KERNEL_VITALITY_CRITICAL_JERK", "").strip()
    if not raw:
        return 0.8
    try:
        return _clamp01(float(raw))
    except (TypeError, ValueError):
        return 0.8


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
    """
    t0 = time.perf_counter()
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

    latency = (time.perf_counter() - t0) * 1000
    if latency > 1.0:
        _log.debug("Vitality: merge_nomad_telemetry_into_snapshot latency = %.2fms", latency)

    if not overrides:
        return snapshot
    return replace(snapshot, **overrides)


def apply_nomad_telemetry_if_enabled(snapshot: SensorSnapshot | None) -> SensorSnapshot | None:
    """
    Legacy wrapper: merges Nomad telemetry from the bridge if KERNEL_NOMAD_TELEMETRY_VITALITY=1.
    """
    from src.kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_TELEMETRY_VITALITY"):
        return snapshot

    from src.modules.perception.nomad_bridge import get_nomad_bridge

    bridge = get_nomad_bridge()
    with bridge._telemetry_lock:
        raw = bridge._latest_telemetry

    return merge_nomad_telemetry_into_snapshot(snapshot, raw)


def reset_thermal_interrupt_latch_for_tests():
    """Utility for test suites."""
    global _thermal_interrupt_latch
    _thermal_interrupt_latch = False


def impact_jerk_threshold() -> float:
    """Legacy helper for tests."""
    return critical_jerk_threshold()


def assess_vitality(
    snapshot: SensorSnapshot | None,
    *,
    temperature_threshold: float | None = None,
    jerk_threshold: float | None = None,
) -> VitalityAssessment:
    """Derive vitality from sensor snapshot (battery & thermal).

    Args:
        snapshot: Current sensor snapshot.
        temperature_threshold: Optional override (°C) from :class:`SensorBaselineCalibrator`.
            When provided, replaces the ``KERNEL_VITALITY_CRITICAL_TEMP`` env default.
        jerk_threshold: Optional override (normalised [0,1]) from the calibrator.
            When provided, replaces the ``KERNEL_VITALITY_CRITICAL_JERK`` env default.
    """
    t0 = time.perf_counter()

    global _thermal_interrupt_latch

    t_bat = critical_battery_threshold()
    t_temp = (
        temperature_threshold
        if (temperature_threshold is not None and math.isfinite(temperature_threshold))
        else critical_temperature_threshold()
    )
    t_jerk = (
        jerk_threshold
        if (jerk_threshold is not None and math.isfinite(jerk_threshold))
        else critical_jerk_threshold()
    )

    use_hyst = os.environ.get("KERNEL_VITALITY_THERMAL_HYSTERESIS", "0") == "1"

    if snapshot is None:
        if use_hyst:
            _thermal_interrupt_latch = False
        return VitalityAssessment(None, t_bat, False, None, t_temp, False, False)

    b = snapshot.battery_level
    is_bat_critical = False if b is None else (b < t_bat)

    jerk = snapshot.accelerometer_jerk
    # Swarm Rule 2: Anti-NaN check for jerk
    if jerk is not None and not math.isfinite(jerk):
        jerk = 0.0

    is_impacted = False if jerk is None else (jerk > t_jerk)

    temp = snapshot.core_temperature
    # Swarm Rule 2: Anti-NaN check for temp
    if temp is not None and not math.isfinite(temp):
        temp = 40.0  # Default safe temp

    is_temp_critical = False if temp is None else (temp >= t_temp)

    # Bloque S.2.1: elevated band logic
    # Nomad real telemetry (raw skin/core) may be above warning but below critical
    warn_temp = os.environ.get("KERNEL_VITALITY_WARNING_TEMP", "70")
    try:
        t_warn = float(warn_temp)
    except (TypeError, ValueError):
        t_warn = 70.0
    is_temp_elevated = False if temp is None else (temp >= t_warn)

    # Bloque S.2: Calibración de criticidad (Batería O Impacto)
    # Thermal is tracked separately via thermal_critical — it does not
    # count as a full is_critical event (battery/impact override).
    is_critical_combined = is_bat_critical or is_impacted

    res = VitalityAssessment(
        battery_level=b,
        critical_threshold=t_bat,
        is_critical=is_critical_combined,
        core_temperature=temp,
        temperature_threshold=t_temp,
        thermal_critical=is_temp_critical,
        is_impacted=is_impacted,
        thermal_elevated=is_temp_elevated,
    )

    latency = (time.perf_counter() - t0) * 1000
    if latency > 1.0:
        _log.debug("VitalityAssessment: assess_vitality latency = %.2fms", latency)

    return res


def vitality_communication_hint(assessment: VitalityAssessment, trust_level: float = 1.0) -> str:
    """
    Optional line for LLM weakness context when resources are critical.
    Uchi-Soto Aware: modulates technical disclosure based on trust_level.
    """
    if not (assessment.is_critical or assessment.thermal_critical or assessment.thermal_elevated):
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
            hints.append(
                "Operational battery or physical integrity is critically compromised. Need charging area or safe space."
            )
        else:
            hints.append(
                "Executing power management or emergency physical protocols; pending non-essential tasks."
            )

    if assessment.thermal_critical:
        if is_trusted:
            hints.append(
                "My internal core temperature is critically high, causing thermal tension and degraded processing power."
            )
        else:
            hints.append("System load management active; maintaining safety margins.")

    return " ".join(hints)


_nomad_telemetry_consumer: NomadTelemetryConsumer | None = None


class NomadTelemetryConsumer:
    """
    Consumes telemetry updates from the NomadBridge asynchronously and
    updates the global sensor state or individual snapshot buffers.
    """

    def __init__(self):
        self._task: asyncio.Task | None = None
        self.latest_raw: dict[str, Any] = {}

    @property
    def latest_telemetry(self) -> dict[str, Any]:
        """Alias for ``latest_raw`` (integration tests / Module S.1)."""
        return dict(self.latest_raw) if isinstance(self.latest_raw, dict) else {}

    def start(self):
        self._task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        from src.modules.perception.nomad_bridge import get_nomad_bridge

        bridge = get_nomad_bridge()
        while True:
            try:
                raw = await bridge.telemetry_queue.get()
                if isinstance(raw, dict):
                    self.latest_raw = raw
                    # Phase 12.2: Feed the calibrator with latest telemetry
                    from src.modules.perception.sensor_calibration import get_sensor_calibrator
                    from src.modules.perception.sensor_contracts import SensorSnapshot

                    calibrator = get_sensor_calibrator()
                    if calibrator.is_active:
                        snap = SensorSnapshot.from_dict(raw, strict=False)
                        calibrator.update(snap)
            except asyncio.CancelledError:
                break
            except Exception as e:
                import logging

                logging.getLogger(__name__).error("Error in NomadTelemetryConsumer: %s", e)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


def get_nomad_telemetry_consumer_optional() -> NomadTelemetryConsumer | None:
    """Return the active :class:`NomadTelemetryConsumer` if started."""
    return _nomad_telemetry_consumer


def start_nomad_telemetry_consumer_from_env() -> NomadTelemetryConsumer | None:
    """
    Start the background telemetry drain when KERNEL_NOMAD_TELEMETRY_CONSUMER=1.
    """
    global _nomad_telemetry_consumer
    from src.kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_TELEMETRY_CONSUMER"):
        return None
    if _nomad_telemetry_consumer is not None:
        return _nomad_telemetry_consumer

    _nomad_telemetry_consumer = NomadTelemetryConsumer()
    _nomad_telemetry_consumer.start()
    import logging

    logging.getLogger(__name__).info("NomadTelemetryConsumer started.")
    return _nomad_telemetry_consumer


async def stop_nomad_telemetry_consumer_async() -> None:
    """Graceful stop for telemetry background task."""
    global _nomad_telemetry_consumer
    c = _nomad_telemetry_consumer
    _nomad_telemetry_consumer = None
    if c is not None:
        await c.stop()
        import logging

        logging.getLogger(__name__).info("NomadTelemetryConsumer stopped.")
