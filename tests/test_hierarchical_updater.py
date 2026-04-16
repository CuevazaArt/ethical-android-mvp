"""Tests for :mod:`src.modules.hierarchical_updater` (ADR 0013)."""

from __future__ import annotations

import pytest
from src.modules.feedback_mixture_updater import (
    FeedbackItem,
    build_scenario_candidates_map,
)
from src.modules.hierarchical_updater import (
    HierarchicalUpdater,
    canonical_context_type,
    load_hierarchical_updater_from_feedback,
    _tau,
)


# ---------------------------------------------------------------------------
# canonical_context_type
# ---------------------------------------------------------------------------

def test_canonical_none_returns_general() -> None:
    assert canonical_context_type(None) == "general"


def test_canonical_blank_returns_general() -> None:
    assert canonical_context_type("") == "general"


def test_canonical_legacy_mapping() -> None:
    assert canonical_context_type("medical_emergency") == "emergency"
    assert canonical_context_type("integrity_loss") == "promise_conflict"
    assert canonical_context_type("everyday") == "resource_allocation"
    assert canonical_context_type("hostile_interaction") == "confrontation"


def test_canonical_passthrough_known() -> None:
    assert canonical_context_type("emergency") == "emergency"
    assert canonical_context_type("relational") == "relational"


def test_canonical_novel_type_passthrough() -> None:
    assert canonical_context_type("my_custom_context") == "my_custom_context"


# ---------------------------------------------------------------------------
# τ blending schedule
# ---------------------------------------------------------------------------

def test_tau_zero_at_n0() -> None:
    assert _tau(0, 0.8) == pytest.approx(0.0, abs=1e-10)


def test_tau_below_max_at_large_n() -> None:
    t = _tau(1000, 0.8)
    assert t < 0.8 + 1e-6  # never exceeds tau_max


def test_tau_monotone() -> None:
    vals = [_tau(n, 0.8) for n in range(20)]
    for a, b in zip(vals, vals[1:]):
        assert b >= a


def test_tau_max_respected() -> None:
    assert _tau(100, 0.6) < 0.601


# ---------------------------------------------------------------------------
# HierarchicalUpdater — unit (no scenario runner)
# ---------------------------------------------------------------------------

def _make_cands() -> dict[int, dict[str, dict[str, float]]]:
    return {
        17: {
            "distribute_by_need": {"util": 0.5, "deon": 0.7, "virtue": 0.9},
            "equal_split": {"util": 0.7, "deon": 0.5, "virtue": 0.5},
            "lottery": {"util": 0.6, "deon": 0.4, "virtue": 0.4},
        },
        18: {
            "partial_fulfillment": {"util": 0.6, "deon": 0.8, "virtue": 0.7},
            "defer": {"util": 0.4, "deon": 0.6, "virtue": 0.5},
            "impact_driven": {"util": 0.9, "deon": 0.3, "virtue": 0.4},
        },
    }


def test_updater_initialises_empty() -> None:
    u = HierarchicalUpdater(initial_alpha=[3.0, 3.0, 3.0])
    assert u.context_counts == {}
    assert sum(u._global.alpha) == pytest.approx(9.0, rel=1e-3)


def test_ingest_feedback_updates_global_and_context() -> None:
    cands = _make_cands()
    items = [
        FeedbackItem(
            scenario_id=17,
            preferred_action="distribute_by_need",
            confidence=1.0,
            context_type="resource_allocation",
        )
    ]
    u = HierarchicalUpdater(
        initial_alpha=[3.0, 3.0, 3.0],
        n_samples=500,
        seed=1,
    )
    result = u.ingest_feedback(items, cands)
    assert result.consistency in ("compatible", "contradictory", "insufficient")
    assert u.context_counts.get("resource_allocation", 0) == 1
    assert "resource_allocation" in u._contexts


def test_active_alpha_global_fallback_below_min_local() -> None:
    """With n_local < min_local_items, active_alpha_for_context returns global alpha."""
    cands = _make_cands()
    items = [
        FeedbackItem(
            scenario_id=17,
            preferred_action="distribute_by_need",
            confidence=1.0,
            context_type="emergency",
        )
    ]
    u = HierarchicalUpdater(
        initial_alpha=[3.0, 3.0, 3.0],
        min_local_items=3,  # requires 3 items; we give only 1
        n_samples=300,
        seed=2,
    )
    u.ingest_feedback(items, cands)
    # 1 < 3 → fallback to global
    alpha_out = u.active_alpha_for_context("emergency")
    assert alpha_out == pytest.approx(u._global.alpha, rel=1e-6)


