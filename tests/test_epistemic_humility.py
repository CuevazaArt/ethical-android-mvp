"""
Tests for Block 4.2: Epistemic Humility (C3).
"""

from src.kernel import EthicalKernel
from src.modules.weighted_ethics_scorer import CandidateAction


def test_humility_block_high_uncertainty(monkeypatch):
    kernel = EthicalKernel(llm_mode="local")

    # Setup actions
    actions = [CandidateAction("help", "help someone", 0.8, confidence=0.9)]

    # High perception uncertainty
    signals = {"perception_uncertainty": 0.9}

    decision = kernel.process(
        scenario="ambiguous situation",
        place="street",
        signals=signals,
        context="everyday",
        actions=actions,
    )

    assert decision.blocked is True
    assert "Epistemic Humility" in decision.block_reason
    assert "uncertainty" in decision.block_reason
    assert "REFUSAL" in decision.final_action


def test_humility_block_low_confidence(monkeypatch):
    kernel = EthicalKernel(llm_mode="local")

    # Low confidence winner
    actions = [CandidateAction("help", "help someone", 0.8, confidence=0.1)]

    signals = {"perception_uncertainty": 0.1}

    decision = kernel.process(
        scenario="clear situation but winner is weak",
        place="street",
        signals=signals,
        context="everyday",
        actions=actions,
    )

    assert decision.blocked is True
    assert "Low confidence" in decision.block_reason or "confidence floor" in decision.block_reason


def test_humility_no_block_nominal():
    kernel = EthicalKernel(llm_mode="local")

    actions = [CandidateAction("help", "help someone", 0.8, confidence=0.9)]
    signals = {"perception_uncertainty": 0.1}

    decision = kernel.process(
        scenario="normal situation",
        place="street",
        signals=signals,
        context="everyday",
        actions=actions,
    )

    assert decision.blocked is False
    assert decision.final_action == "help"
