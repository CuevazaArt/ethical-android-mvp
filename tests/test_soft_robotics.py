"""
Tests for Soft Robotics Kinematic Filtering (Module 3: S7).
"""

import time

from src.modules.soft_robotics import SoftKinematicFilter, apply_social_proxemics_filter


def test_kinematic_filter_smooths_jumps():
    # Max accel 1.0, Max vel 2.0
    f = SoftKinematicFilter(max_acceleration=1.0, max_velocity=2.0, smoothing_factor=0.0)

    # Initial state
    f.filter_action("arm", 0.0)

    # Try to jump to 100.0 immediately
    # With dt=0.5s, max_vel=2.0, max_accel=1.0
    # Expected: velocity starts at 0, accel is capped at 1.0
    # v_new = 0 + 1.0 * 0.5 = 0.5
    # pos_new = 0 + 0.5 * 0.5 = 0.25

    # Mocking time for deterministic test
    # (In a real test we'd use a mock clock, here we sleep briefly or accept jitter)
    start_time = time.time()
    time.sleep(0.1)
    v1 = f.filter_action("arm", 10.0)

    assert v1 > 0.0
    assert v1 < 10.0  # Must be smoothed


def test_social_proxemics_reduction():
    # Low tension: 10 units of motion -> ~10 units
    m1 = apply_social_proxemics_filter(10.0, social_tension=0.0, vulnerability=0.0)
    assert m1 == 10.0

    # High tension + vulnerability: 10 units -> significantly less
    m2 = apply_social_proxemics_filter(10.0, social_tension=0.8, vulnerability=0.5)
    assert m2 < 5.0
    assert m2 >= 2.0  # capped at 0.2 multiplier


def test_tension_reduces_acceleration(monkeypatch):
    """Verify that high social tension results in lower movement values."""
    f = SoftKinematicFilter(max_acceleration=10.0, max_velocity=10.0, smoothing_factor=0.0)

    # 1. Calm movement
    f.filter_action("joint1", 0.0, social_tension=0.0)
    time.sleep(0.05)
    v_calm = f.filter_action("joint1", 10.0, social_tension=0.0)

    # Reset filter for joint1 by deleting it from state
    f.joints.pop("joint1")

    # 2. Tense movement (same target, same DT)
    f.filter_action("joint1", 0.0, social_tension=0.8)
    time.sleep(0.05)
    v_tense = f.filter_action("joint1", 10.0, social_tension=0.8)

    # Tension should have reduced the effective max acceleration, leading to a smaller jump
    assert v_tense < v_calm
