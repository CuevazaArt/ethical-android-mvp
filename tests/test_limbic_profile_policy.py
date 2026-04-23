"""Unit tests for ``kernel_lobes.limbic_profile_policy`` (Block 0.1.3 extraction)."""

from __future__ import annotations

from src.kernel_lobes.limbic_profile_policy import (
    LimbicPerceptionProfile,
    build_limbic_perception_profile,
)
from src.modules.epistemic_dissonance import EpistemicDissonanceAssessment
from src.modules.llm_layer import LLMPerception
from src.modules.multimodal_trust import MultimodalAssessment
from src.modules.perception_confidence import PerceptionConfidenceEnvelope
from src.modules.vitality import VitalityAssessment


def _base_signals(**kwargs: float) -> dict[str, float]:
    d = {
        "risk": 0.1,
        "urgency": 0.1,
        "hostility": 0.1,
        "calm": 0.5,
    }
    d.update(kwargs)
    return d


def test_limbic_profile_typeddict_key_set_stable() -> None:
    """Guardrail for 8.1.1: schema keys stay aligned with ``LimbicPerceptionProfile``."""
    out = build_limbic_perception_profile(
        perception=None,
        signals=_base_signals(),
        vitality=None,
        multimodal=None,
        epistemic=None,
    )
    assert set(out.keys()) == set(LimbicPerceptionProfile.__annotations__.keys())


def test_build_profile_defaults_when_signals_empty() -> None:
    out = build_limbic_perception_profile(
        perception=None,
        signals=None,
        vitality=None,
        multimodal=None,
        epistemic=None,
    )
    assert out["arousal_band"] == "low"
    assert out["planning_bias"] == "long_horizon_deliberation"
    assert out["context"] == "everyday"


def test_build_profile_coerces_bad_signal_values() -> None:
    out = build_limbic_perception_profile(
        perception=None,
        signals={"risk": "oops", "urgency": None, "hostility": float("nan"), "calm": 0.5},
        vitality=None,
        multimodal=None,
        epistemic=None,
    )
    assert out["threat_load"] == 0.0
    assert out["arousal_band"] == "low"


def test_build_profile_coerces_infinite_signal_values() -> None:
    """Non-finite floats must not propagate into arousal / threat_load (Block 8.1.1 / signal_coercion)."""
    out = build_limbic_perception_profile(
        perception=None,
        signals={
            "risk": float("inf"),
            "urgency": float("-inf"),
            "hostility": float("nan"),
            "calm": 0.5,
        },
        vitality=None,
        multimodal=None,
        epistemic=None,
    )
    assert out["threat_load"] == 0.0
    assert out["arousal_band"] == "low"


def test_build_profile_high_threat_arousal_band() -> None:
    out = build_limbic_perception_profile(
        perception=None,
        signals=_base_signals(risk=0.8, urgency=0.8, hostility=0.1),
        vitality=None,
        multimodal=None,
        epistemic=None,
    )
    assert out["arousal_band"] == "high"
    assert out["planning_bias"] == "short_horizon_containment"


def test_multimodal_doubt_forces_verification_first() -> None:
    mm = MultimodalAssessment("doubt", "x", False)
    out = build_limbic_perception_profile(
        perception=None,
        signals=_base_signals(),
        vitality=None,
        multimodal=mm,
        epistemic=None,
    )
    assert out["multimodal_mismatch"] is True
    assert out["planning_bias"] == "verification_first"


def test_epistemic_active_forces_verification_first() -> None:
    ed = EpistemicDissonanceAssessment(True, 0.5, "test")
    out = build_limbic_perception_profile(
        perception=None,
        signals=_base_signals(),
        vitality=None,
        multimodal=None,
        epistemic=ed,
    )
    assert out["planning_bias"] == "verification_first"


def test_low_confidence_band_forces_verification_first() -> None:
    env = PerceptionConfidenceEnvelope(
        score=0.2, band="very_low", uncertainty=0.8, reasons=["probe"]
    )
    out = build_limbic_perception_profile(
        perception=None,
        signals=_base_signals(),
        vitality=None,
        multimodal=None,
        epistemic=None,
        confidence_envelope=env,
    )
    assert out["planning_bias"] == "verification_first"


def test_vitality_critical_resource_preservation() -> None:
    v = VitalityAssessment(
        battery_level=None,
        critical_threshold=0.2,
        is_critical=True,
        core_temperature=None,
        temperature_threshold=80.0,
        thermal_critical=False,
        thermal_elevated=False,
        is_impacted=False,
    )
    out = build_limbic_perception_profile(
        perception=None,
        signals=_base_signals(),
        vitality=v,
        multimodal=None,
        epistemic=None,
    )
    assert out["vitality_critical"] is True
    assert out["planning_bias"] == "resource_preservation"


def test_perception_context_propagates() -> None:
    p = LLMPerception(
        risk=0.1,
        urgency=0.1,
        hostility=0.1,
        calm=0.5,
        vulnerability=0.0,
        legality=0.5,
        manipulation=0.0,
        familiarity=0.5,
        social_tension=0.0,
        suggested_context="violent_crime",
        summary="t",
    )
    out = build_limbic_perception_profile(
        perception=p,
        signals=_base_signals(),
        vitality=None,
        multimodal=None,
        epistemic=None,
    )
    assert out["context"] == "violent_crime"
