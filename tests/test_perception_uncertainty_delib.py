"""Optional deliberation nudge when LLM perception coercion uncertainty is high."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.bayesian_engine import CandidateAction

# High arousal + strong candidate → sympathetic + non-gray will → baseline ``D_fast``.
_FAST_SIGNALS = {
    "risk": 0.85,
    "urgency": 0.7,
    "hostility": 0.2,
    "calm": 0.15,
    "vulnerability": 0.3,
    "legality": 1.0,
}
_FAST_ACTIONS = [
    CandidateAction("act", "x", 0.85, 0.95),
    CandidateAction("wait", "y", 0.1, 0.8),
]
_SEED = 0


def _k() -> EthicalKernel:
    return EthicalKernel(variability=False, seed=_SEED)


def test_perception_uncertainty_no_op_when_flag_off(monkeypatch):
    monkeypatch.delenv("KERNEL_PERCEPTION_UNCERTAINTY_DELIB", raising=False)
    d0 = _k().process(
        "test",
        "here",
        _FAST_SIGNALS,
        "everyday",
        _FAST_ACTIONS,
        perception_coercion_uncertainty=None,
    )
    d1 = _k().process(
        "test",
        "here",
        _FAST_SIGNALS,
        "everyday",
        _FAST_ACTIONS,
        perception_coercion_uncertainty=0.99,
    )
    assert d0.decision_mode == "D_fast"
    assert d1.decision_mode == "D_fast"


def test_perception_uncertainty_upgrades_d_fast_to_delib_when_flag_on(monkeypatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_UNCERTAINTY_DELIB", "1")
    monkeypatch.setenv("KERNEL_PERCEPTION_UNCERTAINTY_MIN", "0.25")
    d0 = _k().process(
        "test",
        "here",
        _FAST_SIGNALS,
        "everyday",
        _FAST_ACTIONS,
        perception_coercion_uncertainty=None,
    )
    d1 = _k().process(
        "test",
        "here",
        _FAST_SIGNALS,
        "everyday",
        _FAST_ACTIONS,
        perception_coercion_uncertainty=0.99,
    )
    assert d0.decision_mode == "D_fast"
    assert d1.decision_mode == "D_delib"


def test_perception_uncertainty_below_threshold_no_upgrade(monkeypatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_UNCERTAINTY_DELIB", "1")
    monkeypatch.setenv("KERNEL_PERCEPTION_UNCERTAINTY_MIN", "0.9")
    d0 = _k().process(
        "test",
        "here",
        _FAST_SIGNALS,
        "everyday",
        _FAST_ACTIONS,
        perception_coercion_uncertainty=None,
    )
    d1 = _k().process(
        "test",
        "here",
        _FAST_SIGNALS,
        "everyday",
        _FAST_ACTIONS,
        perception_coercion_uncertainty=0.2,
    )
    assert d0.decision_mode == "D_fast"
    assert d1.decision_mode == "D_fast"
