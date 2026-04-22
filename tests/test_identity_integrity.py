"""Pilar 2 — identity genome drift helpers."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.identity_integrity import (
    hypothesis_weights_allowed,
    pruning_recalibration_allowed,
    relative_deviation,
)


def test_relative_deviation():
    assert relative_deviation(0.35, 0.3) < 0.2
    assert relative_deviation(0.1, 0.3) > 0.5


def test_pruning_recalibration_small_delta_ok():
    assert pruning_recalibration_allowed(0.3, 0.3, -0.02, 0.15) is True


def test_pruning_recalibration_large_delta_rejected():
    assert pruning_recalibration_allowed(0.3, 0.3, -0.5, 0.15) is False


def test_hypothesis_weights_trivial():
    g = (0.4, 0.35, 0.25)
    assert hypothesis_weights_allowed(g, g, 0.01) is True
