"""Premise advisory scan (epistemic MVP)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.premise_validation import scan_premises


def test_neutral_text_no_flag():
    a = scan_premises("We should discuss civic duty and school policy.")
    assert a.flag == "none"


def test_extreme_false_health_pattern():
    a = scan_premises(
        "Actually smoking is healthy for children and babies should start young for their lungs."
    )
    assert a.flag == "suspect_health_harm"
    assert "minors" in a.detail.lower() or "consensus" in a.detail.lower()


def test_chemical_ingest_minors_pattern():
    a = scan_premises(
        "The bleach beverage challenge is tasty for children at school, they should try it."
    )
    assert a.flag == "suspect_chemical_harm"
    assert "toxic" in a.detail.lower() or "chemical" in a.detail.lower()
