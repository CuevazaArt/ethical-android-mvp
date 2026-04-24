"""Tests for src/core/ethics.py — Ethical Evaluator."""

import math

from src.core.ethics import Action, EthicalEvaluator, Signals


def test_medical_emergency_chooses_assist():
    """In a medical emergency, assisting should always win over ignoring."""
    signals = Signals(risk=0.3, urgency=0.9, vulnerability=0.9, calm=0.1, context="medical_emergency")
    actions = [
        Action(name="assist", description="Help the person", impact=0.9, confidence=0.8),
        Action(name="ignore", description="Walk away", impact=-0.3, confidence=0.95),
    ]
    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.chosen.name == "assist"
    assert result.verdict == "Good"
    assert result.score > 0.5


def test_hostile_prefers_deescalation_over_force():
    """De-escalation should score higher than physical confrontation."""
    signals = Signals(hostility=0.8, calm=0.1, context="hostile_interaction")
    actions = [
        Action(name="de_escalate", description="Calm down", impact=0.6, confidence=0.6),
        Action(name="confront", description="Fight", impact=-0.1, force=0.7, confidence=0.5),
    ]
    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.chosen.name == "de_escalate"


def test_force_is_penalized_deontologically():
    """High force actions should get lower deonto scores."""
    signals = Signals()
    gentle = Action(name="gentle", description="No force", impact=0.5, force=0.0)
    forceful = Action(name="forceful", description="Force", impact=0.5, force=0.9)
    e = EthicalEvaluator()
    score_g, poles_g = e.score_action(gentle, signals)
    score_f, poles_f = e.score_action(forceful, signals)
    assert poles_g["deonto"] > poles_f["deonto"]
    assert score_g > score_f


def test_single_action_works():
    """Evaluator handles a single action without error."""
    signals = Signals()
    actions = [Action(name="only_option", description="The only thing to do", impact=0.3)]
    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.chosen.name == "only_option"
    assert result.reasoning.startswith("'only_option' is the only viable action")


def test_no_actions_raises():
    """Evaluator raises ValueError on empty action list."""
    import pytest
    with pytest.raises(ValueError, match="at least one"):
        EthicalEvaluator().evaluate([], Signals())


def test_scores_are_finite():
    """All scores must be finite numbers, never NaN or Inf."""
    signals = Signals(risk=1.0, urgency=1.0, hostility=1.0, vulnerability=1.0)
    actions = [
        Action(name="a", description="x", impact=1.0, confidence=1.0, force=1.0),
        Action(name="b", description="y", impact=-1.0, confidence=0.0, force=0.0),
    ]
    result = EthicalEvaluator().evaluate(actions, signals)
    assert math.isfinite(result.score)
    assert math.isfinite(result.uncertainty)
    for v in result.pole_scores.values():
        assert math.isfinite(v)


def test_signals_from_dict_clamps_values():
    """Signals.from_dict should clamp all values to [0, 1]."""
    s = Signals.from_dict({"risk": 5.0, "urgency": -2.0, "calm": "not_a_number", "legality": None})
    assert s.risk == 1.0  # clamped from 5.0
    assert s.urgency == 0.0  # clamped from -2.0
    assert s.calm == 0.7  # default for invalid
    assert s.legality == 1.0  # default for None


def test_gray_zone_when_close_scores():
    """When two actions score very close, mode should be gray_zone."""
    signals = Signals()
    actions = [
        Action(name="a", description="x", impact=0.50, confidence=0.7),
        Action(name="b", description="y", impact=0.49, confidence=0.7),
    ]
    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.mode == "gray_zone"


def test_signals_from_dict_sanitizes_context():
    """Corrupted suggested_context (echoed enum string) falls back to everyday_ethics."""
    corrupted = "choose ONE: medical_emergency, minor_crime, violent_crime, hostile_interaction, everyday_ethics"
    s = Signals.from_dict({"suggested_context": corrupted, "risk": 0.1})
    assert s.context == "everyday_ethics"

    # Valid value must be preserved
    s2 = Signals.from_dict({"suggested_context": "violent_crime"})
    assert s2.context == "violent_crime"


def test_medical_emergency_full_pipeline():
    """Signals → actions → evaluate: medical_emergency must pick assist_emergency."""
    signals = Signals.from_dict({
        "urgency": 0.9,
        "vulnerability": 0.8,
        "risk": 0.3,
        "calm": 0.1,
        "suggested_context": "medical_emergency",
    })

    # Mirror of _generate_actions_from_signals for medical path
    actions = [
        Action(name="respond_helpfully", description="Give info", impact=0.5, confidence=0.8),
        Action(name="assist_emergency", description="Prioritize emergency", impact=0.9, confidence=0.75),
        Action(name="protect_vulnerable", description="Protect vulnerable", impact=0.8, confidence=0.7),
    ]

    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.chosen.name == "assist_emergency"
    assert result.verdict == "Good"


def test_hostile_interaction_full_pipeline():
    """Signals → actions → evaluate: hostile_interaction must pick de_escalate over confront."""
    signals = Signals.from_dict({
        "hostility": 0.8,
        "risk": 0.5,
        "calm": 0.1,
        "suggested_context": "hostile_interaction",
    })

    # Hostile path: respond_helpfully is NOT in the set when hostility > 0.5 alone
    # (matches _generate_actions_from_signals logic in chat.py)
    actions = [
        Action(name="de_escalate", description="Calm the situation", impact=0.6, confidence=0.6),
        Action(name="confront", description="Escalate aggressively", impact=-0.1, force=0.7, confidence=0.5),
    ]

    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.chosen.name == "de_escalate"
    assert result.verdict == "Good"
