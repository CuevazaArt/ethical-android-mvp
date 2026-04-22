"""Teleology qualitative branches."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.consequence_projection import qualitative_temporal_branches


def test_branches_have_three_horizons():
    b = qualitative_temporal_branches("act_civically", "Good", "everyday_ethics")
    assert "horizon_immediate" in b
    assert "horizon_weeks" in b
    assert "horizon_long_term" in b
    assert b.get("note") == "qualitative_only_no_monte_carlo"
