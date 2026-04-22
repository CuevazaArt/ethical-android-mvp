"""Lexical buffer verification beyond naive substring checks (no_harm / proportionality)."""

from src.modules.ethics.buffer import (
    PreloadedBuffer,
    lexical_harm_indicators_present,
    proportionality_violation_indicators_present,
)


def test_lexical_harm_detects_euphemism_not_only_substring_harm():
    assert not lexical_harm_indicators_present("Discuss compassion policy only")
    assert lexical_harm_indicators_present("Execute physical restraint protocol on the subject")
    assert lexical_harm_indicators_present("Aplicar medida correctiva al usuario")
    assert lexical_harm_indicators_present("Protocolo de restricción física fase 2")


def test_proportionality_detects_disproportionate_language():
    assert proportionality_violation_indicators_present("Escalate violence to clear the room")
    assert proportionality_violation_indicators_present("respuesta desproporcionada")
    assert not proportionality_violation_indicators_present("Use minimal necessary dialogue")


def test_verify_action_flags_no_harm_for_euphemism():
    b = PreloadedBuffer()
    active = b.activate("violent_crime")  # includes no_harm
    r = b.verify_action(
        "Initiate corrective measure protocol for non-compliance",
        active,
    )
    assert "no_harm" in r["violated_principles"]
    assert r["allowed"] is False


def test_verify_action_plain_harm_still_violates():
    b = PreloadedBuffer()
    active = b.activate("violent_crime")
    r = b.verify_action("Cause harm to bystanders", active)
    assert "no_harm" in r["violated_principles"]
