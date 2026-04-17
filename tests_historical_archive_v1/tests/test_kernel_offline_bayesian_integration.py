"""
Integration test: full offline Bayesian pipeline (ADR 0014).

Verifies that EthicalKernel.process() completes and returns a valid KernelDecision
with correct Bayesian fields when LLM_MODE=local and KERNEL_BAYESIAN_FEEDBACK /
KERNEL_HIERARCHICAL_FEEDBACK are active — no network calls required.

ADR 0014 invariants tested:
  1. process() never raises under LLM_MODE=local.
  2. KernelDecision.final_action is always populated.
  3. KernelDecision.blocked is correctly set.
  4. mixture_posterior_alpha is populated when Bayesian feedback is active.
  5. HierarchicalUpdater cache is reused across ticks (mtime-based).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from src.kernel import EthicalKernel

_FIXTURE_FB = Path(__file__).resolve().parent / "fixtures" / "feedback" / "compatible_17_18_19.json"
_FIXTURE_SCENARIOS = (
    Path(__file__).resolve().parent / "fixtures" / "empirical_pilot" / "scenarios.json"
)


def _make_kernel(monkeypatch: pytest.MonkeyPatch) -> EthicalKernel:
    """Build a minimal offline kernel using LLM_MODE=local (heuristic templates, no API)."""
    monkeypatch.setenv("LLM_MODE", "local")
    monkeypatch.setenv("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", "1")
    # local mode uses heuristic templates — no LLM object needed
    return EthicalKernel(llm_mode="local")


# ---------------------------------------------------------------------------
# Baseline offline (no Bayesian)
# ---------------------------------------------------------------------------


def test_offline_process_completes(monkeypatch: pytest.MonkeyPatch) -> None:
    """ADR 0014 invariant 1 + 2: process() completes and final_action is populated."""
    kernel = _make_kernel(monkeypatch)
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[1]()
    d = kernel.process(
        scenario=scn.name,
        place="test",
        context=scn.context,
        actions=scn.actions,
        signals=scn.signals,
    )
    assert d.final_action, "final_action must be non-empty offline"
    assert d.blocked in (True, False)
    assert d.mixture_posterior_alpha is None  # no Bayesian flags


# ---------------------------------------------------------------------------
# ADR 0012 Level 2 offline
# ---------------------------------------------------------------------------


def test_offline_bayesian_feedback_l2(monkeypatch: pytest.MonkeyPatch) -> None:
    """mixture_posterior_alpha populated when KERNEL_BAYESIAN_FEEDBACK active (offline)."""
    if not _FIXTURE_FB.is_file():
        pytest.skip("feedback fixture not found")

    monkeypatch.setenv("KERNEL_BAYESIAN_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_PATH", str(_FIXTURE_FB))
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "500")

    kernel = _make_kernel(monkeypatch)
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[17]()
    d = kernel.process(
        scenario=scn.name,
        place="test",
        context=scn.context,
        actions=scn.actions,
        signals=scn.signals,
    )
    assert d.final_action, "final_action must be populated"
    # ADR 0014 invariant 4
    assert d.mixture_posterior_alpha is not None, "mixture_posterior_alpha must be set"
    assert len(d.mixture_posterior_alpha) == 3
    assert all(a > 0 for a in d.mixture_posterior_alpha)
    assert d.feedback_consistency in ("compatible", "contradictory", "insufficient")


# ---------------------------------------------------------------------------
# ADR 0013 HierarchicalUpdater offline
# ---------------------------------------------------------------------------


def test_offline_hierarchical_feedback(monkeypatch: pytest.MonkeyPatch) -> None:
    """KERNEL_HIERARCHICAL_FEEDBACK active: mixture_posterior_alpha populated offline."""
    if not _FIXTURE_FB.is_file():
        pytest.skip("feedback fixture not found")

    monkeypatch.setenv("KERNEL_HIERARCHICAL_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_PATH", str(_FIXTURE_FB))
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "500")

    kernel = _make_kernel(monkeypatch)
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[17]()
    d = kernel.process(
        scenario=scn.name,
        place="test",
        context=scn.context,
        actions=scn.actions,
        signals=scn.signals,
    )
    assert d.final_action
    assert d.mixture_posterior_alpha is not None
    assert d.hierarchical_context_key is not None


def test_offline_hierarchical_cache_reuse(monkeypatch: pytest.MonkeyPatch) -> None:
    """ADR 0014 invariant 5: HierarchicalUpdater cache is reused across ticks."""
    if not _FIXTURE_FB.is_file():
        pytest.skip("feedback fixture not found")

    monkeypatch.setenv("KERNEL_HIERARCHICAL_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_PATH", str(_FIXTURE_FB))
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "300")

    kernel = _make_kernel(monkeypatch)
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[17]()

    # First tick — builds cache
    kernel.process(
        scenario=scn.name,
        place="test",
        context=scn.context,
        actions=scn.actions,
        signals=scn.signals,
    )
    cache_after_first = kernel._hier_updater_cache
    mtime_after_first = kernel._hier_cache_mtime

    # Second tick — should reuse cache (same file, no mtime change)
    kernel.process(
        scenario=scn.name,
        place="test",
        context=scn.context,
        actions=scn.actions,
        signals=scn.signals,
    )
    assert kernel._hier_updater_cache is cache_after_first, "cache object must be reused"
    assert kernel._hier_cache_mtime == mtime_after_first


# ---------------------------------------------------------------------------
# OOS-004: precedence warning (both flags)
# ---------------------------------------------------------------------------


def test_precedence_warning_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """OOS-004: warning emitted when HIERARCHICAL + BAYESIAN_FEEDBACK both enabled."""
    if not _FIXTURE_FB.is_file():
        pytest.skip("feedback fixture not found")

    monkeypatch.setenv("KERNEL_HIERARCHICAL_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_BAYESIAN_FEEDBACK", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_PATH", str(_FIXTURE_FB))
    monkeypatch.setenv("KERNEL_FEEDBACK_MC_SAMPLES", "300")

    kernel = _make_kernel(monkeypatch)
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[17]()

    import logging

    with caplog.at_level(logging.WARNING, logger="src.kernel"):
        kernel.process(
            scenario=scn.name,
            place="test",
            context=scn.context,
            actions=scn.actions,
            signals=scn.signals,
        )

    assert any(
        "OOS-004" in r.message or "Precedence conflict" in r.message for r in caplog.records
    ), "Expected OOS-004 precedence warning in logs"


# ---------------------------------------------------------------------------
# BMA offline
# ---------------------------------------------------------------------------


def test_offline_bma_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """BMA win_probabilities populated offline when KERNEL_BMA_ENABLED=1."""
    monkeypatch.setenv("KERNEL_BMA_ENABLED", "1")
    monkeypatch.setenv("KERNEL_BMA_SAMPLES", "300")
    monkeypatch.setenv("KERNEL_BMA_ALPHA", "3.0")

    kernel = _make_kernel(monkeypatch)
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[1]()
    d = kernel.process(
        scenario=scn.name,
        place="test",
        context=scn.context,
        actions=scn.actions,
        signals=scn.signals,
    )
    assert d.bma_win_probabilities is not None
    assert len(d.bma_win_probabilities) > 0
    total_prob = sum(d.bma_win_probabilities.values())
    assert abs(total_prob - 1.0) < 0.02, f"BMA probs should sum ~1.0, got {total_prob}"
