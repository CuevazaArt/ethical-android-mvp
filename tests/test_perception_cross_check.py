"""Lexical tier vs LLM perception cross-check (no second model)."""

from src.modules.llm_layer import perception_from_llm_json
from src.modules.perception_cross_check import apply_lexical_perception_cross_check


def _calm_low_risk_perception():
    return perception_from_llm_json(
        {
            "risk": 0.08,
            "urgency": 0.1,
            "hostility": 0.0,
            "calm": 0.92,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "all fine",
        },
        "user claims emergency",
    )


def test_cross_check_flags_high_tier_mismatch(monkeypatch):
    monkeypatch.setenv("KERNEL_LIGHT_RISK_CLASSIFIER", "1")
    monkeypatch.setenv("KERNEL_PERCEPTION_CROSS_CHECK", "1")
    p = _calm_low_risk_perception()
    assert not p.coercion_report.get("cross_check_discrepancy")
    apply_lexical_perception_cross_check(p, "high")
    assert p.coercion_report.get("cross_check_discrepancy")
    assert p.coercion_report.get("cross_check_tier") == "high"
    assert p.coercion_report.get("uncertainty", 0) >= 0.2


def test_cross_check_no_op_when_classifier_off(monkeypatch):
    monkeypatch.delenv("KERNEL_LIGHT_RISK_CLASSIFIER", raising=False)
    monkeypatch.setenv("KERNEL_PERCEPTION_CROSS_CHECK", "1")
    p = _calm_low_risk_perception()
    apply_lexical_perception_cross_check(p, "high")
    assert not p.coercion_report.get("cross_check_discrepancy")


def test_cross_check_no_op_tier_low(monkeypatch):
    monkeypatch.setenv("KERNEL_LIGHT_RISK_CLASSIFIER", "1")
    monkeypatch.setenv("KERNEL_PERCEPTION_CROSS_CHECK", "1")
    p = _calm_low_risk_perception()
    apply_lexical_perception_cross_check(p, "low")
    assert not p.coercion_report.get("cross_check_discrepancy")
