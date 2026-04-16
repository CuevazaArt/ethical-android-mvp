"""
Perception confidence envelope (advisory).

Aggregates distrust signals from coercion diagnostics, multimodal mismatch,
epistemic dissonance, and vitality constraints into a compact confidence score.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .perception_schema import perception_report_from_dict

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_support"


@dataclass(frozen=True)
class PerceptionConfidenceEnvelope:
    """Unified confidence posture for one perception turn."""

    score: float
    band: str
    uncertainty: float
    reasons: list[str]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 4),
            "band": self.band,
            "uncertainty": round(self.uncertainty, 4),
            "reasons": list(self.reasons),
            "note": "advisory_perception_confidence_no_policy_change",
        }


def build_perception_confidence_envelope(
    *,
    coercion_report: dict[str, Any] | None,
    multimodal_state: str | None,
    epistemic_active: bool,
    vitality_critical: bool,
    thermal_critical: bool = False,
) -> PerceptionConfidenceEnvelope:
    """
    Build confidence envelope in [0, 1] where higher is better confidence.

    Base score derives from coercion uncertainty, then applies bounded penalties
    for cross-modal mismatch and runtime risk overlays.
    """
    report = perception_report_from_dict(coercion_report)
    uncertainty = float(report.uncertainty())
    score = max(0.0, min(1.0, 1.0 - uncertainty))
    reasons: list[str] = []

    if report.cross_check_discrepancy:
        reasons.append("cross_check_discrepancy")
    if report.perception_dual_high_discrepancy:
        reasons.append("dual_vote_high_discrepancy")
    if report.backend_degraded:
        reasons.append("backend_degraded")
    if multimodal_state == "doubt":
        score -= 0.12
        reasons.append("multimodal_mismatch")
    if epistemic_active:
        score -= 0.1
        reasons.append("epistemic_dissonance_active")
    if vitality_critical:
        score -= 0.06
        reasons.append("vitality_critical")
    if thermal_critical:
        score -= 0.15
        reasons.append("thermal_critical")

    score = max(0.0, min(1.0, score))
    if score >= 0.72:
        band = "high"
    elif score >= 0.46:
        band = "medium"
    elif score >= 0.26:
        band = "low"
    else:
        band = "very_low"
    return PerceptionConfidenceEnvelope(
        score=score,
        band=band,
        uncertainty=uncertainty,
        reasons=reasons,
    )
