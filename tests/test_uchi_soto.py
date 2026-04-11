"""Uchi–Soto: tone_brief, familiarity blend, register_result."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.uchi_soto import TrustCircle, UchiSotoModule


def test_tone_brief_non_empty_per_circle():
    m = UchiSotoModule()
    for circle in TrustCircle:
        tb = UchiSotoModule._tone_brief_for_circle(circle)
        assert tb
        assert "Social posture" in tb


def test_evaluate_interaction_sets_tone_brief():
    m = UchiSotoModule()
    ev = m.evaluate_interaction(
        {"hostility": 0.0, "manipulation": 0.0, "familiarity": 0.8},
        "u1",
        "",
    )
    assert ev.circle == TrustCircle.UCHI_CERCANO
    assert ev.tone_brief
    assert "close uchi" in ev.tone_brief.lower()


def test_familiarity_blend_uses_profile_trust():
    m = UchiSotoModule()
    m.evaluate_interaction(
        {"hostility": 0.0, "manipulation": 0.0, "familiarity": 0.35},
        "blend_user",
        "",
    )
    # First hit: soto_neutro (0.35 alone)
    assert m.profiles["blend_user"].circle == TrustCircle.SOTO_NEUTRO
    m.profiles["blend_user"].trust_score = 0.85
    c2 = m.classify(
        {"hostility": 0.0, "manipulation": 0.0, "familiarity": 0.35},
        "blend_user",
    )
    # Blended familiarity > 0.4 → uchi_amplio or higher
    assert c2 in (TrustCircle.UCHI_AMPLIO, TrustCircle.UCHI_CERCANO)


def test_register_result_nudges_trust():
    m = UchiSotoModule()
    m.evaluate_interaction(
        {"hostility": 0.0, "manipulation": 0.0, "familiarity": 0.5},
        "r1",
        "",
    )
    t0 = m.profiles["r1"].trust_score
    m.register_result("r1", True)
    assert m.profiles["r1"].trust_score > t0
    assert m.profiles["r1"].positive_history == 1
