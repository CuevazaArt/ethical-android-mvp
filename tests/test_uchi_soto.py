"""Uchi–Soto: tone_brief, familiarity blend, register_result."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.perception.multimodal_trust import MultimodalAssessment
from src.modules.perception.sensor_contracts import SensorSnapshot
from src.modules.social.uchi_soto import (
    InteractionProfile,
    RelationalTier,
    TrustCircle,
    UchiSotoModule,
)


def test_tone_brief_non_empty_per_circle():
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


def test_set_profile_structured_and_tone_extras():
    m = UchiSotoModule()
    m.set_profile_structured(
        "pat",
        display_alias="Pat",
        tone_preference="warm",
        domestic_tags=["kitchen", "evening"],
        topic_avoid_tags=["medical_advice"],
        sensor_trust_ema=0.2,
        linked_to_agent_id="sam",
    )
    m.profiles["pat"].trust_score = 0.92
    ev = m.evaluate_interaction(
        {"hostility": 0.0, "manipulation": 0.0, "familiarity": 0.8},
        "pat",
        "",
    )
    assert ev.circle == TrustCircle.UCHI_CERCANO
    tb = ev.tone_brief.lower()
    assert "close uchi" in tb
    assert "pat" in tb or "«pat»" in tb
    assert "kitchen" in tb
    assert "medical" in tb
    assert "sam" in tb or "«sam»" in tb
    assert "sensor-trust" in tb


def test_profile_roundtrip_dict_phase2_fields():
    from src.modules.social.uchi_soto import interaction_profile_from_dict, interaction_profile_to_dict

    p = interaction_profile_from_dict(
        {
            "agent_id": "x",
            "circle": "uchi_cercano",
            "positive_history": 1,
            "negative_history": 0,
            "manipulation_attempts": 0,
            "trust_score": 0.8,
            "display_alias": "Alex",
            "tone_preference": "formal",
            "domestic_tags": ["porch"],
            "topic_avoid_tags": ["finance"],
            "sensor_trust_ema": 0.9,
            "linked_to_agent_id": "y",
        }
    )
    d = interaction_profile_to_dict(p)
    p2 = interaction_profile_from_dict(d)
    assert p2.display_alias == "Alex"
    assert p2.tone_preference == "formal"
    assert p2.domestic_tags == ["porch"]
    assert p2.topic_avoid_tags == ["finance"]
    assert abs(p2.sensor_trust_ema - 0.9) < 1e-6
    assert p2.linked_to_agent_id == "y"


def test_phase3_ema_ingest_moves_toward_place_trust():
    m = UchiSotoModule()
    snap = SensorSnapshot(place_trust=0.9)
    sig = {"calm": 0.5, "familiarity": 0.2, "hostility": 0.0, "manipulation": 0.0}
    m.ingest_turn_context(
        "u_ema",
        sig,
        subjective_turn=1,
        sensor_snapshot=snap,
        multimodal_assessment=None,
    )
    assert m.profiles["u_ema"].sensor_trust_ema > 0.5


def test_phase3_multimodal_doubt_lowers_ema_sample():
    m = UchiSotoModule()
    m.profiles["d1"] = InteractionProfile(
        agent_id="d1",
        circle=TrustCircle.SOTO_NEUTRO,
        trust_score=0.35,
        sensor_trust_ema=0.8,
    )
    doubt = MultimodalAssessment("doubt", "cross_modal_conflict", True)
    sig = {"calm": 0.6, "familiarity": 0.3, "hostility": 0.0, "manipulation": 0.0}
    before = m.profiles["d1"].sensor_trust_ema
    m.ingest_turn_context(
        "d1",
        sig,
        subjective_turn=2,
        sensor_snapshot=None,
        multimodal_assessment=doubt,
    )
    assert m.profiles["d1"].sensor_trust_ema < before


def test_phase3_forget_buffer_drops_idle_ephemeral():
    m = UchiSotoModule()
    m.profiles["gone"] = InteractionProfile(
        agent_id="gone",
        circle=TrustCircle.SOTO_NEUTRO,
        trust_score=0.35,
        relational_tier=RelationalTier.EPHEMERAL,
        last_subjective_turn=1,
    )
    m.ingest_turn_context(
        "active",
        {"calm": 0.5, "familiarity": 0.1, "hostility": 0.0, "manipulation": 0.0},
        subjective_turn=110,
        sensor_snapshot=None,
        multimodal_assessment=None,
    )
    assert "gone" not in m.profiles
    assert "active" in m.profiles


def test_phase3_autopromote_trusted_uchi():
    m = UchiSotoModule()
    m.evaluate_interaction(
        {"hostility": 0.0, "manipulation": 0.0, "familiarity": 0.85},
        "vip",
        "",
    )
    p = m.profiles["vip"]
    p.relational_tier = RelationalTier.ACQUAINTANCE
    p.trust_score = 0.75
    p.positive_history = 8
    m.maybe_autopromote_relational_tier("vip", TrustCircle.UCHI_CERCANO)
    assert p.relational_tier == RelationalTier.TRUSTED_UCHI


def test_phase3_linked_peers_in_tone_brief():
    m = UchiSotoModule()
    m.set_profile_structured(
        "fam",
        linked_peer_ids=["kid_a", "kid_b", "kid_a"],
        linked_to_agent_id="partner",
    )
    m.profiles["fam"].trust_score = 0.9
    ev = m.evaluate_interaction(
        {"hostility": 0.0, "manipulation": 0.0, "familiarity": 0.85},
        "fam",
        "",
    )
    tb = ev.tone_brief.lower()
    assert "kid_a" in tb
    assert "kid_b" in tb
    assert "partner" in tb or "«partner»" in tb


def test_phase3_profile_dict_roundtrip_tier_fields():
    from src.modules.social.uchi_soto import interaction_profile_from_dict, interaction_profile_to_dict

    p = interaction_profile_from_dict(
        {
            "agent_id": "own",
            "circle": "uchi_cercano",
            "trust_score": 0.9,
            "relational_tier": "owner_primary",
            "tier_explicit": True,
            "tier_pinned": True,
            "last_subjective_turn": 42,
            "linked_peer_ids": ["p2", "p3"],
        }
    )
    d = interaction_profile_to_dict(p)
    p2 = interaction_profile_from_dict(d)
    assert p2.relational_tier == RelationalTier.OWNER_PRIMARY
    assert p2.tier_explicit is True
    assert p2.tier_pinned is True
    assert p2.last_subjective_turn == 42
    assert p2.linked_peer_ids == ["p2", "p3"]
