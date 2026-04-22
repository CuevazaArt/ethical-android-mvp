"""
Massive asynchronous load tests for persistence locking (Module 8).
Verifies that concurrent writes to the same SQLite file do not cause 'database is locked' errors.
"""

import asyncio
import os
import time
from pathlib import Path

import pytest
from src.modules.narrative_types import BodyState, NarrativeEpisode
from src.persistence.narrative_storage import NarrativePersistence


@pytest.mark.asyncio
async def test_concurrent_narrative_writes():
    """Simulate multiple concurrent tasks writing to the same narrative DB."""
    db_path = Path("tests/concurrent_audit_test.db")
    if db_path.exists():
        os.remove(db_path)

    storage = NarrativePersistence(db_path)

    tasks = []
    num_tasks = 50

    def create_episode(i):
        return NarrativeEpisode(
            id=f"ep_{i}",
            timestamp=f"2026-04-18T12:00:{i:02d}",
            place="Test Lab",
            event_description=f"Concurrent event {i}",
            body_state=BodyState(1.0, 8, True, "OK"),
            action_taken="LOG",
            morals={},
            verdict="Neutral",
            ethical_score=0.5,
            decision_mode="D_fast",
            sigma=0.0,
            context="everyday",
        )

    async def worker(i):
        # Heavy write operation
        storage.save_episode(create_episode(i))
        # Ensure some overlap
        await asyncio.sleep(0.01)
        # Attempt a read immediately
        all_ep = storage.load_all_episodes()
        assert len(all_ep) > 0

    print(f"\n[Bench] Starting {num_tasks} concurrent storage tasks...")
    start_time = time.time()
    for i in range(num_tasks):
        tasks.append(worker(i))

    await asyncio.gather(*tasks)
    end_time = time.time()

    final_count = len(storage.load_all_episodes())
    print(f"[Bench] Completed in {end_time - start_time:.2f}s. Final count: {final_count}")

    assert final_count == num_tasks
    if db_path.exists():
        os.remove(db_path)
