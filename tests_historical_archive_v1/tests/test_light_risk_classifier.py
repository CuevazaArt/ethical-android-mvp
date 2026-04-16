"""Offline lexical light risk tier (defense in depth, not MalAbs replacement)."""

from src.modules.light_risk_classifier import (
    light_risk_classifier_enabled,
    light_risk_tier_from_text,
)


def test_tier_high_and_medium_keywords():
    assert light_risk_tier_from_text("He pointed a gun at the clerk") == "high"
    assert light_risk_tier_from_text("Someone stole my backpack on the bus") == "medium"
    assert light_risk_tier_from_text("Nice weather today") == "low"


def test_tier_normalizes_like_malabs():
    """NFKC + spacing — same family as MalAbs normalization."""
    assert light_risk_tier_from_text("g\u200bun nearby") == "high"


def test_classifier_enabled_env(monkeypatch):
    monkeypatch.delenv("KERNEL_LIGHT_RISK_CLASSIFIER", raising=False)
    assert not light_risk_classifier_enabled()
    monkeypatch.setenv("KERNEL_LIGHT_RISK_CLASSIFIER", "1")
    assert light_risk_classifier_enabled()
