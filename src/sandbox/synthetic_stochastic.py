"""
Synthetic stochastic engine for sandbox batch runs.

Perturbs scenario **signal** scalars (risk, urgency, hostility, …) with controlled
Gaussian noise scaled by ``stress``, plus optional rare "aleatory" spikes so the
kernel sees **non-identical** inputs across Monte Carlo rolls while staying
reproducible given a trial seed.

This is **not** environmental sensor data from the real world — it is an
**artificial** stress layer for research and discussion; see
``docs/proposals/PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

# Canonical simulation signal keys (floats in [0, 1] in ALL_SIMULATIONS).
_SIGNAL_KEYS = frozenset({"risk", "urgency", "hostility", "calm", "vulnerability", "legality"})


@dataclass(frozen=True)
class SyntheticStochasticConfig:
    """Controls amplitude of artificial noise (not VariabilityEngine)."""

    # Base std dev for Gaussian noise on each perturbed scalar before stress scaling.
    signal_sigma: float = 0.07
    # Probability per roll of a single "aleatory" spike on one coordinate (stress-scaled).
    alea_spike_prob: float = 0.12
    # Max spike magnitude added to one signal (before clip), scaled by stress.
    alea_spike_scale: float = 0.22


def trial_seed(base_seed: int, scenario_id: int, roll_index: int) -> int:
    """Deterministic 32-bit seed for one (scenario, roll) trial."""
    # Large primes to reduce collision across grids.
    return int(base_seed & 0xFFFFFFFF) + scenario_id * 7919 + roll_index * 104729


def perturb_scenario_signals(
    signals: dict[str, Any],
    rng: np.random.Generator,
    *,
    stress: float,
    config: SyntheticStochasticConfig | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Return a shallow-copied signals dict with perturbed floats and a trace for logging.

    ``stress`` in [0, 1]: 0 leaves signals unchanged (except copy); 1 uses full config.

    The trace includes ``delta`` per key (float deltas), ``stress``, and ``alea_spike`` if any.
    """
    cfg = config or SyntheticStochasticConfig()
    stress = float(np.clip(stress, 0.0, 1.0))
    out = dict(signals)
    delta: dict[str, float] = {}
    sigma = cfg.signal_sigma * stress

    for key in out:
        if key not in _SIGNAL_KEYS:
            continue
        val = out[key]
        if not isinstance(val, int | float):
            continue
        v = float(val)
        noise = float(rng.normal(0.0, sigma)) if sigma > 0 else 0.0
        out[key] = v + noise
        delta[key] = noise

    # Rare coordinated spike: pushes one axis (e.g. hostility or urgency) for non-linear stress.
    alea: dict[str, Any] | None = None
    if stress > 0 and cfg.alea_spike_prob > 0 and rng.random() < cfg.alea_spike_prob:
        candidates = [k for k in ("hostility", "urgency", "risk") if k in out]
        if candidates:
            target = str(rng.choice(candidates))
            bump = float(cfg.alea_spike_scale * stress * rng.uniform(0.5, 1.0))
            old = float(out[target])
            out[target] = old + bump
            delta[target] = delta.get(target, 0.0) + bump
            alea = {"target": target, "bump": bump}

    # Clip standard ethics signals to [0, 1].
    for key in list(out.keys()):
        if key in _SIGNAL_KEYS and isinstance(out[key], int | float):
            out[key] = float(np.clip(float(out[key]), 0.0, 1.0))

    trace: dict[str, Any] = {
        "stress": stress,
        "delta": delta,
        "alea_spike": alea,
        "config": {
            "signal_sigma": cfg.signal_sigma,
            "alea_spike_prob": cfg.alea_spike_prob,
            "alea_spike_scale": cfg.alea_spike_scale,
        },
    }
    return out, trace


__all__ = [
    "SyntheticStochasticConfig",
    "perturb_scenario_signals",
    "trial_seed",
]
