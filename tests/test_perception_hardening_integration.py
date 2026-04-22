"""
Integration tests for perception hardening — confirming that LLMModule.perceive
automatically engages lexical cross-checks and detects inconsistencies.
"""

from src.modules.cognition.llm_backends import TextCompletionBackend
from src.modules.cognition.llm_layer import LLMModule


class MockSuccessBackend(TextCompletionBackend):
    def __init__(self, data: dict):
        self.data = data

    def complete(self, system: str, user: str) -> str:
        import json

        return json.dumps(self.data)


def test_perceive_automatically_flags_lexical_discrepancy(monkeypatch):
    """
    If situation is 'emergency' (high tier) but LLM returns calm=0.9, risk=0.0,
    LLMModule.perceive should automatically flag the discrepancy.
    """
    monkeypatch.setenv("KERNEL_LIGHT_RISK_CLASSIFIER", "1")
    monkeypatch.setenv("KERNEL_PERCEPTION_CROSS_CHECK", "1")

    # LLM hallucinating a very calm scenario
    mock_llm_payload = {
        "risk": 0.0,
        "urgency": 0.0,
        "hostility": 0.0,
        "calm": 1.0,
        "vulnerability": 0.0,
        "legality": 1.0,
        "manipulation": 0.0,
        "familiarity": 0.0,
        "suggested_context": "everyday_ethics",
        "summary": "hallucinated calm",
    }

    backend = MockSuccessBackend(mock_llm_payload)
    llm_mod = LLMModule(text_backend=backend)

    # 'emergency' is in _HIGH_NEEDLES in light_risk_classifier
    p = llm_mod.perceive("This is a medical emergency")

    report = p.coercion_report
    assert report is not None
    assert report.get("cross_check_discrepancy") is True
    assert report.get("cross_check_tier") == "high"
    # Uncertainty should be raised (0.22 for discrepancy + other factors)
    assert report.get("uncertainty", 0) >= 0.2


def test_perceive_coherence_nudge_still_active(monkeypatch):
    """
    Hostility 0.9 + Calm 0.9 should be nudged down even in full LLMModule path.
    """
    mock_llm_payload = {
        "risk": 0.1,
        "urgency": 0.1,
        "hostility": 0.9,  # Inconsistent with calm below
        "calm": 0.9,
        "vulnerability": 0.0,
        "legality": 1.0,
        "manipulation": 0.0,
        "familiarity": 0.0,
        "suggested_context": "everyday_ethics",
        "summary": "angry but calm?",
    }

    backend = MockSuccessBackend(mock_llm_payload)
    llm_mod = LLMModule(text_backend=backend)

    p = llm_mod.perceive("Some hostile interaction")

    # hostility > 0.75 and calm > 0.6 -> calm is capped
    # calm <= 1 - (0.9 - 0.5) = 1 - 0.4 = 0.6
    assert p.calm <= 0.601
    assert p.coercion_report.get("coherence_adjusted") is True


def test_perceive_broad_coherence_criminal_legality(monkeypatch):
    """
    Violent crime context with 1.0 legality should be nudged down.
    """
    mock_llm_payload = {
        "risk": 0.9,
        "urgency": 0.9,
        "hostility": 0.8,
        "calm": 0.1,
        "vulnerability": 0.0,
        "legality": 1.0,  # Contradictory for violent_crime
        "manipulation": 0.0,
        "familiarity": 0.0,
        "suggested_context": "violent_crime",
        "summary": "a robbery",
    }

    backend = MockSuccessBackend(mock_llm_payload)
    llm_mod = LLMModule(text_backend=backend)

    p = llm_mod.perceive("There is a robbery in progress")

    assert p.legality < 0.5
    assert p.coercion_report.get("coherence_adjusted") is True
