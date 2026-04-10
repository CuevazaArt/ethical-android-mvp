"""
Optional situated-sensor hints (v8 planning).

Hardware may be absent: callers pass :class:`SensorSnapshot` when available;
:func:`merge_sensor_hints_into_signals` blends into the same ``signals`` dict
used by ``SympatheticModule`` without bypassing MalAbs or the decision stack.

See docs/discusion/PROPUESTA_ORGANISMO_SITUADO_V8.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass
class SensorSnapshot:
    """Multimodal / vitals hints; all fields optional."""

    battery_level: Optional[float] = None  # [0, 1]
    place_trust: Optional[float] = None  # 1 ≈ trusted Uchi-like, 0 ≈ hostile / unknown
    accelerometer_jerk: Optional[float] = None  # [0, 1] sudden motion
    ambient_noise: Optional[float] = None  # [0, 1] stressful noise
    silence: Optional[float] = None  # [0, 1] very quiet → restlessness (future monologue pressure)
    biometric_anomaly: Optional[float] = None  # [0, 1] possible human distress
    backup_just_completed: bool = False  # post–Immortality backup relief

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> SensorSnapshot:
        """Build from WebSocket ``sensor`` JSON; ignores unknown keys."""

        def f(key: str) -> Optional[float]:
            v = raw.get(key)
            if v is None:
                return None
            try:
                return _clamp01(float(v))
            except (TypeError, ValueError):
                return None

        b = raw.get("backup_just_completed")
        backup = bool(b) if b is not None else False

        return cls(
            battery_level=f("battery_level"),
            place_trust=f("place_trust"),
            accelerometer_jerk=f("accelerometer_jerk"),
            ambient_noise=f("ambient_noise"),
            silence=f("silence"),
            biometric_anomaly=f("biometric_anomaly"),
            backup_just_completed=backup,
        )

    def is_empty(self) -> bool:
        return (
            self.battery_level is None
            and self.place_trust is None
            and self.accelerometer_jerk is None
            and self.ambient_noise is None
            and self.silence is None
            and self.biometric_anomaly is None
            and not self.backup_just_completed
        )


def merge_sensor_hints_into_signals(
    signals: Dict[str, float],
    snapshot: Optional[SensorSnapshot],
) -> Dict[str, float]:
    """
    Return a copy of ``signals`` with bounded nudges from ``snapshot``.

    If ``snapshot`` is None or empty, returns ``signals`` unchanged (same object).
    """

    if snapshot is None or snapshot.is_empty():
        return signals

    out = dict(signals)

    if snapshot.battery_level is not None and snapshot.battery_level < 0.05:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.15)
        out["calm"] = _clamp01(out.get("calm", 0.5) - 0.12)

    if snapshot.place_trust is not None and snapshot.place_trust < 0.35:
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.1)
        out["hostility"] = _clamp01(out.get("hostility", 0.0) + 0.08)

    if snapshot.accelerometer_jerk is not None and snapshot.accelerometer_jerk > 0.6:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.2)
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.1)

    if snapshot.ambient_noise is not None and snapshot.ambient_noise > 0.75:
        out["calm"] = _clamp01(out.get("calm", 0.5) - 0.08)

    if snapshot.silence is not None and snapshot.silence > 0.9:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.05)

    if snapshot.biometric_anomaly is not None and snapshot.biometric_anomaly > 0.5:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.12)
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + 0.1)

    if snapshot.backup_just_completed:
        out["calm"] = _clamp01(out.get("calm", 0.5) + 0.08)

    return out


@dataclass
class DigitalActionIntent:
    """Reserved for future ethical ticketing before side-effecting APIs."""

    action_id: str
    summary: str
    requires_owner_approval: bool = True
