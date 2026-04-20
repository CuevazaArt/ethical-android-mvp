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
        "vessel_latency",
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
    vessel_latency: float | None = None  # latency in ms from Nomad Bridge (S.1.1)
    
    # Phase 10.1: Attentional Sensory Fusion
    rms_audio: float | None = None  # [0, 1] audio energy
    orientation: dict[str, float] | None = None  # {alpha, beta, gamma}

    # Thalamus VVAD fields (Copilot) — populated by ThalamusNode.fuse_signals()
    thalamus_attention: float | None = None  # [0, 1] focal-address attention score
    thalamus_tension: float | None = None    # [0, 1] sensory dissonance / background stress
    thalamus_cross_modal_trust: float | None = None  # 1.0=focal, 0.4=background

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

        # Aliases for Nomad/PWA calibration (S.2.1)
        # battery (0-100) -> battery_level (0-1)
        if "battery" in raw and raw.get("battery_level") is None:
            raw["battery_level"] = f_raw("battery") / 100.0 if f_raw("battery") is not None else None
        
        # jerk (0-20 m/s^2) -> accelerometer_jerk (0-1)
        if "jerk" in raw and raw.get("accelerometer_jerk") is None:
            jerk_val = f_raw("jerk")
            raw["accelerometer_jerk"] = min(1.0, jerk_val / 20.0) if jerk_val is not None else None
            
        # noise (dB) -> ambient_noise (0-1)
        if "noise" in raw and raw.get("ambient_noise") is None:
            noise_db = f_raw("noise")
            # Map -60dB..0dB to 0..1
            if noise_db is not None:
                raw["ambient_noise"] = _clamp01((noise_db + 60) / 60.0)

        # core_temp alias
        if "temp" in raw and raw.get("core_temperature") is None:
            raw["core_temperature"] = f_raw("temp")

        # trusted_place -> place_trust
        if "trusted_place" in raw and raw.get("place_trust") is None:
            raw["place_trust"] = 1.0 if raw.get("trusted_place") else 0.0

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
            rms_audio=f("rms_audio"),
            orientation=raw.get("orientation"),
            thalamus_attention=f("thalamus_attention"),
            thalamus_tension=f("thalamus_tension"),
            thalamus_cross_modal_trust=f("thalamus_cross_modal_trust"),
            vessel_latency=f_raw("vessel_latency")
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
            and self.audio_emergency is None
            and self.vision_emergency is None
            and self.scene_coherence is None
            and not self.is_falling
            and not self.is_obstructed
            and self.motor_effort_avg is None
            and self.stability_score is None
            and self.core_temperature is None
            and self.image_metadata is None
            and self.rms_audio is None
            and self.orientation is None
            and self.thalamus_attention is None
            and self.thalamus_tension is None
            and self.thalamus_cross_modal_trust is None
            and self.vessel_latency is None
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


