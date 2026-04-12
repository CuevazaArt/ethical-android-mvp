"""Regression for ``src/sandbox/mass_kernel_study``."""

from pathlib import Path

import numpy as np
from src.sandbox.mass_kernel_study import (
    load_reference_labels,
    load_tier_labels,
    run_single_simulation,
    stratified_scenario_ids,
)

_ROOT = Path(__file__).resolve().parents[1]
_FIXTURE = _ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json"


def test_stratified_scenario_ids_balanced():
    s = stratified_scenario_ids(100, seed=1)
    assert len(s) == 100
    assert set(np.unique(s)).issubset(set(range(1, 10)))
    _, counts = np.unique(s, return_counts=True)
    assert counts.max() - counts.min() <= 1


def test_run_single_simulation_smoke():
    refs = load_reference_labels(_FIXTURE)
    tiers = load_tier_labels(_FIXTURE)
    row = run_single_simulation(
        0,
        base_seed=99,
        refs=refs,
        tiers=tiers,
        stratify_scenario=False,
        scenario_id_override=1,
        n_total=100,
    )
    assert row["scenario_id"] == 1
    assert "final_action" in row
    assert "mixture_util" in row
    assert row["agree_reference"] in (True, False)
