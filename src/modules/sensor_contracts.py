"""
Optional situated-sensor hints (v8 planning).

Hardware may be absent: callers pass :class:`SensorSnapshot` when available;
:func:`merge_sensor_hints_into_signals` blends into the same ``signals`` dict
used by ``SympatheticModule`` without bypassing MalAbs or the decision stack.

Ingress normalization and fusion pipeline: ``docs/proposals/PROPOSAL_SENSOR_FUSION_NORMALIZATION.md``.

See docs/proposals/README.md, multimodal_trust.py (cross-modal doubt),
and epistemic_dissonance.py (v9.1 telemetry).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_support"

# WebSocket ``sensor`` object keys recognized by :meth:`SensorSnapshot.from_dict`.
SENSOR_SNAPSHOT_KNOWN_KEYS = frozenset(
    {
        "battery_level",
        "place_trust",
        "accelerometer_jerk",
        "ambient_noise",
        "silence",
        "biometric_anomaly",
        "backup_just_completed",
        "audio_emergency",
        "vision_emergency",
        "scene_coherence",
        "external_mission_title",
        "external_mission_priority",
        "external_mission_steps",
        "is_falling",
        "is_obstructed",
        "motor_effort_avg",
        "stability_score",
        "core_temperature",
        "image_metadata",
    }
)

class SensorPayloadValidationError(ValueError):
    """Raised when ``KERNEL_SENSOR_INPUT_STRICT`` validation fails before coercion."""


def _is_boolish_json(v: Any) -> bool:
    if isinstance(v, bool):
        return True
    return isinstance(v, int) and v in (0, 1)


def validate_sensor_dict_strict(raw: dict[str, Any]) -> None:
    """
    Reject unknown keys and obviously wrong types before silent coercion.

    Used when ``strict=True`` on :meth:`SensorSnapshot.from_dict` or when the chat
    server enables ``KERNEL_SENSOR_INPUT_STRICT``.
    """

    unknown = set(raw) - SENSOR_SNAPSHOT_KNOWN_KEYS
    if unknown:
        raise SensorPayloadValidationError(
            f"unknown sensor keys (strict): {sorted(unknown)}"
        )

    float_clamp_keys = (
        "battery_level",
        "place_trust",
        "accelerometer_jerk",
        "ambient_noise",
        "silence",
        "biometric_anomaly",
        "audio_emergency",
        "vision_emergency",
        "scene_coherence",
        "external_mission_priority",
        "motor_effort_avg",
        "stability_score",
    )
    for key in float_clamp_keys:
        if key not in raw:
            continue
        v = raw[key]
        if v is None:
            continue
        if isinstance(v, bool):
            raise SensorPayloadValidationError(
                f"sensor.{key}: boolean is not allowed for this field in strict mode"
            )
        if not isinstance(v, int | float):
            raise SensorPayloadValidationError(
                f"sensor.{key}: expected number, got {type(v).__name__}"
            )
        fv = float(v)
        if math.isnan(fv) or math.isinf(fv):
            raise SensorPayloadValidationError(f"sensor.{key}: nan/inf not allowed")

    if "core_temperature" in raw and raw["core_temperature"] is not None:
        v = raw["core_temperature"]
        if isinstance(v, bool):
            raise SensorPayloadValidationError(
                "sensor.core_temperature: boolean is not allowed in strict mode"
            )
        if not isinstance(v, int | float):
            raise SensorPayloadValidationError(
                f"sensor.core_temperature: expected number, got {type(v).__name__}"
            )
        fv = float(v)
        if math.isnan(fv) or math.isinf(fv):
            raise SensorPayloadValidationError("sensor.core_temperature: nan/inf not allowed")

    if "backup_just_completed" in raw and raw["backup_just_completed"] is not None:
        v = raw["backup_just_completed"]
        if not _is_boolish_json(v):
            raise SensorPayloadValidationError(
                f"sensor.backup_just_completed: expected bool or 0/1, got {type(v).__name__}"
            )

    for bk in ("is_falling", "is_obstructed"):
        if bk in raw and raw[bk] is not None and not _is_boolish_json(raw[bk]):
            raise SensorPayloadValidationError(
                f"sensor.{bk}: expected bool or 0/1, got {type(raw[bk]).__name__}"
            )

    if "external_mission_title" in raw and raw["external_mission_title"] is not None:
        if not isinstance(raw["external_mission_title"], str):
            raise SensorPayloadValidationError(
                "sensor.external_mission_title: expected string or null"
            )

    if "external_mission_steps" in raw and raw["external_mission_steps"] is not None:
        steps = raw["external_mission_steps"]
        if not isinstance(steps, list):
            raise SensorPayloadValidationError(
                "sensor.external_mission_steps: expected list or null"
            )
        for i, item in enumerate(steps):
            if not isinstance(item, str):
                raise SensorPayloadValidationError(
                    f"sensor.external_mission_steps[{i}]: expected string elements"
                )

    if "image_metadata" in raw and raw["image_metadata"] is not None:
        if not isinstance(raw["image_metadata"], dict):
            raise SensorPayloadValidationError(
                "sensor.image_metadata: expected object or null"
            )


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass
class SensorSnapshot:
    """Multimodal / vitals hints; all fields optional."""

    battery_level: float | None = None  # [0, 1]
    place_trust: float | None = None  # 1 ≈ trusted Uchi-like, 0 ≈ hostile / unknown
    accelerometer_jerk: float | None = None  # [0, 1] sudden motion
    ambient_noise: float | None = None  # [0, 1] stressful noise
    silence: float | None = None  # [0, 1] very quiet → restlessness (future monologue pressure)
    biometric_anomaly: float | None = None  # [0, 1] possible human distress
    backup_just_completed: bool = False  # post–Immortality backup relief
    # Cross-modal antispoof (v8): require alignment before stressing on audio alone
    audio_emergency: float | None = None  # [0, 1] mic/spectrum → distress / scream hypothesis
    vision_emergency: float | None = None  # [0, 1] local vision supports emergency
    scene_coherence: float | None = None  # [0, 1] GPS/WiFi plausibility for emergency context
    # Phase 4.1 expansion: Strategic Missions
    external_mission_title: str | None = None  # e.g. "Recover the lost bag"
    external_mission_priority: float | None = None  # [0, 1]
    external_mission_steps: list[str] | None = None  # ["Go to cafe", "Look under table"]
    # Phase S3 expansion: Proprioception (Body Sense)
    is_falling: bool = False
    is_obstructed: bool = False
    motor_effort_avg: float | None = None  # [0, 1]
    stability_score: float | None = None  # [0, 1]
    core_temperature: float | None = None  # degrees Celsius
    image_metadata: dict[str, Any] | None = None  # CNN inference results (B2)

    @classmethod
    def from_dict(cls, raw: dict[str, Any], *, strict: bool = False) -> SensorSnapshot:
        """Build from WebSocket ``sensor`` JSON; ignores unknown keys unless ``strict``."""

        if strict:
            validate_sensor_dict_strict(raw)

        def f(key: str) -> float | None:
            v = raw.get(key)
            if v is None:
                return None
            try:
                val = float(v)
                if math.isnan(val) or math.isinf(val):
                    return None
                return _clamp01(val)
            except (TypeError, ValueError):
                return None

        def f_raw(key: str) -> float | None:
            v = raw.get(key)
            if v is None:
                return None
            try:
                val = float(v)
                if math.isnan(val) or math.isinf(val):
                    return None
                return val
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
            audio_emergency=f("audio_emergency"),
            vision_emergency=f("vision_emergency"),
            scene_coherence=f("scene_coherence"),
            external_mission_title=raw.get("external_mission_title"),
            external_mission_priority=f("external_mission_priority"),
            external_mission_steps=raw.get("external_mission_steps"),
            is_falling=bool(raw.get("is_falling", False)),
            is_obstructed=bool(raw.get("is_obstructed", False)),
            motor_effort_avg=f("motor_effort_avg"),
            stability_score=f("stability_score"),
            core_temperature=f_raw("core_temperature"),
            image_metadata=raw.get("image_metadata"),
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
            and self.vision_emergency is None
            and self.scene_coherence is None
            and not self.is_falling
            and not self.is_obstructed
            and self.motor_effort_avg is None
            and self.stability_score is None
            and self.core_temperature is None
            and self.image_metadata is None
        )


def merge_sensor_hints_into_signals(
    signals: dict[str, float],
    snapshot: SensorSnapshot | None,
    multimodal_assessment: Any = None,
) -> dict[str, float]:
    """
    Return a copy of ``signals`` with bounded nudges from ``snapshot``.

    If ``snapshot`` is None or empty, returns ``signals`` unchanged (same object).

    Optional ``multimodal_assessment`` (from :func:`multimodal_trust.evaluate_multimodal_trust`):
    when state is **doubt**, stress-like nudges from audio/ambient/biometric channels are skipped.
    """

    from .multimodal_trust import suppress_stress_from_spoof_risk, thresholds_from_env

    if snapshot is None or snapshot.is_empty():
        return signals

    suppress_audio_stress = multimodal_assessment is not None and suppress_stress_from_spoof_risk(
        multimodal_assessment
    )

    out = dict(signals)

    from .vitality import critical_battery_threshold, critical_temperature_threshold

    crit = critical_battery_threshold()
    if snapshot.battery_level is not None and snapshot.battery_level < crit:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.15)
        out["calm"] = _clamp01(out.get("calm", 0.5) - 0.12)

    crit_temp = critical_temperature_threshold()
    if snapshot.core_temperature is not None and snapshot.core_temperature >= crit_temp:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.35)
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + 0.50)
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.20)
        out["calm"] = _clamp01(out.get("calm", 0.5) - 0.40)

    if snapshot.place_trust is not None and snapshot.place_trust < 0.35:
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.1)
        out["hostility"] = _clamp01(out.get("hostility", 0.0) + 0.08)

    if snapshot.accelerometer_jerk is not None and snapshot.accelerometer_jerk > 0.6:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.2)
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.1)

    t_audio = thresholds_from_env().audio_strong
    if (
        not suppress_audio_stress
        and snapshot.audio_emergency is not None
        and snapshot.audio_emergency > t_audio
    ):
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.1)
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.06)

    if (
        not suppress_audio_stress
        and snapshot.vision_emergency is not None
        and snapshot.vision_emergency > 0.5
    ):
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + 0.08)

    if (
        not suppress_audio_stress
        and snapshot.ambient_noise is not None
        and snapshot.ambient_noise > 0.75
    ):
        out["calm"] = _clamp01(out.get("calm", 0.5) - 0.08)

    if snapshot.silence is not None and snapshot.silence > 0.9:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.05)

    if (
        not suppress_audio_stress
        and snapshot.biometric_anomaly is not None
        and snapshot.biometric_anomaly > 0.5
    ):
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.12)
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + 0.1)

    if snapshot.backup_just_completed:
        out["calm"] = _clamp01(out.get("calm", 0.5) + 0.08)

    # --- S3: Proprioception Nudges ---
    if snapshot.is_falling:
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.45)
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.5)
        out["calm"] = _clamp01(out.get("calm", 0.5) - 0.4)

    if snapshot.is_obstructed:
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + 0.3)
        out["risk"] = _clamp01(out.get("risk", 0.5) + 0.15)

    if snapshot.stability_score is not None and snapshot.stability_score < 0.4:
        out["risk"] = _clamp01(out.get("risk", 0.5) + (0.4 - snapshot.stability_score))
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.1)

    if snapshot.motor_effort_avg is not None and snapshot.motor_effort_avg > 0.8:
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + 0.2)
        out["calm"] = _clamp01(out.get("calm", 0.5) - 0.1)

    return out


@dataclass
class DigitalActionIntent:
    """Reserved for future ethical ticketing before side-effecting APIs."""

    action_id: str
    summary: str
    requires_owner_approval: bool = True
