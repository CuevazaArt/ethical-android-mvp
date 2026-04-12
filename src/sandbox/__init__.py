"""Experimental sandbox utilities (stochastic stress, reproducible seeds)."""

from .synthetic_stochastic import (
    SyntheticStochasticConfig,
    perturb_scenario_signals,
    trial_seed,
)

__all__ = [
    "SyntheticStochasticConfig",
    "perturb_scenario_signals",
    "trial_seed",
]
