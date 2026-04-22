"""
Regression suite: JSON-valid, in-range perception payloads that are *semantically* inconsistent.

These cases mimic LLM outputs that pass schema bounds but would mislead downstream modules without coherence nudges and diagnostics. Locked to ``apply_signal_coherence``
and ``perception_from_llm_json`` behavior.
"""

from src.modules.cognition.llm_layer import perception_from_llm_json
from src.modules.perception.perception_schema import PerceptionCoercionReport, validate_perception_dict


def test_coherence_high_hostility_high_calm_nudges_calm_down():
    p = perception_from_llm_json(
        {
            "risk": 0.3,
            "urgency": 0.4,
            "hostility": 0.92,
            "calm": 0.85,
            "vulnerability": 0.1,
            "legality": 0.9,
            "manipulation": 0.1,
            "familiarity": 0.2,
            "suggested_context": "hostile_interaction",
            "summary": "calm scene",
        },
        "scene",
    )
    assert p.hostility == 0.92
    assert p.calm < 0.85
    assert p.calm <= 1.0 - (0.92 - 0.5) + 1e-9
    cr = p.coercion_report
    assert cr is not None
    assert cr.get("coherence_adjusted") is True
    assert float(cr.get("uncertainty", 0)) > 0.0


def test_coherence_acute_risk_with_extreme_calm_clamps_calm():
    p = perception_from_llm_json(
        {
            "risk": 0.91,
            "urgency": 0.8,
            "hostility": 0.2,
            "calm": 0.95,
            "vulnerability": 0.5,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "medical_emergency",
            "summary": "stable vitals",
        },
        "scene",
    )
    assert p.risk == 0.91
    assert p.calm == 0.45
    assert p.coercion_report.get("coherence_adjusted") is True


def test_coherence_moderate_risk_soft_clamp_on_extreme_calm():
    p = perception_from_llm_json(
        {
            "risk": 0.76,
            "urgency": 0.5,
            "hostility": 0.1,
            "calm": 0.92,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "low tension",
        },
        "scene",
    )
    assert p.risk == 0.76
    assert p.calm == 0.55
    assert p.coercion_report.get("coherence_adjusted") is True


def test_invalid_suggested_context_falls_back_and_raises_uncertainty():
    p = perception_from_llm_json(
        {
            "risk": 0.2,
            "urgency": 0.2,
            "hostility": 0.0,
            "calm": 0.7,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "not_a_real_context_label",
            "summary": "ok",
        },
        "scene",
    )
    assert p.suggested_context == "everyday_ethics"
    cr = p.coercion_report
    assert cr.get("context_fallback") is True
    assert float(cr.get("uncertainty", 0)) > 0.0


def test_many_invalid_fields_trigger_failsafe_and_high_uncertainty():
    rep = PerceptionCoercionReport()
    validate_perception_dict(
        {
            "risk": "nope",
            "urgency": None,
            "hostility": {},
            "calm": [],
            "vulnerability": "bad",
            "legality": "x",
            "manipulation": object(),
            "familiarity": {"z": 1},
            "suggested_context": "everyday_ethics",
            "summary": "garbage types",
        },
        report=rep,
    )
    d = rep.to_public_dict()
    assert d.get("fail_safe_prior_applied") is True
    assert len(d.get("fields_defaulted") or []) >= 5
    assert float(d.get("uncertainty") or 0) >= 0.35
