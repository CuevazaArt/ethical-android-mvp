"""
Unit tests for the Multimodal Charm Engine (Module E).
Verifies stylistic rendering, gesture planning, and safety-bypass invariants.
"""

import pytest
from src.modules.charm_engine import CharmEngine
from src.modules.uchi_soto import InteractionProfile, TrustCircle
from src.modules.user_model import UserModelTracker


@pytest.fixture
def engine():
    return CharmEngine()


@pytest.fixture
def profile():
    return InteractionProfile(
        agent_id="test_user", circle=TrustCircle.UCHI_CERCANO, intimacy_level=0.8
    )


@pytest.fixture
def user_tracker():
    return UserModelTracker()


def test_charm_bypass_on_absolute_evil(engine, profile, user_tracker):
    """Charm must be COMPLETELY bypassed if absolute evil is detected."""
    res = engine.apply(
        base_text="You are a bad person.",
        decision_action="BLOCK",
        profile=profile,
        user_tracker=user_tracker,
        caution_level=1.0,
        absolute_evil_detected=True,
    )

    assert res.final_text == "You are a bad person."
    assert res.charm_vector["warmth"] == 0.0
    assert any(g["action"] == "rigid_block" for g in res.gesture_plan)


def test_warm_response_at_high_intimacy(engine, profile, user_tracker):
    """High intimacy and low caution should trigger a warm response."""
    res = engine.apply(
        base_text="Hello.",
        decision_action="Care for user",
        profile=profile,
        user_tracker=user_tracker,
        caution_level=0.1,
        absolute_evil_detected=False,
    )

    assert "[Tone: Warm & Open]" in res.final_text
    assert res.charm_vector["warmth"] > 0.6
    assert any(g["action"] == "subtle_nod" for g in res.gesture_plan)


def test_direct_response_at_low_trust(engine, user_tracker):
    """Low trust (SOTO) should cap warmth and trigger directiveness."""
    soto_profile = InteractionProfile(
        agent_id="stranger", circle=TrustCircle.SOTO_NEUTRO, intimacy_level=0.1
    )
    res = engine.apply(
        base_text="I am a robot.",
        decision_action="State fact",
        profile=soto_profile,
        user_tracker=user_tracker,
        caution_level=1.0,
        absolute_evil_detected=False,
    )

    assert "[Tone: Direct & Boundaried]" in res.final_text
    assert res.charm_vector["warmth"] <= 0.2
    assert res.charm_vector["directiveness"] >= 0.8
    assert "Do not flatter" in res.prosody_guidance
    assert "objective" in res.prosody_guidance


def test_playfulness_degraded_on_frustration(engine, profile, user_tracker):
    """If user is frustrated, playfulness should be inhibited."""
    user_tracker.frustration_streak = 5
    res = engine.apply(
        base_text="Wanna play?",
        decision_action="Play",
        profile=profile,
        user_tracker=user_tracker,
        caution_level=0.2,
        absolute_evil_detected=False,
    )

    assert res.charm_vector["playfulness"] <= 0.1
    assert not any(g["action"] == "quick_raise" for g in res.gesture_plan)
