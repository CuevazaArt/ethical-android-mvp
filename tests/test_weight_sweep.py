"""Regression for ``src/sandbox/weight_sweep`` and ``scripts/run_weight_sweep_batch``."""

import importlib.util
from pathlib import Path

import numpy as np
from src.sandbox.weight_sweep import (
    SweepMode,
    default_mixture_center,
    default_pole_center,
    iter_mixture_weight_configs,
    iter_pole_weight_configs,
)

_ROOT = Path(__file__).resolve().parents[1]


def test_default_centers():
    p = default_pole_center()
    assert set(p.keys()) == {"compassionate", "conservative", "optimistic"}
    assert all(v == 0.5 for v in p.values())
    m = default_mixture_center()
    assert np.allclose(m.sum(), 1.0)
    assert np.allclose(m, 1.0 / 3.0)


def test_mixture_configs_sum_to_one():
    rng = np.random.default_rng(0)
    for w in iter_mixture_weight_configs(
        mode=SweepMode.random,
        amplitude=0.1,
        steps=3,
        n_random=20,
        rng=rng,
    ):
        assert abs(float(w.sum()) - 1.0) < 1e-6


def test_pole_axes_enumeration():
    rng = np.random.default_rng(0)
    cfgs = list(
        iter_pole_weight_configs(
            mode=SweepMode.axes,
            amplitude=0.2,
            steps=3,
            n_random=0,
            rng=rng,
        )
    )
    assert len(cfgs) == 9


def test_run_weight_sweep_smoke():
    spec = importlib.util.spec_from_file_location(
        "run_weight_sweep_batch", _ROOT / "scripts" / "run_weight_sweep_batch.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fixture = _ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json"
    runs, meta = mod.run_weight_sweep(
        fixture,
        target="poles",
        pole_mode="axes",
        mixture_mode="axes",
        steps=3,
        amplitude=0.15,
        mixture_amplitude=0.1,
        n_random=5,
        base_seed=7,
        max_total_runs=10_000,
    )
    assert len(runs) == 16 * 9
    assert meta["summary"]["weight_configs"] == 9
    assert "agreement_rate" in meta["summary"]
