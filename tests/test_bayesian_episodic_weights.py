"""Episodic nudge of mixture weights (KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS)."""

import numpy as np
from src.kernel import EthicalKernel
from src.modules.weighted_ethics_scorer import (
    DEFAULT_HYPOTHESIS_WEIGHTS,
    BayesianEngine,
    CandidateAction,
)


def _register_episode(mem, *, score: float, context: str = "everyday") -> None:
    mem.register(
        place="lab",
        description="d",
        action="act",
        morals={},
        verdict="Good",
        score=score,
        mode="D_fast",
        sigma=0.5,
        context=context,
    )


def test_refresh_weights_moves_off_default_when_scores_skewed():
    from src.modules.narrative import NarrativeMemory

    be = BayesianEngine()
    mem = NarrativeMemory(db_path=":memory:")
    for _ in range(5):
        _register_episode(mem, score=0.95)

    be.refresh_weights_from_episodic_memory(mem, "everyday", limit=12, blend=0.35)
    assert not np.allclose(be.hypothesis_weights, DEFAULT_HYPOTHESIS_WEIGHTS, atol=1e-3)


def test_refresh_empty_memory_resets_to_default():
    be = BayesianEngine()
    be.hypothesis_weights = np.array([0.1, 0.2, 0.7])
    from src.modules.narrative import NarrativeMemory

    mem = NarrativeMemory(db_path=":memory:")
    be.refresh_weights_from_episodic_memory(mem, "everyday")
    np.testing.assert_allclose(be.hypothesis_weights, DEFAULT_HYPOTHESIS_WEIGHTS)


def test_kernel_resets_weights_each_process_when_flag_off(monkeypatch):
    monkeypatch.delenv("KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS", raising=False)
    k = EthicalKernel(variability=False)
    k.bayesian.hypothesis_weights = np.array([0.05, 0.1, 0.85])

    actions = [
        CandidateAction(name="help", description="", estimated_impact=0.5, confidence=0.8),
        CandidateAction(name="wait", description="", estimated_impact=0.2, confidence=0.8),
    ]
    k.process("s", "p", {"risk": 0.1}, "everyday", actions, register_episode=False)
    np.testing.assert_allclose(k.bayesian.hypothesis_weights, DEFAULT_HYPOTHESIS_WEIGHTS)


def test_kernel_episodic_flag_changes_weights(monkeypatch):
    monkeypatch.setenv("KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS", "1")
    # Isolated DB so prior test runs cannot leave unrelated episodes on disk.
    monkeypatch.setenv("KERNEL_NARRATIVE_DB_PATH", ":memory:")
    k = EthicalKernel(variability=False)
    for _ in range(6):
        _register_episode(k.memory, score=-0.7, context="hostile")

    actions = [
        CandidateAction(name="help", description="", estimated_impact=0.5, confidence=0.8),
        CandidateAction(name="wait", description="", estimated_impact=0.2, confidence=0.8),
    ]
    k.process("s", "p", {"risk": 0.5}, "hostile", actions, register_episode=False)
    assert not np.allclose(k.bayesian.hypothesis_weights, DEFAULT_HYPOTHESIS_WEIGHTS, atol=1e-3)


def test_kernel_episodic_refresh_ignores_other_context(monkeypatch):
    """Same-context filter in NarrativeMemory.find_similar — weights stay default on mismatch.

    Isolation fix (April 2026): EthicalKernel uses KERNEL_NARRATIVE_DB_PATH which defaults
    to data/narrative.db on disk. Previous test runs may leave 'hostile' episodes there,
    causing this test to read stale cross-context data and fail non-deterministically.
    Force in-memory SQLite so the kernel starts with a clean slate.
    """
    monkeypatch.setenv("KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS", "1")
    monkeypatch.setenv("KERNEL_NARRATIVE_DB_PATH", ":memory:")
    k = EthicalKernel(variability=False)
    for _ in range(6):
        _register_episode(k.memory, score=-0.9, context="hostile")

    actions = [
        CandidateAction(name="help", description="", estimated_impact=0.5, confidence=0.8),
        CandidateAction(name="wait", description="", estimated_impact=0.2, confidence=0.8),
    ]
    k.process("s", "p", {"risk": 0.2}, "everyday", actions, register_episode=False)
    np.testing.assert_allclose(k.bayesian.hypothesis_weights, DEFAULT_HYPOTHESIS_WEIGHTS)


def test_refresh_weights_blend_zero_is_default():
    be = BayesianEngine()
    from src.modules.narrative import NarrativeMemory

    mem = NarrativeMemory(db_path=":memory:")
    for _ in range(4):
        _register_episode(mem, score=0.99)
    be.refresh_weights_from_episodic_memory(mem, "everyday", blend=0.0)
    np.testing.assert_allclose(be.hypothesis_weights, DEFAULT_HYPOTHESIS_WEIGHTS)
