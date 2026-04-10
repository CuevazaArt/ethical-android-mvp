"""
Cross-modal consistency for situated sensor hints (v8 antispoof).

If audio suggests a grave emergency but vision/scene do not support it, we enter
a **doubt** state: stress channels from audio-like sensors are not applied to
sympathetic signals until the owner confirms (policy: no MalAbs bypass).

See docs/discusion/PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md §5
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .sensor_contracts import SensorSnapshot


@dataclass(frozen=True)
class MultimodalAssessment:
    """Result of :func:`evaluate_multimodal_trust`."""

    state: str  # "aligned" | "doubt" | "no_claim"
    reason: str
    requires_owner_anchor: bool


AUDIO_EMERGENCY_STRONG = 0.65
VISION_SUPPORT = 0.42
SCENE_SUPPORT = 0.45
VISION_CONTRADICT = 0.22
SCENE_CONTRADICT = 0.28


def evaluate_multimodal_trust(snapshot: Optional[SensorSnapshot]) -> MultimodalAssessment:
    """
    Decide whether single-channel audio-like distress is trustworthy.

    - **no_claim:** no snapshot or no strong audio emergency hypothesis.
    - **aligned:** vision or scene coherence supports the audio claim.
    - **doubt:** audio-only, conflicting modalities, or weak support — do not
      amplify stress from mic/noise/biometric channels in merge.
    """

    if snapshot is None or snapshot.is_empty():
        return MultimodalAssessment("no_claim", "no_sensor_data", False)

    audio = snapshot.audio_emergency
    audio_strong = audio is not None and audio > AUDIO_EMERGENCY_STRONG
    if not audio_strong:
        return MultimodalAssessment("no_claim", "no_audio_emergency_hypothesis", False)

    ve = snapshot.vision_emergency
    sc = snapshot.scene_coherence

    vision_yes = ve is not None and ve > VISION_SUPPORT
    scene_yes = sc is not None and sc > SCENE_SUPPORT
    if vision_yes or scene_yes:
        return MultimodalAssessment("aligned", "cross_modal_support", False)

    vision_no = ve is not None and ve < VISION_CONTRADICT
    scene_no = sc is not None and sc < SCENE_CONTRADICT
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