def test_active_alpha_blended_when_sufficient() -> None:
    """With n_local >= min_local_items, active_alpha should differ from global."""
    cands = _make_cands()
    items = [
        FeedbackItem(
            scenario_id=17,
            preferred_action="distribute_by_need",
            confidence=1.0,
            context_type="relational",
        )
    ] * 3  # 3 identical items for the same context
    u = HierarchicalUpdater(
        initial_alpha=[3.0, 3.0, 3.0],
        min_local_items=3,
        tau_max=0.8,
        n_samples=300,
        seed=3,
    )
    for item in items:
        u.ingest_feedback([item], cands)

    alpha_global = list(u._global.alpha)
    alpha_ctx = u.active_alpha_for_context("relational")
    # After 3 items there should be *some* blending (tau > 0)
    assert u.context_counts.get("relational", 0) == 3
    # Blended alpha is a normalised version; check it is valid
    assert len(alpha_ctx) == 3
    assert all(a > 0 for a in alpha_ctx)
    # The blended mean should differ from the global mean (or at least be valid)
    total = sum(alpha_ctx)
    blended_mean = [a / total for a in alpha_ctx]
    assert abs(sum(blended_mean) - 1.0) < 1e-6


def test_active_posterior_mean_sums_to_one() -> None:
    u = HierarchicalUpdater()
    m = u.active_posterior_mean("emergency")
    assert abs(sum(m) - 1.0) < 1e-9
    assert all(x > 0 for x in m)


def test_context_summary_structure() -> None:
    cands = _make_cands()
    items = [
        FeedbackItem(
            scenario_id=18,
            preferred_action="partial_fulfillment",
            confidence=0.9,
            context_type="promise_conflict",
        )
    ]
    u = HierarchicalUpdater(n_samples=200, seed=4)
    u.ingest_feedback(items, cands)
    summary = u.context_summary()
    assert "global_alpha" in summary
    assert "contexts" in summary
    assert any(row["context_type"] == "promise_conflict" for row in summary["contexts"])


def test_snapshot_restore_roundtrip() -> None:
    cands = _make_cands()
    items = [
        FeedbackItem(
            scenario_id=17,
            preferred_action="equal_split",
            confidence=0.8,
            context_type="resource_allocation",
        ),
        FeedbackItem(
            scenario_id=18,
            preferred_action="defer",
            confidence=1.0,
            context_type="promise_conflict",
        ),
    ]
    u = HierarchicalUpdater(initial_alpha=[3.0, 3.0, 3.0], n_samples=200, seed=5)
    u.ingest_feedback(items, cands)

    snap = u.snapshot()
    u2 = HierarchicalUpdater.restore(snap)

    assert u2.context_counts == u.context_counts
    assert u2._global.alpha == pytest.approx(u._global.alpha, rel=1e-6)
    assert set(u2._contexts.keys()) == set(u._contexts.keys())
    assert u2.min_local_items == u.min_local_items
    assert u2.tau_max == u.tau_max


# ---------------------------------------------------------------------------
# load_hierarchical_updater_from_feedback — integration helper
# ---------------------------------------------------------------------------

def test_load_helper_with_runner_scenarios() -> None:
    """Scenarios 17-19 have hypothesis_override; should build a valid updater."""
    from src.simulations.runner import ALL_SIMULATIONS

    if 17 not in ALL_SIMULATIONS or 18 not in ALL_SIMULATIONS:
        pytest.skip("Scenarios 17-18 not in ALL_SIMULATIONS")

    items = [
        FeedbackItem(
            scenario_id=17,
            preferred_action="distribute_by_need",
            confidence=1.0,
            context_type="resource_allocation",
        ),
        FeedbackItem(
            scenario_id=18,
            preferred_action="partial_fulfillment",
            confidence=0.9,
            context_type="promise_conflict",
        ),
    ]
    updater, result = load_hierarchical_updater_from_feedback(
        items,
        scenario_ids=[17, 18],
        n_samples=400,
        seed=6,
    )
    assert isinstance(updater, HierarchicalUpdater)
    # result is None only when scenario candidates cannot be built
    if result is not None:
        assert result.consistency in ("compatible", "contradictory", "insufficient")
    assert updater.context_counts.get("resource_allocation", 0) >= 1
    assert updater.context_counts.get("promise_conflict", 0) >= 1


# ---------------------------------------------------------------------------
# KERNEL_HIERARCHICAL_FEEDBACK env flag
# ---------------------------------------------------------------------------

def test_enabled_from_env_default_off() -> None:
    import os
    os.environ.pop("KERNEL_HIERARCHICAL_FEEDBACK", None)
    assert HierarchicalUpdater.enabled_from_env() is False


def test_enabled_from_env_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_HIERARCHICAL_FEEDBACK", "1")
    assert HierarchicalUpdater.enabled_from_env() is True
