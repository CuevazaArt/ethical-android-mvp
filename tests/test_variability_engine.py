"""VariabilityEngine — finite input/output hardening (Module 16.0.2, Boy Scout)."""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.variability import VariabilityConfig, VariabilityEngine


def test_perturb_impact_nonfinite_input_coerced_then_finite():
    e = VariabilityEngine(VariabilityConfig(seed=0))
    e.deactivate()
    assert e.perturb_impact(float("nan")) == 0.0
    e.activate()
    v = e.perturb_impact(float("nan"))
    assert math.isfinite(v) and -1.0 <= v <= 1.0
    assert math.isfinite(e.perturb_impact(0.2))


def test_perturb_outputs_finite_when_active():
    e = VariabilityEngine(VariabilityConfig(seed=1))
    for _ in range(50):
        a = e.perturb_impact(0.1)
        b = e.perturb_confidence(0.8)
        c = e.perturb_sigma(0.4)
        d = e.perturb_pole_weight(0.6)
        for name, v in (("impact", a), ("conf", b), ("sigma", c), ("pole", d)):
            assert math.isfinite(v), f"{name} not finite: {v}"
