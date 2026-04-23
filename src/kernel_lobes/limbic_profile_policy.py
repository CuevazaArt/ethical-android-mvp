"""
Limbic perception profile (pure policy extracted from :class:`~src.kernel.EthicalKernel`).

Module 0 / Block 0.1.3 — single implementation for advisory plan-bias + arousal labeling so chat
and offline buffer paths stay aligned (ADR 0018).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypedDict

from ..modules.epistemic_dissonance import EpistemicDissonanceAssessment
from ..modules.llm_layer import LLMPerception
from ..modules.multimodal_trust import MultimodalAssessment
from ..modules.perception_confidence import PerceptionConfidenceEnvelope
from ..modules.vitality import VitalityAssessment
from .signal_coercion import safe_signal_scalar

_PlanningBias = Literal[
    "short_horizon_containment",
    "balanced",
    "long_horizon_deliberation",
    "resource_preservation",
    "verification_first",
]
_ArousalBand = Literal["low", "medium", "high"]


class LimbicPerceptionProfile(TypedDict):
    """
    Advisory limbic snapshot injected into chat/offline routing (no policy bypass).

    Keys are stable for tests and :class:`~src.kernel.EthicalKernel` serialization paths.
    """

    arousal_band: _ArousalBand
    threat_load: float
    regulation_gap: float
    planning_bias: _PlanningBias
    multimodal_mismatch: bool
    vitality_critical: bool
    context: str
    confidence_band: str


def build_limbic_perception_profile(
    *,
    perception: LLMPerception | None,
    signals: Mapping[str, Any] | None,
    vitality: VitalityAssessment | None,
    multimodal: MultimodalAssessment | None,
    epistemic: EpistemicDissonanceAssessment | None,
    confidence_envelope: PerceptionConfidenceEnvelope | None = None,
) -> LimbicPerceptionProfile:
    """
    Compact limbic profile derived from perception-adjacent channels.

    Advisory and local-only; does not bypass policy gates. Signal dict values are coerced
    defensively so corrupt or non-numeric payloads cannot abort the chat path.

    Returns
    -------
    LimbicPerceptionProfile
        Keys: ``arousal_band``, ``threat_load``, ``regulation_gap``, ``planning_bias``,
        ``multimodal_mismatch``, ``vitality_critical``, ``context``, ``confidence_band``.
    """
    sig: Mapping[str, Any] = signals or {}
    risk = safe_signal_scalar(sig.get("risk", 0.0))
    urgency = safe_signal_scalar(sig.get("urgency", 0.0))
    hostility = safe_signal_scalar(sig.get("hostility", 0.0))
    calm = safe_signal_scalar(sig.get("calm", 0.0))
    threat_load = max(risk, urgency, hostility)
    regulation_gap = max(0.0, threat_load - calm)
    if threat_load >= 0.75:
        arousal_band = "high"
    elif threat_load >= 0.45:
        arousal_band = "medium"
    else:
        arousal_band = "low"
    planning_bias = (
        "short_horizon_containment"
        if arousal_band == "high"
        else ("balanced" if arousal_band == "medium" else "long_horizon_deliberation")
    )
    if vitality is not None and bool(vitality.is_critical):
        planning_bias = "resource_preservation"
    mismatch = multimodal is not None and getattr(multimodal, "state", "") == "doubt"
    if mismatch:
        planning_bias = "verification_first"
    if epistemic is not None and bool(epistemic.active):
        planning_bias = "verification_first"
    confidence_band = confidence_envelope.band if confidence_envelope is not None else "unknown"
    if confidence_band in ("low", "very_low"):
        planning_bias = "verification_first"
    out: LimbicPerceptionProfile = {
        "arousal_band": arousal_band,
        "threat_load": round(threat_load, 4),
        "regulation_gap": round(regulation_gap, 4),
        "planning_bias": planning_bias,
        "multimodal_mismatch": bool(mismatch),
        "vitality_critical": bool(vitality.is_critical) if vitality is not None else False,
        "context": (getattr(perception, "suggested_context", "") or "everyday"),
        "confidence_band": confidence_band,
    }
    return out
