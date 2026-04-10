"""Local sovereignty stub — future DAO calibration veto."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.local_sovereignty import evaluate_calibration_update


def test_evaluate_calibration_stub_accepts():
    r = evaluate_calibration_update({"weights": [0.1]}, narrative_episode_count=3)
    assert r.accept is True
    assert "stub" in r.reason.lower()
