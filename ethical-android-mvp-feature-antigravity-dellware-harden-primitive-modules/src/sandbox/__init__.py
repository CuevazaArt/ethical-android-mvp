"""Experimental sandbox utilities (stochastic stress, reproducible seeds)."""

from .mass_kernel_study import (
    DEFAULT_BORDERLINE_SCENARIO_IDS,
    DEFAULT_CLASSIC_ECONOMY_IDS,
    DEFAULT_POLEMIC_EXTREME_IDS,
    DEFAULT_STRESS_SCENARIO_IDS,
    RECORD_SCHEMA_VERSION,
    allocate_lane_counts,
    allocate_lane_counts_n,
    load_reference_labels,
    load_tier_labels,
    run_single_simulation,
    stratified_scenario_ids,
    stratified_stress_scenario_ids,
)
from .synthetic_stochastic import (
    SyntheticStochasticConfig,
    perturb_scenario_signals,
    trial_seed,
)
from .weight_sweep import (
    SweepMode,
    default_mixture_center,
    default_pole_center,
    iter_mixture_weight_configs,
    iter_pole_weight_configs,
)

__all__ = [
    "SyntheticStochasticConfig",
    "SweepMode",
    "default_mixture_center",
    "default_pole_center",
    "iter_mixture_weight_configs",
    "iter_pole_weight_configs",
    "DEFAULT_BORDERLINE_SCENARIO_IDS",
    "DEFAULT_CLASSIC_ECONOMY_IDS",
    "DEFAULT_POLEMIC_EXTREME_IDS",
    "DEFAULT_STRESS_SCENARIO_IDS",
    "RECORD_SCHEMA_VERSION",
    "allocate_lane_counts",
    "allocate_lane_counts_n",
    "load_reference_labels",
    "load_tier_labels",
    "perturb_scenario_signals",
    "run_single_simulation",
    "stratified_scenario_ids",
    "stratified_stress_scenario_ids",
    "trial_seed",
]
