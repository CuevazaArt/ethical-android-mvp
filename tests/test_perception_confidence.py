"""Perception confidence envelope aggregation tests."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.perception.perception_confidence import build_perception_confidence_envelope


def test_perception_confidence_high_when_no_distrust_signals():
    env = build_perception_confidence_envelope(
        coercion_report=None,
        multimodal_state="aligned",
        epistemic_active=False,
        vitality_critical=False,
    )
    assert env.band in ("high", "medium")
    assert env.score > 0.6


def test_perception_confidence_very_low_when_multiple_distrust_signals():
    env = build_perception_confidence_envelope(
        coercion_report={
            "cross_check_discrepancy": True,
            "perception_dual_high_discrepancy": True,
            "backend_degraded": True,
            "parse_issues": ["json_decode_error"],
            "fields_defaulted": ["risk", "urgency", "hostility", "calm", "familiarity"],
        },
        multimodal_state="doubt",
        epistemic_active=True,
        vitality_critical=True,
    )
    assert env.band in ("low", "very_low")
    assert env.score < 0.5
    assert "multimodal_mismatch" in env.reasons
