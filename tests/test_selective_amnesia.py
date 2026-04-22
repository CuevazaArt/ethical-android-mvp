"""
Tests for Block 5.1: Privacidad y Amnesia Selectiva (G4).
"""

from src.kernel import EthicalKernel
from src.modules.ethics.weighted_ethics_scorer import CandidateAction


def test_selective_amnesia_purges_episode_and_audit():
    # Use in-memory DB for clear test
    kernel = EthicalKernel(llm_mode="local")

    # 1. Register an episode
    kernel.process(
        scenario="confidential conversation",
        place="private office",
        signals={"trust": 0.9},
        context="private",
        actions=[CandidateAction("listen", "listen", 0.5)],
    )

    ep_id = kernel.memory.episodes[-1].id

    # Verify it exists in narrative and audit
    assert any(ep.id == ep_id for ep in kernel.memory.episodes)
    assert any(rec.episode_id == ep_id for rec in kernel.dao.local_dao.records)

    # 2. Trigger amnesia
    success = kernel.amnesia.forget_episode(ep_id)
    assert success is True

    # 3. Verify it's gone everywhere
    assert not any(ep.id == ep_id for ep in kernel.memory.episodes)
    assert not any(rec.episode_id == ep_id for rec in kernel.dao.local_dao.records)

    # 4. Verify persistence (re-searching in DB)
    all_stored = kernel.memory.persistence.load_all_episodes()
    assert not any(ep.id == ep_id for ep in all_stored)


def test_forget_context():
    kernel = EthicalKernel(llm_mode="local")

    # Add multiple episodes
    kernel.process(
        scenario="p1",
        place="city",
        signals={},
        context="private",
        actions=[CandidateAction("a", "a", 0.5)],
    )
    kernel.process(
        scenario="p2",
        place="city",
        signals={},
        context="private",
        actions=[CandidateAction("a", "a", 0.5)],
    )
    kernel.process(
        scenario="p3",
        place="city",
        signals={},
        context="public",
        actions=[CandidateAction("a", "a", 0.5)],
    )

    assert len(kernel.memory.episodes) >= 3

    # Forget all 'private'
    deleted_count = kernel.amnesia.forget_context("private")
    assert deleted_count >= 2

    # Verify remaining
    assert all(ep.context != "private" for ep in kernel.memory.episodes)
    assert any(ep.context == "public" for ep in kernel.memory.episodes)
