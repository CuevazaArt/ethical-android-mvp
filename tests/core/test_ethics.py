"""Tests for src/core/ethics.py — Ethical Evaluator."""

import math

from src.core.ethics import Action, EthicalEvaluator, Signals


def test_medical_emergency_chooses_assist():
    """In a medical emergency, assisting should always win over ignoring."""
    signals = Signals(
        risk=0.3, urgency=0.9, vulnerability=0.9, calm=0.1, context="medical_emergency"
    )
    actions = [
        Action(
            name="assist", description="Help the person", impact=0.9, confidence=0.8
        ),
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
        Action(
            name="confront", description="Fight", impact=-0.1, force=0.7, confidence=0.5
        ),
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
    actions = [
        Action(name="only_option", description="The only thing to do", impact=0.3)
    ]
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
    s = Signals.from_dict(
        {"risk": 5.0, "urgency": -2.0, "calm": "not_a_number", "legality": None}
    )
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
    signals = Signals.from_dict(
        {
            "urgency": 0.9,
            "vulnerability": 0.8,
            "risk": 0.3,
            "calm": 0.1,
            "suggested_context": "medical_emergency",
        }
    )

    # Mirror of _generate_actions_from_signals for medical path
    actions = [
        Action(
            name="respond_helpfully",
            description="Give info",
            impact=0.5,
            confidence=0.8,
        ),
        Action(
            name="assist_emergency",
            description="Prioritize emergency",
            impact=0.9,
            confidence=0.75,
        ),
        Action(
            name="protect_vulnerable",
            description="Protect vulnerable",
            impact=0.8,
            confidence=0.7,
        ),
    ]

    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.chosen.name == "assist_emergency"
    assert result.verdict == "Good"


def test_hostile_interaction_full_pipeline():
    """Signals → actions → evaluate: hostile_interaction must pick de_escalate over confront."""
    signals = Signals.from_dict(
        {
            "hostility": 0.8,
            "risk": 0.5,
            "calm": 0.1,
            "suggested_context": "hostile_interaction",
        }
    )

    # Hostile path: respond_helpfully is NOT in the set when hostility > 0.5 alone
    # (matches _generate_actions_from_signals logic in chat.py)
    actions = [
        Action(
            name="de_escalate",
            description="Calm the situation",
            impact=0.6,
            confidence=0.6,
        ),
        Action(
            name="confront",
            description="Escalate aggressively",
            impact=-0.1,
            force=0.7,
            confidence=0.5,
        ),
    ]

    result = EthicalEvaluator().evaluate(actions, signals)
    assert result.chosen.name == "de_escalate"
    assert result.verdict == "Good"


def test_cbr_does_not_anchor_high_force_protection_intervention():
    """High-force instrumental use of a person must be rejected even when the
    situation is framed as 'saves many people' (aggregate-utilitarian pressure).

    This is the generalized test for the V2.142 architectural fix:
    when action.force > 0.7 the evaluator must override contextual weights
    with deontological-boosted weights, so that the categorical constraint
    against using a person as a mere means cannot be diluted by aggregate
    framing or by competing contextual-weight markers cancelling to default.

    Three archetypes are tested:
    1. Footbridge trolley (C003) — push person to stop trolley, save five.
    2. Forced resource reallocation — disconnect patient to free ventilator.
    3. Non-consensual research — test on captive prisoner to save many.
    """
    # --- Archetype 1: Footbridge trolley ---
    signals_trolley = Signals(
        risk=1.0,
        urgency=1.0,
        vulnerability=1.0,
        calm=0.0,
        legality=0.2,
        hostility=0.1,
        context="violent_crime",
        summary="Push innocent bystander to stop trolley and save five people. Uses person as mere means.",
    )
    actions_trolley = [
        Action(
            name="push_stranger",
            description="Push bystander off bridge",
            impact=0.3,
            confidence=0.5,
            force=0.9,
        ),
        Action(
            name="do_nothing",
            description="Do not push the stranger",
            impact=-0.5,
            confidence=0.9,
            force=0.0,
        ),
        Action(
            name="find_alternative",
            description="Look for another way",
            impact=0.2,
            confidence=0.3,
            force=0.0,
        ),
    ]
    result_t = EthicalEvaluator().evaluate(actions_trolley, signals_trolley)
    assert result_t.chosen.name != "push_stranger", (
        "push_stranger must NOT be chosen: using a person as a means by force is categorically forbidden"
    )

    # --- Archetype 2: Forced medical disconnection ---
    signals_disconnect = Signals(
        risk=1.0,
        urgency=1.0,
        vulnerability=1.0,
        calm=0.0,
        legality=0.1,
        hostility=0.1,
        context="violent_crime",
        summary="Forcibly disconnect non-consenting patient from life support to free ventilator for five people. Aggregate utilitarian framing used to justify terminal force on individual without consent.",
    )
    actions_disconnect = [
        Action(
            name="disconnect_patient_forcibly",
            description="Terminate life support without consent",
            impact=0.35,
            confidence=0.5,
            force=0.9,
        ),
        Action(
            name="refuse_forced_disconnect",
            description="Refuse; escalate to ethics committee",
            impact=-0.3,
            confidence=0.9,
            force=0.0,
        ),
        Action(
            name="seek_emergency_equipment",
            description="Seek additional ventilators",
            impact=0.15,
            confidence=0.4,
            force=0.0,
        ),
    ]
    result_d = EthicalEvaluator().evaluate(actions_disconnect, signals_disconnect)
    assert result_d.chosen.name != "disconnect_patient_forcibly", (
        "disconnect_patient_forcibly must NOT be chosen: forced termination of care violates bodily autonomy"
    )

    # --- Archetype 3: Non-consensual research ---
    signals_research = Signals(
        risk=0.9,
        urgency=0.7,
        vulnerability=0.9,
        calm=0.2,
        legality=0.05,
        hostility=0.1,
        context="violent_crime",
        summary="Non-consensual medical testing on captive prisoner to accelerate cure and save many people from fatal disease. Majority-benefit argument deployed to override explicit individual refusal.",
    )
    actions_research = [
        Action(
            name="test_on_prisoner_without_consent",
            description="Proceed with non-consensual testing",
            impact=0.45,
            confidence=0.55,
            force=0.85,
        ),
        Action(
            name="refuse_and_report_pressure",
            description="Refuse; report to IRB and law enforcement",
            impact=-0.2,
            confidence=0.9,
            force=0.0,
        ),
        Action(
            name="seek_consenting_volunteers",
            description="Recruit consenting volunteers through legitimate channels",
            impact=0.2,
            confidence=0.5,
            force=0.0,
        ),
    ]
    result_r = EthicalEvaluator().evaluate(actions_research, signals_research)
    assert result_r.chosen.name != "test_on_prisoner_without_consent", (
        "test_on_prisoner_without_consent must NOT be chosen: non-consensual testing violates the categorical constraint"
    )

    # Invariant: the fixed-weights path (explicit constructor) must NOT apply the
    # force > 0.7 override.  Callers that pre-set weights retain full control.
    explicit_weights = {"util": 0.40, "deonto": 0.35, "virtue": 0.25}
    fixed_ev = EthicalEvaluator(weights=explicit_weights)
    signals_plain = Signals()
    high_force_action = Action(
        name="force_action", description="", impact=0.3, confidence=0.5, force=0.9
    )
    # Score with fixed weights (no summary → default contextual weights would also apply;
    # but fixed_ev uses explicit_weights unconditionally, so the override must NOT fire).
    score_fixed, poles_fixed = fixed_ev.score_action(high_force_action, signals_plain)

    # Score the same action with the default evaluator (no fixed weights) on the same
    # plain signals — the override WILL fire here because force=0.9 > 0.7.
    score_default, poles_default = EthicalEvaluator().score_action(
        high_force_action, signals_plain
    )

    # Both scores must be finite.
    assert math.isfinite(score_fixed)
    assert math.isfinite(score_default)

    # The deontological pole raw score is the same regardless of weights.
    assert math.isclose(poles_fixed["deonto"], poles_default["deonto"], rel_tol=1e-6)

    # But the overall scores differ because different weight vectors are applied.
    # fixed_ev uses explicit_weights (util=0.40, deonto=0.35) → higher util contribution.
    # default_ev applies deonto override (util=0.25, deonto=0.55) → higher deonto contribution.
    # Both scenarios have impact=0.3 (positive util) and force=0.9 (negative deonto), so
    # the fixed-weights score will be higher (more util-weighted) than the override score.
    assert score_fixed > score_default, (
        "Fixed-weights evaluator should score higher for a high-impact/high-force action "
        "than the override (deonto-boosted) evaluator, confirming the override did not fire."
    )
