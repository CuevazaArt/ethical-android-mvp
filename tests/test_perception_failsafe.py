"""Fail-safe numeric prior when LLM perception coercion indicates unreliable output."""

import pytest
from src.modules.perception.perception_schema import (
    PerceptionCoercionReport,
    validate_perception_dict,
)


def test_clean_payload_no_fail_safe_prior():
    r = PerceptionCoercionReport()
    validate_perception_dict(
        {
            "risk": 0.2,
            "urgency": 0.3,
            "hostility": 0.1,
            "calm": 0.6,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "ok",
        },
        report=r,
    )
    assert r.fail_safe_prior_applied is False
    assert r.to_public_dict()["fail_safe_prior_applied"] is False


def test_non_dict_payload_applies_fail_safe_prior(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_FAILSAFE", "1")
    monkeypatch.setenv("KERNEL_PERCEPTION_FAILSAFE_BLEND", "0.42")
    r = PerceptionCoercionReport()
    out = validate_perception_dict(["not", "a", "dict"], report=r)
    assert r.fail_safe_prior_applied is True
    assert out["risk"] > 0.5
    assert out["calm"] < 0.5


def test_fail_safe_disabled_restores_neutral_blend(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_FAILSAFE", "0")
    r = PerceptionCoercionReport()
    out = validate_perception_dict(["not", "a", "dict"], report=r)
    assert r.fail_safe_prior_applied is False
    assert out["risk"] == 0.5
