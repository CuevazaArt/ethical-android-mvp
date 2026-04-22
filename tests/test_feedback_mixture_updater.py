"""Tests for ``feedback_mixture_updater`` (ADR 0012 explicit triples)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from src.modules.cognition.feedback_mixture_updater import (
    FeedbackItem,
    FeedbackUpdater,
    build_scenario_candidates_map,
    scenario_candidate_triples_from_runner,
)


def test_triples_from_scenario_17() -> None:
    t = scenario_candidate_triples_from_runner(17)
    assert t is not None
    assert "distribute_by_need" in t
    assert set(t["distribute_by_need"].keys()) == {"util", "deon", "virtue"}


def test_build_map_17_18_19() -> None:
    m = build_scenario_candidates_map([17, 18, 19])
    assert m is not None
    assert len(m) == 3


def test_build_map_includes_scenario_without_override() -> None:
    assert build_scenario_candidates_map([1, 17]) is None


def test_bma_win_probabilities_sum_to_one() -> None:
    t = scenario_candidate_triples_from_runner(17)
    assert t is not None
    u = FeedbackUpdater(n_samples=500, seed=1)
    br = u.bma_win_probabilities(t, n_samples=500)
    assert abs(sum(br.win_probabilities.values()) - 1.0) < 1e-5


def test_ingest_feedback_need_on_17(tmp_path: Path) -> None:
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps([{"scenario_id": 17, "preferred_action": "distribute_by_need"}]),
        encoding="utf-8",
    )
    cmap = build_scenario_candidates_map([17])
    assert cmap is not None
    items = FeedbackUpdater.load_feedback_file(p)
    u = FeedbackUpdater(n_samples=800, seed=2, update_strength=2.0)
    fr = u.ingest_feedback(items, cmap)
    assert fr.n_feedback_items == 1
    assert fr.consistency in ("compatible", "insufficient")


def test_drift_guard_clamps_after_feedback() -> None:
    cmap = build_scenario_candidates_map([17])
    assert cmap is not None
    max_d = 0.05
    u = FeedbackUpdater(
        initial_alpha=[10.0, 10.0, 10.0],
        max_drift=max_d,
        n_samples=2500,
        seed=0,
        update_strength=80.0,
    )
    fb = FeedbackItem(scenario_id=17, preferred_action="distribute_by_need")
    u.update_from_feedback(fb, cmap[17])
    mean = u.posterior_mean()
    init_norm = [1 / 3, 1 / 3, 1 / 3]
    for i in range(3):
        # Clamp per axis then renormalize; allow small slack beyond box after renorm.
        assert abs(mean[i] - init_norm[i]) <= max_d + 0.03


def test_compatible_fixture_explicit_triples_path() -> None:
    """Versioned JSON matches scenarios 17–19 explicit triples → explicit_triples updater."""
    from src.modules.cognition.feedback_mixture_posterior import load_and_apply_feedback

    root = Path(__file__).resolve().parents[1]
    p = root / "tests" / "fixtures" / "feedback" / "compatible_17_18_19.json"
    alpha, consistency, meta = load_and_apply_feedback(p, rng=np.random.default_rng(0))
    assert consistency == "compatible"
    assert meta.get("updater") == "explicit_triples"
    assert alpha.shape == (3,)
    assert float(alpha.sum()) > 0
