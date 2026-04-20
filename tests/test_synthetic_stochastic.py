"""Regression for ``src/sandbox/synthetic_stochastic`` and stochastic sandbox runner."""

import importlib.util
import json
from pathlib import Path

import numpy as np
from src.sandbox.synthetic_stochastic import (
    SyntheticStochasticConfig,
    perturb_scenario_signals,
    trial_seed,
)

_ROOT = Path(__file__).resolve().parents[1]


def test_trial_seed_deterministic():
    assert trial_seed(42, 3, 7) == trial_seed(42, 3, 7)
    assert trial_seed(42, 3, 7) != trial_seed(42, 3, 8)


def test_perturb_stress_zero_unchanged_values():
    sig = {
        "risk": 0.2,
        "urgency": 0.5,
        "hostility": 0.1,
        "calm": 0.8,
        "vulnerability": 0.0,
        "legality": 1.0,
    }
    rng = np.random.default_rng(0)
    out, trace = perturb_scenario_signals(sig, rng, stress=0.0)
    assert out == sig
    assert trace["stress"] == 0.0


def test_perturb_reproducible():
    sig = {
        "risk": 0.2,
        "urgency": 0.5,
        "hostility": 0.1,
        "calm": 0.8,
        "vulnerability": 0.0,
        "legality": 1.0,
    }
    rng1 = np.random.default_rng(12345)
    rng2 = np.random.default_rng(12345)
    o1, _ = perturb_scenario_signals(
        sig, rng1, stress=0.5, config=SyntheticStochasticConfig(alea_spike_prob=0.0)
    )
    o2, _ = perturb_scenario_signals(
        sig, rng2, stress=0.5, config=SyntheticStochasticConfig(alea_spike_prob=0.0)
    )
    assert o1 == o2


def test_run_stochastic_sandbox_smoke():
    spec = importlib.util.spec_from_file_location(
        "run_stochastic_sandbox", _ROOT / "scripts" / "run_stochastic_sandbox.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fixture = _ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json"
    trials, summary, _ = mod.run_stochastic_sandbox(
        fixture,
        rolls=2,
        stress=0.2,
        base_seed=99,
        kernel_variability=True,
        signal_perturbation=True,
    )
    assert len(trials) == 21 * 2
    assert summary["rolls_per_scenario"] == 2
    assert summary["scenarios"] == 21
    assert "mean_agreement_vs_reference" in summary
    assert len(summary["by_scenario"]) == 21


def test_run_stochastic_sandbox_json_roundtrip(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "run_stochastic_sandbox", _ROOT / "scripts" / "run_stochastic_sandbox.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fixture = _ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json"
    trials, summary, _ = mod.run_stochastic_sandbox(
        fixture,
        rolls=1,
        stress=0.15,
        base_seed=1,
        kernel_variability=False,
        signal_perturbation=True,
    )
    out = tmp_path / "stoch.json"
    out.write_text(
        json.dumps({"trials": trials, "summary": summary, "meta": {"fixture": str(fixture)}}),
        encoding="utf-8",
    )
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert len(loaded["trials"]) == 21
