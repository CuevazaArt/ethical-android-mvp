"""ADR 0012 — BMA win probabilities and optional feedback posterior."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from src.kernel import EthicalKernel
from src.modules.bayesian_mixture_averaging import (
    analytic_expected_weights,
    monte_carlo_win_probabilities,
    parse_bma_alpha_from_env,
)
from src.modules.feedback_mixture_posterior import (
    joint_satisfaction_monte_carlo,
    load_feedback_records,
)
from src.modules.weighted_ethics_scorer import CandidateAction, WeightedEthicsScorer
from src.simulations.runner import ALL_SIMULATIONS


def test_analytic_expected_weights_matches_dirichlet_mean() -> None:
    a = np.array([2.0, 3.0, 5.0], dtype=np.float64)
    m = analytic_expected_weights(a)
    assert abs(float(np.sum(m)) - 1.0) < 1e-9
    assert np.allclose(m, a / np.sum(a))


def test_monte_carlo_sums_to_one() -> None:
    scn = ALL_SIMULATIONS[1]()
    actions = list(scn.actions)
    scorer = WeightedEthicsScorer()
    text = "[SIM 1] t"
    rng = np.random.default_rng(0)
    probs = monte_carlo_win_probabilities(
        scorer,
        actions,
        alpha=np.array([3.0, 3.0, 3.0]),
        n_samples=400,
        scenario=text,
        context=scn.context,
        signals=scn.signals,
        rng=rng,
    )
    assert abs(sum(probs.values()) - 1.0) < 1e-5


def test_kernel_bma_attaches_fields(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KERNEL_BMA_ENABLED", "1")
    monkeypatch.setenv("KERNEL_BMA_SAMPLES", "120")
    monkeypatch.setenv("KERNEL_BMA_SEED", "7")
    k = EthicalKernel(variability=False, seed=42, llm_mode="local")
    scn = ALL_SIMULATIONS[1]()
    d = k.process(
        scenario=f"[SIM 1] {scn.name}",
        place=scn.place,
        signals=scn.signals,
        context=scn.context,
        actions=list(scn.actions),
    )
    assert d.bma_win_probabilities is not None
    assert abs(sum(d.bma_win_probabilities.values()) - 1.0) < 0.02
    assert d.bma_n_samples == 120
    assert d.bma_dirichlet_alpha is not None
    assert len(d.bma_dirichlet_alpha) == 3


def test_parse_bma_alpha_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_BMA_ALPHA", "2,3,5")
    a = parse_bma_alpha_from_env()
    assert np.allclose(a, [2.0, 3.0, 5.0])


def test_feedback_json_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps(
            [
                {
                    "scenario_id": 17,
                    "preferred_action": "distribute_by_need",
                    "confidence": 0.9,
                }
            ]
        ),
        encoding="utf-8",
    )
    recs = load_feedback_records(p)
    assert len(recs) == 1
    assert recs[0].scenario_id == 17


def test_joint_satisfaction_runs() -> None:
    from src.modules.feedback_mixture_posterior import FeedbackRecord

    recs = [
        FeedbackRecord(17, "distribute_by_need"),
    ]
    rng = np.random.default_rng(1)
    alpha = np.array([3.0, 3.0, 3.0])
    rate, _ = joint_satisfaction_monte_carlo(alpha, recs, n_samples=200, rng=rng)
    assert 0.0 <= rate <= 1.0


def test_kernel_feedback_compatible_versioned_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    """Documented ADR 0012 sample (17–19) loads and stays compatible with EthicalKernel."""
    root = Path(__file__).resolve().parents[1]
    p = root / "tests" / "fixtures" / "feedback" / "compatible_17_18_19.json"
    assert p.is_file()
    monkeypatch.setenv("KERNEL_BAYESIAN_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_PATH", str(p))
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "3000")
    monkeypatch.setenv("KERNEL_FEEDBACK_SEED", "1")
    k = EthicalKernel(variability=False, seed=42, llm_mode="local")
    scn = ALL_SIMULATIONS[3]()
    d = k.process(
        scenario=f"[SIM 3] {scn.name}",
        place=scn.place,
        signals=scn.signals,
        context=scn.context,
        actions=list(scn.actions),
    )
    assert d.mixture_posterior_alpha is not None
    assert d.feedback_consistency == "compatible"
    assert len(d.mixture_posterior_alpha) == 3


def test_feedback_kernel_updates_weights(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps([{"scenario_id": 17, "preferred_action": "distribute_by_need"}]),
        encoding="utf-8",
    )
    monkeypatch.setenv("KERNEL_BAYESIAN_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_PATH", str(p))
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "800")
    monkeypatch.setenv("KERNEL_FEEDBACK_SEED", "3")
    k = EthicalKernel(variability=False, seed=42, llm_mode="local")
    scn = ALL_SIMULATIONS[3]()
    d = k.process(
        scenario=f"[SIM 3] {scn.name}",
        place=scn.place,
        signals=scn.signals,
        context=scn.context,
        actions=list(scn.actions),
    )
    assert d.mixture_posterior_alpha is not None
    assert d.feedback_consistency in ("compatible", "contradictory", "insufficient")
    assert len(d.mixture_posterior_alpha) == 3


def test_run_feedback_posterior_script_default_fixture() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_feedback_posterior.py"
    env = {**os.environ, "KERNEL_FEEDBACK_MC_SAMPLES": "2000", "KERNEL_FEEDBACK_SEED": "0"}
    r = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["feedback_consistency"] == "compatible"
    assert data["meta"].get("updater") == "explicit_triples"
    assert len(data["posterior_alpha"]) == 3


def test_candidate_action_hypothesis_stub() -> None:
    """Sanity: override triple scores linearly under mixture."""
    a = CandidateAction(
        "x",
        "d",
        0.5,
        1.0,
        hypothesis_override=(0.2, 0.5, 0.9),
    )
    s = WeightedEthicsScorer()
    s.hypothesis_weights = np.array([1.0, 0.0, 0.0])
    ei = s.calculate_expected_impact(a, scenario="t", context="c", signals={})
    assert abs(ei - 0.2) < 1e-6
