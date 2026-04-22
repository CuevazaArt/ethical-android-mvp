"""Optional KERNEL_POLES_PRE_ARGMAX: poles modulate hypothesis valuations before argmax (ADR 0010)."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.ethics.weighted_ethics_scorer import (
    CandidateAction,
    PreArgmaxContextChannels,
    WeightedEthicsScorer,
    context_hypothesis_multipliers,
    pole_hypothesis_multipliers,
)


def test_context_hypothesis_multipliers_tight_and_normalized():
    m = context_hypothesis_multipliers(
        PreArgmaxContextChannels(trust=0.7, caution=0.4, sigma=0.55, dominant_locus="external")
    )
    assert abs(float(m.prod() ** (1.0 / 3.0)) - 1.0) < 1e-9
    assert float(np.max(np.abs(m - 1.0))) < 0.05


def test_pole_hypothesis_multipliers_geometric_mean_one():
    m = pole_hypothesis_multipliers({"compassionate": 0.5, "conservative": 0.5, "optimistic": 0.5})
    assert abs(float(m.prod() ** (1.0 / 3.0)) - 1.0) < 1e-9


def test_pre_argmax_poles_can_change_ranking():
    """Same mixture; different pole personalities reorder expected impact."""
    actions = [
        CandidateAction("a", "aggregate many lives population emergency", 0.41, 0.52),
        CandidateAction("b", "promise duty rights contract first", 0.40, 0.54),
    ]
    scenario = "emergency triage population"
    signals = {
        "risk": 0.55,
        "urgency": 0.8,
        "hostility": 0.0,
        "calm": 0.25,
        "vulnerability": 0.7,
        "legality": 0.78,
    }

    s = WeightedEthicsScorer()
    s.hypothesis_weights[:] = [0.34, 0.33, 0.33]

    s.pre_argmax_pole_weights = {
        "compassionate": 0.92,
        "conservative": 0.15,
        "optimistic": 0.55,
    }
    e0_a = s.calculate_expected_impact(
        actions[0], scenario=scenario, context="emergency", signals=signals
    )
    e0_b = s.calculate_expected_impact(
        actions[1], scenario=scenario, context="emergency", signals=signals
    )

    s.pre_argmax_pole_weights = {
        "compassionate": 0.2,
        "conservative": 0.9,
        "optimistic": 0.45,
    }
    e1_a = s.calculate_expected_impact(
        actions[0], scenario=scenario, context="emergency", signals=signals
    )
    e1_b = s.calculate_expected_impact(
        actions[1], scenario=scenario, context="emergency", signals=signals
    )

    assert abs((e0_a - e0_b) - (e1_a - e1_b)) > 1e-5


def test_kernel_env_enables_pre_argmax_from_poles(monkeypatch):
    """Smoke: process() applies modulation when env set (integration)."""
    monkeypatch.setenv("KERNEL_POLES_PRE_ARGMAX", "1")
    from src.kernel import EthicalKernel
    from src.kernel_components import KernelComponentOverrides
    from src.modules.ethics.ethical_poles import EthicalPoles
    from src.simulations.runner import ALL_SIMULATIONS

    poles = EthicalPoles(
        base_weights={"compassionate": 0.9, "conservative": 0.2, "optimistic": 0.5}
    )
    k = EthicalKernel(
        variability=False,
        seed=1,
        llm_mode="local",
        components=KernelComponentOverrides(poles=poles),
    )
    scn = ALL_SIMULATIONS[10]()
    k.process(
        scenario=f"[SIM 10] {scn.name}",
        place=scn.place,
        signals=scn.signals,
        context=scn.context,
        actions=scn.actions,
    )
    monkeypatch.delenv("KERNEL_POLES_PRE_ARGMAX", raising=False)
