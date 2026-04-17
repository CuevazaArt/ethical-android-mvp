"""Regression for ``src/sandbox/mass_kernel_study``."""

from pathlib import Path

import numpy as np
from src.sandbox.mass_kernel_study import (
    DEFAULT_CLASSIC_ECONOMY_IDS,
    RECORD_SCHEMA_VERSION,
    allocate_lane_counts,
    allocate_lane_counts_n,
    load_reference_labels,
    load_tier_labels,
    run_single_simulation,
    stratified_scenario_ids,
    stratified_stress_scenario_ids,
)

_ROOT = Path(__file__).resolve().parents[1]
_FIXTURE = _ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json"


def test_stratified_scenario_ids_balanced():
    s = stratified_scenario_ids(100, seed=1)
    assert len(s) == 100
    assert set(np.unique(s)).issubset(set(range(1, 10)))
    _, counts = np.unique(s, return_counts=True)
    assert counts.max() - counts.min() <= 1


def test_stratified_scenario_ids_economy_triple():
    s = stratified_scenario_ids(99, seed=2, ids=DEFAULT_CLASSIC_ECONOMY_IDS)
    assert set(np.unique(s)).issubset({1, 5, 7})
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
    assert row["kernel_seed"] == 99
    assert "final_action" in row
    assert "mixture_util" in row
    assert row["agree_reference"] in (True, False)
    assert row["experiment_protocol"] == "legacy"
    assert row["experiment_lane"] == "legacy_uniform"
    assert "ei_margin_bin" in row
    assert "observation_palette" in row
    assert row.get("poles_pre_argmax") is False
    assert row.get("context_richness_pre_argmax") is False
    assert row.get("signal_stress") == 0.0
    assert row["sampling_pole_lo"] == 0.05
    assert row["sampling_pole_hi"] == 0.95
    assert row["sampling_mixture_dirichlet_alpha"] == 1.0
    assert RECORD_SCHEMA_VERSION == 6
    assert row["bma_enabled"] is False
    assert row["bma_win_prob_winner"] is None
    assert row["bma_win_prob_max"] is None


def test_run_single_simulation_bma_smoke():
    """Phase D (ADR 0012): BMA fields populated when bma_enabled=True."""
    refs = load_reference_labels(_FIXTURE)
    tiers = load_tier_labels(_FIXTURE)
    row = run_single_simulation(
        0,
        base_seed=7,
        refs=refs,
        tiers=tiers,
        stratify_scenario=False,
        scenario_id_override=1,
        n_total=10,
        bma_enabled=True,
        bma_dirichlet_alpha=3.0,
        bma_n_samples=200,
    )
    assert row["bma_enabled"] is True
    assert isinstance(row["bma_win_prob_winner"], str)
    assert isinstance(row["bma_win_prob_max"], float)
    assert 0.0 <= row["bma_win_prob_max"] <= 1.0
    assert isinstance(row["bma_winner_prob_at_final_action"], float)
    # bma_win_prob_winner must be the action with highest win probability
    assert row["bma_win_prob_max"] >= row["bma_winner_prob_at_final_action"]


def test_tight_pole_sampling_range():
    refs = load_reference_labels(_FIXTURE)
    tiers = load_tier_labels(_FIXTURE)
    for i in range(30):
        row = run_single_simulation(
            i,
            base_seed=42,
            refs=refs,
            tiers=tiers,
            stratify_scenario=False,
            scenario_id_override=1,
            n_total=1000,
            pole_weight_low=0.38,
            pole_weight_high=0.62,
        )
        assert 0.38 <= row["pole_compassionate"] <= 0.62
        assert row["sampling_pole_lo"] == 0.38
        assert row["sampling_pole_hi"] == 0.62


def test_allocate_lane_counts_sums_to_n():
    for n in (1, 7, 100, 100_000):
        a, b, c = allocate_lane_counts(n, (0.45, 0.35, 0.2))
        assert a + b + c == n


def test_stratified_stress_scenario_ids():
    s = stratified_stress_scenario_ids(30, (2, 5, 8), seed=3)
    assert len(s) == 30
    assert set(np.unique(s)).issubset({2, 5, 8})


def test_run_single_simulation_v2_lane_a():
    refs = load_reference_labels(_FIXTURE)
    tiers = load_tier_labels(_FIXTURE)
    row = run_single_simulation(
        0,
        base_seed=100,
        refs=refs,
        tiers=tiers,
        stratify_scenario=True,
        scenario_id_override=None,
        n_total=100,
        experiment_protocol="v2",
        lane_split=(0.45, 0.35, 0.2),
    )
    assert row["experiment_protocol"] == "v2"
    assert row["experiment_lane"] == "A_mixture_focus"
    assert row["pole_compassionate"] == 0.5
    assert row["scenario_id"] in DEFAULT_CLASSIC_ECONOMY_IDS


def test_allocate_lane_counts_n_four():
    assert sum(allocate_lane_counts_n(100, (0.25, 0.25, 0.25, 0.25))) == 100


def test_run_single_simulation_v4_polemic_lane():
    refs = load_reference_labels(_FIXTURE)
    tiers = load_tier_labels(_FIXTURE)
    row = run_single_simulation(
        99,
        base_seed=100,
        refs=refs,
        tiers=tiers,
        stratify_scenario=True,
        scenario_id_override=None,
        n_total=100,
        experiment_protocol="v4",
        lane_split=(0.20, 0.16, 0.12, 0.20, 0.32),
        poles_pre_argmax=True,
    )
    assert row["experiment_protocol"] == "v4"
    assert row["experiment_lane"] == "E_polemic_extreme"
    assert row["scenario_id"] in (13, 14, 15)


def test_run_single_simulation_v3_borderline_lane():
    refs = load_reference_labels(_FIXTURE)
    tiers = load_tier_labels(_FIXTURE)
    # Index 99 with default v3 split (0.28,0.22,0.12,0.38) of n=100 -> last lane D
    row = run_single_simulation(
        99,
        base_seed=100,
        refs=refs,
        tiers=tiers,
        stratify_scenario=True,
        scenario_id_override=None,
        n_total=100,
        experiment_protocol="v3",
        lane_split=(0.28, 0.22, 0.12, 0.38),
        poles_pre_argmax=True,
    )
    assert row["experiment_protocol"] == "v3"
    assert row["experiment_lane"] == "D_borderline"
    assert row["scenario_id"] in (10, 11, 12)
    assert row["poles_pre_argmax"] is True
