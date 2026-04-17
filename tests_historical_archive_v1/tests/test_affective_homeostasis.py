"""Pilar 4 — affective homeostasis telemetry (UX-only)."""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.affective_homeostasis import homeostasis_telemetry


def test_homeostasis_high_sigma_elevated():
    d = SimpleNamespace(
        sympathetic_state=SimpleNamespace(sigma=0.85),
        reflection=None,
        affect=None,
    )
    h = homeostasis_telemetry(d)
    assert h["state"] == "elevated_activation"
    assert h["sigma"] == 0.85


def test_homeostasis_within_range():
    d = SimpleNamespace(
        sympathetic_state=SimpleNamespace(sigma=0.5),
        reflection=SimpleNamespace(strain_index=0.2),
        affect=None,
    )
    h = homeostasis_telemetry(d)
    assert h["state"] == "within_range"