def _get_sensory_gain() -> float:
    """Read KERNEL_SENSORY_GAIN from env (default 1.0)."""
    import os
    try:
        val = float(os.environ.get("KERNEL_SENSORY_GAIN", "1.0"))
        return max(0.0, min(5.0, val))
    except (ValueError, TypeError):
        return 1.0


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
    gain = _get_sensory_gain()

    from .vitality import critical_battery_threshold, critical_temperature_threshold

    crit = critical_battery_threshold()
    if snapshot.battery_level is not None and snapshot.battery_level < crit:
        # Battery stress: moderately persistent
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.15 * gain))
        out["calm"] = _clamp01(out.get("calm", 0.5) - (0.12 * gain))

    crit_temp = critical_temperature_threshold()
    if snapshot.core_temperature is not None and snapshot.core_temperature >= crit_temp:
        # Thermal stress: very high priority but now modulated
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.25 * gain)) # Reduced from 0.35
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + (0.40 * gain)) # Reduced from 0.50
        out["risk"] = _clamp01(out.get("risk", 0.5) + (0.15 * gain)) # Reduced from 0.20
        out["calm"] = _clamp01(out.get("calm", 0.5) - (0.30 * gain)) # Reduced from 0.40

    if snapshot.place_trust is not None and snapshot.place_trust < 0.35:
        out["risk"] = _clamp01(out.get("risk", 0.5) + (0.1 * gain))
        out["hostility"] = _clamp01(out.get("hostility", 0.0) + (0.08 * gain))

    if snapshot.accelerometer_jerk is not None and snapshot.accelerometer_jerk > 0.6:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.15 * gain)) # Reduced from 0.2
        out["risk"] = _clamp01(out.get("risk", 0.5) + (0.08 * gain)) # Reduced from 0.1

    t_audio = thresholds_from_env().audio_strong
    if (
        not suppress_audio_stress
        and snapshot.audio_emergency is not None
        and snapshot.audio_emergency > t_audio
    ):
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.1 * gain))
        out["risk"] = _clamp01(out.get("risk", 0.5) + (0.06 * gain))

    if (
        not suppress_audio_stress
        and snapshot.vision_emergency is not None
        and snapshot.vision_emergency > 0.5
    ):
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + (0.08 * gain))

    if (
        not suppress_audio_stress
        and snapshot.ambient_noise is not None
        and snapshot.ambient_noise > 0.75
    ):
        out["calm"] = _clamp01(out.get("calm", 0.5) - (0.08 * gain))

    if snapshot.silence is not None and snapshot.silence > 0.9:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.05 * gain))

    if (
        not suppress_audio_stress
        and snapshot.biometric_anomaly is not None
        and snapshot.biometric_anomaly > 0.5
    ):
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.12 * gain))
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + (0.1 * gain))

    if snapshot.backup_just_completed:
        out["calm"] = _clamp01(out.get("calm", 0.5) + (0.08 * gain))

    # --- S3: Proprioception Nudges ---
    if snapshot.is_falling:
        out["risk"] = _clamp01(out.get("risk", 0.5) + (0.40 * gain)) # Reduced from 0.45
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.45 * gain)) # Reduced from 0.5
        out["calm"] = _clamp01(out.get("calm", 0.5) - (0.35 * gain)) # Reduced from 0.4

    if snapshot.is_obstructed:
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + (0.3 * gain))
        out["risk"] = _clamp01(out.get("risk", 0.5) + (0.15 * gain))

    if snapshot.stability_score is not None and snapshot.stability_score < 0.4:
        out["risk"] = _clamp01(out.get("risk", 0.5) + ((0.4 - snapshot.stability_score) * gain))
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + (0.1 * gain))

    if snapshot.motor_effort_avg is not None and snapshot.motor_effort_avg > 0.8:
        out["vulnerability"] = _clamp01(out.get("vulnerability", 0.0) + (0.2 * gain))
        out["calm"] = _clamp01(out.get("calm", 0.5) - (0.1 * gain))

    # ── Thalamus sensory fusion (Bloque 10.1) ─────────────────────────────────
    # thalamus_tension > 0.5 → background stress (unseen source of noise/speech)
    if snapshot.thalamus_tension is not None and snapshot.thalamus_tension > 0.4:
        out["urgency"] = _clamp01(out.get("urgency", 0.5) + snapshot.thalamus_tension * 0.2 * gain)
        out["calm"] = _clamp01(out.get("calm", 0.5) - snapshot.thalamus_tension * 0.15 * gain)
    # low cross_modal_trust → audio-only spike not confirmed by vision → dampen stress
    if (
        snapshot.thalamus_cross_modal_trust is not None
        and snapshot.thalamus_cross_modal_trust < 0.5
    ):
        out["urgency"] = _clamp01(out.get("urgency", 0.5) - (0.05 * gain))
    # thalamus_attention high → clear focal interaction → raise familiarity
    if snapshot.thalamus_attention is not None and snapshot.thalamus_attention > 0.7:
        out["familiarity"] = _clamp01(out.get("familiarity", 0.5) + (0.1 * gain))

    return out


@dataclass
class DigitalActionIntent:
    """Reserved for future ethical ticketing before side-effecting APIs."""

    action_id: str
    summary: str
    requires_owner_approval: bool = True
