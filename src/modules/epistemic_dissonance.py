"""
Epistemic sensor dissonance (v9.1) — optional “reality check” telemetry.

When audio strongly suggests an emergency but motion is near rest and vision
does not support the claim, we flag **epistemic dissonance** for tone and JSON.
This does **not** bypass MalAbs or the decision stack; it refines transparency.

See docs/discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md (pillar 1).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .sensor_contracts import SensorSnapshot

if TYPE_CHECKING:
    from .multimodal_trust import MultimodalAssessment


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return _clamp01(float(raw))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class EpistemicDissonanceAssessment:
    """Result of :func:`assess_epistemic_dissonance`."""

    active: bool
    score: float  # in [0, 1]; meaningful when active
    reason: str
    communication_hint: str = ""

    def to_public_dict(self) -> dict:
        return {
            "active": self.active,
            "score": round(self.score, 4),
            "reason": self.reason,
        }


def assess_epistemic_dissonance(
    snapshot: Optional[SensorSnapshot],
    multimodal: Optional["MultimodalAssessment"] = None,
) -> EpistemicDissonanceAssessment:
    """
    Detect cross-modal inconsistency: strong audio distress vs. low motion and
    weak/absent visual support.

    ``multimodal`` is optional context; if it already indicates strong
    cross-modal *alignment*, we skip dissonance to avoid duplicate alarms.
    """

    if snapshot is None or snapshot.is_empty():
        return EpistemicDissonanceAssessment(False, 0.0, "no_sensor_data", "")

    if multimodal is not None and multimodal.state == "aligned":
        return EpistemicDissonanceAssessment(False, 0.0, "multimodal_aligned", "")

    audio_min = _env_float("KERNEL_EPISTEMIC_AUDIO_MIN", 0.55)
    motion_max = _env_float("KERNEL_EPISTEMIC_MOTION_MAX", 0.22)
    vision_low = _env_float("KERNEL_EPISTEMIC_VISION_LOW", 0.38)

    a = snapshot.audio_emergency
    j = snapshot.accelerometer_jerk
    v = snapshot.vision_emergency

    if a is None or a < audio_min:
        return EpistemicDissonanceAssessment(False, 0.0, "no_strong_audio_claim", "")

    if j is None:
        return EpistemicDissonanceAssessment(False, 0.0, "accelerometer_unavailable", "")

    if j > motion_max:
        return EpistemicDissonanceAssessment(False, 0.0, "motion_consistent_with_alarm", "")

    if v is not None and v >= vision_low:
        return EpistemicDissonanceAssessment(False, 0.0, "vision_supports_emergency", "")

    # Audio claims distress; device motion is low; vision absent or weak
    v_part = 0.0 if v is None else float(v)
    score = _clamp01(
        0.45 * a + 0.35 * (1.0 - j) + 0.2 * max(0.0, vision_low - v_part)
    )
    hint = (
        "Sensor cues may be inconsistent: strong audio distress signals but low motion "
        "and weak visual support—treat urgency as unverified; favor calm verification "
        "and safety resources where appropriate."
    )
    return EpistemicDissonanceAssessment(
        True,
        score,
        "audio_high_motion_low_vision_weak",
        hint,
    )
