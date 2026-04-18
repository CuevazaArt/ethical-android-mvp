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


def critical_impact_threshold() -> float:
    """
    Above this jerk value, the system reports a **critical impact**.
    Env: ``KERNEL_VITALITY_CRITICAL_IMPACT`` (default ``0.8``).
    """
    raw = os.environ.get("KERNEL_VITALITY_CRITICAL_IMPACT", "").strip()
    if not raw:
        return 0.8
    try:
        return float(raw)
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

    # Fase S: Impactos y Propriocepción (S.3)
    is_impacted: bool
    impact_threshold: float
    is_falling: bool
    stability_score: float | None

    def to_public_dict(self) -> dict:
        return {
            "battery_level": self.battery_level,
            "critical_threshold": self.critical_threshold,
            "is_critical": self.is_critical,
            "battery_unknown": self.battery_level is None,
            "core_temperature": self.core_temperature,
            "thermal_critical": self.thermal_critical,
            "is_impacted": self.is_impacted,
            "impact_threshold": self.impact_threshold,
            "is_falling": self.is_falling,
            "stability_score": self.stability_score,
        }


def assess_vitality(snapshot: SensorSnapshot | None) -> VitalityAssessment:
    """Derive vitality from sensor snapshot (battery, thermal, impact, and proprioception)."""

    t_bat = critical_battery_threshold()
    t_temp = critical_temperature_threshold()
    t_impact = critical_impact_threshold()

    if snapshot is None:
        return VitalityAssessment(
            None, t_bat, False, 
            None, t_temp, False, 
            False, t_impact,
            False, None
        )

    b = snapshot.battery_level
    is_bat_critical = False if b is None else (b < t_bat)
    
    jerk = snapshot.accelerometer_jerk
    is_impacted = False if jerk is None else (jerk >= t_impact)

    temp = snapshot.core_temperature
    is_temp_critical = False if temp is None else (temp >= t_temp)

    return VitalityAssessment(
        battery_level=b,
        critical_threshold=t_bat,
        is_critical=is_bat_critical,
        core_temperature=temp,
        temperature_threshold=t_temp,
        thermal_critical=is_temp_critical,
        is_impacted=is_impacted,
        impact_threshold=t_impact,
        is_falling=snapshot.is_falling if snapshot else False,
        stability_score=snapshot.stability_score if snapshot else None
    )


def vitality_communication_hint(assessment: VitalityAssessment, trust_level: float = 1.0) -> str:
    """
    Optional line for LLM weakness context when resources are critical.
    Uchi-Soto Aware: modulates technical disclosure based on trust_level.
    """
    # Any critical condition triggers a hint (Proprioception S3 added)
    if not (assessment.is_critical or assessment.thermal_critical or 
            assessment.is_impacted or assessment.is_falling or 
            (assessment.stability_score is not None and assessment.stability_score < 0.4)):
        return ""

    is_trusted = trust_level >= 0.5
    hints = []
    
    # Falling has the highest conversational priority
    if assessment.is_falling:
        if is_trusted:
             hints.append("Free-fall detected. Somatic orientation is lost.")
        else:
             hints.append("Executing emergency orientation stabilization.")

    # Stability issues (S.3)
    if assessment.stability_score is not None and assessment.stability_score < 0.4:
        if is_trusted:
             hints.append("Postural stability is degraded. Core balance is at risk.")
        else:
             hints.append("Activating secondary balancing protocols.")

    # Impact signals immediate physical trauma
    if assessment.is_impacted and not assessment.is_falling:
        if is_trusted:
             hints.append("Somatic sensors report a severe physical impact. Movement may be erratic.")
        else:
             hints.append("Executing physical integrity stabilization protocols.")

    if assessment.is_critical:
        # Avoid redundant hints if impact already covered 'emergency protocols'
        if is_trusted:
            hints.append("Operational battery is critically compromised. Need charging area.")
        elif not assessment.is_impacted:
            hints.append("Executing power management protocols; pending non-essential tasks.")

    if assessment.thermal_critical:
        if is_trusted:
            hints.append("Thermal critical: core temperature high. Processing power is degraded.")
        else:
            hints.append("System load management active; maintaining safety margins.")

    return " ".join(hints)


import asyncio

class NomadTelemetryConsumer:
    """
    Consumes telemetry payloads from NomadBridge and updates the internal 
    state available for VitalityAssessment.
    """
    def __init__(self):
        self._task: asyncio.Task | None = None
        self.latest_telemetry: dict[str, Any] | None = None

    def start(self):
        self._task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        from .nomad_bridge import get_nomad_bridge
        bridge = get_nomad_bridge()
        while True:
            try:
                self.latest_telemetry = await bridge.telemetry_queue.get()
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


_nomad_telemetry_consumer: NomadTelemetryConsumer | None = None


def get_nomad_telemetry_consumer_optional() -> NomadTelemetryConsumer | None:
    """Return the active consumer, if started."""
    return _nomad_telemetry_consumer


def start_nomad_telemetry_consumer_from_env() -> NomadTelemetryConsumer | None:
    """
    When ``KERNEL_NOMAD_TELEMETRY_CONSUMER`` is set, start draining ``NomadBridge.telemetry_queue``.
    """
    global _nomad_telemetry_consumer
    from ..kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_TELEMETRY_CONSUMER"):
        return None
    if _nomad_telemetry_consumer is not None:
        return _nomad_telemetry_consumer
    
    _nomad_telemetry_consumer = NomadTelemetryConsumer()
    _nomad_telemetry_consumer.start()
    import logging
    logging.getLogger(__name__).info("NomadTelemetryConsumer started (KERNEL_NOMAD_TELEMETRY_CONSUMER=1).")
    return _nomad_telemetry_consumer


async def stop_nomad_telemetry_consumer_async() -> None:
    """Cancel background telemetry consumption."""
    global _nomad_telemetry_consumer
    c = _nomad_telemetry_consumer
    _nomad_telemetry_consumer = None
    if c is not None:
        await c.stop()
        import logging
        logging.getLogger(__name__).info("NomadTelemetryConsumer stopped.")
