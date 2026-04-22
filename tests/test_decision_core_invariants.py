"""
Architectural invariants for the scalar action choice vs peripheral modules.

Many modules (weakness pole, PAD, augenesis, psi sleep on other paths) do **not**
change ``KernelDecision.final_action`` in ``EthicalKernel.process`` — that string
comes from ``BayesianEngine`` after MalAbs pruning. See
``docs/proposals/README.md``.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.cognition.bayesian_engine import CandidateAction


def test_final_action_is_bayesian_chosen_name_when_unblocked():
    """Regression guard: peripheral layers must not silently swap the argmax action."""
    k = EthicalKernel(variability=False)
    actions = [
        CandidateAction("high_impact", "d", 0.92, 0.9),
        CandidateAction("low_impact", "d", 0.05, 0.85),
    ]
    d = k.process(
        "civic scenario",
        "street",
        {
            "risk": 0.1,
            "calm": 0.6,
            "hostility": 0.0,
            "legality": 1.0,
            "vulnerability": 0.1,
        },
        "ctx",
        actions,
        register_episode=True,
    )
    assert not d.blocked
    assert d.bayesian_result is not None
    assert d.final_action == d.bayesian_result.chosen_action.name
