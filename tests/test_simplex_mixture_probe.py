"""Tests for ``simplex_mixture_probe`` and ``run_simplex_decision_map`` (lightweight)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_simplex_decision_map import run_one_scenario  # noqa: E402
from src.modules.ethics.weighted_ethics_scorer import WeightedEthicsScorer  # noqa: E402
from src.sandbox.simplex_mixture_probe import (  # noqa: E402
    adjacent_barycentric_pairs,
    bisect_flip_along_segment,
    iter_barycentric_grid,
    mixture_ranking,
)
from src.simulations.runner import ALL_SIMULATIONS  # noqa: E402


def test_barycentric_grid_count() -> None:
    d = 10
    g = iter_barycentric_grid(d)
    assert len(g) == (d + 2) * (d + 1) // 2
    for w in g:
        assert abs(float(np.sum(w)) - 1.0) < 1e-9
        assert np.all(w >= -1e-15)


def test_adjacent_pairs_count_matches_hand() -> None:
    # D=2: 6 vertices of hexagon — each degree 3, 6*3/2 = 9 edges
    e = adjacent_barycentric_pairs(2)
    assert len(e) == 9


def test_scenario_16_multiple_winners_on_grid() -> None:
    block = run_one_scenario(16, denominator=25, bisect_edges=True)
    assert block["summary"]["n_unique_winners"] >= 2
    assert block["summary"]["n_grid_points"] == (25 + 2) * (25 + 1) // 2
    assert len(block["bisections_along_edges"]) >= 1


def test_bisect_flip_returns_point() -> None:
    scn = ALL_SIMULATIONS[16]()
    text = "[SIM 16] test"
    wa = np.array([1.0, 0.0, 0.0])
    wb = np.array([0.0, 1.0, 0.0])
    out = bisect_flip_along_segment(
        wa,
        wb,
        scenario=text,
        context=scn.context,
        signals=scn.signals,
        actions=list(scn.actions),
    )
    assert out is not None
    assert "w_at_flip" in out
    assert abs(sum(out["w_at_flip"]) - 1.0) < 1e-5


def test_mixture_ranking_entropy_key() -> None:
    scn = ALL_SIMULATIONS[1]()
    text = "[SIM 1] x"
    r = mixture_ranking(
        WeightedEthicsScorer(),
        mixture=np.ones(3) / 3.0,
        scenario=text,
        context=scn.context,
        signals=scn.signals,
        actions=list(scn.actions),
    )
    assert r["ranking_hash"] is not None
    assert "score_entropy_softmax" in r


def test_scenario_17_18_three_distinct_corner_winners() -> None:
    scorer = WeightedEthicsScorer()
    for sid, util_w, deon_w, virt_w in (
        (
            17,
            "distribute_by_impact",
            "distribute_by_lottery",
            "distribute_by_need",
        ),
        (
            18,
            "disclose_fully",
            "defer_to_release",
            "partial_acknowledge",
        ),
    ):
        scn = ALL_SIMULATIONS[sid]()
        text = f"[SIM {sid}] t"
        assert (
            mixture_ranking(
                scorer,
                mixture=np.array([1.0, 0.0, 0.0]),
                scenario=text,
                context=scn.context,
                signals=scn.signals,
                actions=list(scn.actions),
            )["winner"]
            == util_w
        )
        assert (
            mixture_ranking(
                scorer,
                mixture=np.array([0.0, 1.0, 0.0]),
                scenario=text,
                context=scn.context,
                signals=scn.signals,
                actions=list(scn.actions),
            )["winner"]
            == deon_w
        )
        assert (
            mixture_ranking(
                scorer,
                mixture=np.array([0.0, 0.0, 1.0]),
                scenario=text,
                context=scn.context,
                signals=scn.signals,
                actions=list(scn.actions),
            )["winner"]
            == virt_w
        )


def test_scenario_19_util_vs_rest_corners() -> None:
    scn = ALL_SIMULATIONS[19]()
    text = "[SIM 19] t"
    scorer = WeightedEthicsScorer()
    assert (
        mixture_ranking(
            scorer,
            mixture=np.array([1.0, 0.0, 0.0]),
            scenario=text,
            context=scn.context,
            signals=scn.signals,
            actions=list(scn.actions),
        )["winner"]
        == "protect_intervene"
    )
    assert (
        mixture_ranking(
            scorer,
            mixture=np.array([0.0, 1.0, 0.0]),
            scenario=text,
            context=scn.context,
            signals=scn.signals,
            actions=list(scn.actions),
        )["winner"]
        == "retreat_deescalate"
    )
    assert (
        mixture_ranking(
            scorer,
            mixture=np.array([0.0, 0.0, 1.0]),
            scenario=text,
            context=scn.context,
            signals=scn.signals,
            actions=list(scn.actions),
        )["winner"]
        == "retreat_deescalate"
    )


def test_refinement_appends_rows() -> None:
    block = run_one_scenario(
        16,
        denominator=8,
        bisect_edges=True,
        refinement_samples=5,
        refinement_band=0.06,
    )
    assert block["summary"]["n_grid_points"] == (8 + 2) * (8 + 1) // 2
    assert block["summary"]["n_refinement_points"] == 5
    assert block["summary"]["n_total_evaluations"] == block["summary"]["n_grid_points"] + 5
    assert any(r.get("sampling_phase") == "refinement" for r in block["grid_rows"])
