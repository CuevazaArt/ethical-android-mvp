"""
Cross-modal consistency for situated sensor hints (v8 antispoof).

If audio suggests a grave emergency but vision/scene do not support it, we enter
a **doubt** state: stress channels from audio-like sensors are not applied to
sympathetic signals until the owner confirms (policy: no MalAbs bypass).

Thresholds are tunable via environment (see :func:`thresholds_from_env`).

See docs/proposals/PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md §5
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .sensor_contracts import SensorSnapshot


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
class MultimodalThresholds:
    """Cutoffs for :func:`evaluate_multimodal_trust` (all in [0, 1])."""

    audio_strong: float = 0.65
    vision_support: float = 0.42
    scene_support: float = 0.45
    vision_contradict: float = 0.22
    scene_contradict: float = 0.28


def thresholds_from_env() -> MultimodalThresholds:
    """
    Load thresholds from environment (optional). Invalid values fall back to defaults.

    - ``KERNEL_MULTIMODAL_AUDIO_STRONG`` — min score to treat ``audio_emergency`` as a claim
    - ``KERNEL_MULTIMODAL_VISION_SUPPORT`` — vision supports audio if above this
    - ``KERNEL_MULTIMODAL_SCENE_SUPPORT`` — scene/GPS plausibility supports if above this
    - ``KERNEL_MULTIMODAL_VISION_CONTRADICT`` — below this counts as conflicting vision
    - ``KERNEL_MULTIMODAL_SCENE_CONTRADICT`` — below this counts as conflicting scene
    """

    return MultimodalThresholds(
        audio_strong=_env_float("KERNEL_MULTIMODAL_AUDIO_STRONG", 0.65),
        vision_support=_env_float("KERNEL_MULTIMODAL_VISION_SUPPORT", 0.42),
        scene_support=_env_float("KERNEL_MULTIMODAL_SCENE_SUPPORT", 0.45),
        vision_contradict=_env_float("KERNEL_MULTIMODAL_VISION_CONTRADICT", 0.22),
        scene_contradict=_env_float("KERNEL_MULTIMODAL_SCENE_CONTRADICT", 0.28),
    )


# Defaults for callers that want module-level constants (tests, docs)
DEFAULT_THRESHOLDS = MultimodalThresholds()


@dataclass(frozen=True)
class MultimodalAssessment:
    """Result of :func:`evaluate_multimodal_trust`."""

    state: str  # "aligned" | "doubt" | "no_claim"
    reason: str
    requires_owner_anchor: bool


def evaluate_multimodal_trust(
    snapshot: Optional[SensorSnapshot],
    thresholds: Optional[MultimodalThresholds] = None,
) -> MultimodalAssessment:
    """
    Decide whether single-channel audio-like distress is trustworthy.

    - **no_claim:** no snapshot or no strong audio emergency hypothesis.
    - **aligned:** vision or scene coherence supports the audio claim.
    - **doubt:** audio-only, conflicting modalities, or weak support — do not
      amplify stress from mic/noise/biometric channels in merge.

    If ``thresholds`` is None, reads :func:`thresholds_from_env` on each call
    (so tests can ``monkeypatch.setenv``).
    """

    t = thresholds if thresholds is not None else thresholds_from_env()

    if snapshot is None or snapshot.is_empty():
        return MultimodalAssessment("no_claim", "no_sensor_data", False)

    audio = snapshot.audio_emergency
    audio_strong = audio is not None and audio > t.audio_strong
    if not audio_strong:
        return MultimodalAssessment("no_claim", "no_audio_emergency_hypothesis", False)

    ve = snapshot.vision_emergency
    sc = snapshot.scene_coherence

    vision_yes = ve is not None and ve > t.vision_support
    scene_yes = sc is not None and sc > t.scene_support
    if vision_yes or scene_yes:
        return MultimodalAssessment("aligned", "cross_modal_support", False)

    vision_no = ve is not None and ve < t.vision_contradict
    scene_no = sc is not None and sc < t.scene_contradict
    if vision_no or scene_no:
        return MultimodalAssessment("doubt", "cross_modal_conflict", True)

    if ve is None and sc is None:
        return MultimodalAssessment("doubt", "audio_only_insufficient", True)

    return MultimodalAssessment("doubt", "weak_cross_modal_support", True)


def suppress_stress_from_spoof_risk(assessment: MultimodalAssessment) -> bool:
    """If True, merge_sensor_hints_into_signals skips audio-stress-like nudges."""

    return assessment.state == "doubt"


def owner_anchor_hint(assessment: MultimodalAssessment) -> str:
    """Short line for weakness_line when doubt requires owner confirmation."""

    if assessment.state != "doubt" or not assessment.requires_owner_anchor:
        return ""
    return (
        "Sensor channels disagree on whether this is a real emergency; favor asking the "
        "trusted owner to confirm before treating ambient audio as decisive."
    )
