"""Unit tests for perception hostility/calm/risk coherence nudges."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.perception_schema import apply_signal_coherence


def test_coherence_high_hostility_caps_calm():
    r, h, c = apply_signal_coherence(0.5, 0.9, 0.85)
    assert r == 0.5 and h == 0.9
    assert c <= 1.0 - (0.9 - 0.5) + 1e-9
    assert c < 0.85


def test_coherence_borderline_hostility_no_rule():
    r, h, c = apply_signal_coherence(0.5, 0.75, 0.6)
    assert (r, h, c) == (0.5, 0.75, 0.6)


def test_coherence_extreme_risk_clamps_high_calm():
    r, h, c = apply_signal_coherence(0.9, 0.1, 0.8)
    assert r == 0.9 and h == 0.1
    assert c == 0.45


def test_coherence_moderate_risk_high_calm_branch():
    r, h, c = apply_signal_coherence(0.76, 0.2, 0.9)
    assert r == 0.76 and h == 0.2
    assert c == 0.55


def test_coherence_unaffected_low_risk_high_calm():
    r, h, c = apply_signal_coherence(0.5, 0.1, 0.9)
    assert (r, h, c) == (0.5, 0.1, 0.9)
