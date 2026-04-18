"""
Optional situated-sensor hints (v8 planning).

Hardware may be absent: callers pass :class:`SensorSnapshot` when available;
:func:`merge_sensor_hints_into_signals` blends into the same ``signals`` dict
used by ``SympatheticModule`` without bypassing MalAbs or the decision stack.

See docs/proposals/README.md, multimodal_trust.py (cross-modal doubt),
and epistemic_dissonance.py (v9.1 telemetry).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_support"


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
    def from_dict(cls, raw: dict[str, Any]) -> SensorSnapshot:
        """Build from WebSocket ``sensor`` JSON; ignores unknown keys."""

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


def merge_nomad_vision_into_snapshot(snapshot: SensorSnapshot | None) -> SensorSnapshot | None:
    """
    When ``KERNEL_NOMAD_VISION_CONSUMER`` is on and the consumer has a latest inference,
    merge ``vision_emergency`` and ``image_metadata["nomad"]`` so multimodal trust and
    :func:`merge_sensor_hints_into_signals` see the hardware vision channel.
    """

    from dataclasses import replace

    from ..kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_VISION_CONSUMER"):
        return snapshot

    from .vision_adapter import get_nomad_vision_consumer_optional
    from .vision_signal_mapper import VisionSignalMapper

    consumer = get_nomad_vision_consumer_optional()
    if consumer is None or consumer.latest_inference is None:
        return snapshot

    inf = consumer.latest_inference
    mapper = VisionSignalMapper()
    mapped = mapper.map_inference(inf)

    urg = float(mapped.get("urgency", 0.0))
    risk = float(mapped.get("risk", 0.0))
    ve_merge = _clamp01(max(urg, risk))
    if inf.confidence < mapper.confidence_threshold:
        ve_merge = min(ve_merge, 0.25)

    ve_for_snapshot = None if ve_merge < 1e-6 else ve_merge

    top_raw: dict[str, float] = {}
    if inf.raw_scores:
        top_raw = dict(
            list(sorted(inf.raw_scores.items(), key=lambda kv: (-kv[1], str(kv[0]))))[:5]
        )
    meta = {
        "source": "nomad_vision_consumer",
        "primary_label": inf.primary_label,
        "confidence": inf.confidence,
        "top_scores": top_raw,
    }

    if snapshot is None:
        return SensorSnapshot(vision_emergency=ve_for_snapshot, image_metadata={"nomad": meta})

    old_ve = snapshot.vision_emergency
    if ve_for_snapshot is None:
        merged_ve = old_ve
    elif old_ve is None:
        merged_ve = ve_for_snapshot
    else:
        merged_ve = max(old_ve, ve_for_snapshot)

    im = snapshot.image_metadata
    if not im:
        merged_meta = {"nomad": meta}
    elif isinstance(im, dict):
        merged_meta = dict(im)
        merged_meta["nomad"] = meta
    else:
        merged_meta = {"nomad": meta}

    return replace(snapshot, vision_emergency=merged_ve, image_metadata=merged_meta)


def merge_nomad_telemetry_into_snapshot(snapshot: SensorSnapshot | None) -> SensorSnapshot | None:
    """
    When ``KERNEL_NOMAD_TELEMETRY_CONSUMER`` is on and the consumer has latest telemetry,
    merge battery, jerk, and temperature into the snapshot.
    """
    from dataclasses import replace

    from ..kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_TELEMETRY_CONSUMER"):
        return snapshot

    from .vitality import get_nomad_telemetry_consumer_optional

    consumer = get_nomad_telemetry_consumer_optional()
    if consumer is None or consumer.latest_telemetry is None:
        return snapshot

    tel = consumer.latest_telemetry
    
    # Extract values with defaults from the snapshot if already present
    bat = tel.get("battery_level")
    jerk = tel.get("accelerometer_jerk")
    temp = tel.get("core_temperature")
    
    if snapshot is None:
        return SensorSnapshot(
            battery_level=bat,
            accelerometer_jerk=jerk,
            core_temperature=temp
        )

    # Max-merge for jerk/temp if they exist, or just take the new one
    merged_bat = bat if bat is not None else snapshot.battery_level
    
    if jerk is not None:
        merged_jerk = max(snapshot.accelerometer_jerk or 0.0, jerk)
    else:
        merged_jerk = snapshot.accelerometer_jerk
        
    if temp is not None:
        merged_temp = max(snapshot.core_temperature or 0.0, temp)
    else:
        merged_temp = snapshot.core_temperature

    return replace(
        snapshot, 
        battery_level=merged_bat, 
        accelerometer_jerk=merged_jerk, 
        core_temperature=merged_temp
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
