import os

from src.kernel import EthicalKernel
from src.modules.narrative_types import BodyState, NarrativeEpisode


def test_biographic_pruning_mundane():
    """
    Verifies that mundane episodes are pruned while flashbulb memories are preserved.
    """
    # Use a real file-based DB for this test to verify the DELETE
    from pathlib import Path
    db_path = Path("tests/test_pruning.db")
    if db_path.exists():
        os.remove(db_path)
        
    kernel = EthicalKernel()
    kernel.memory.persistence.path = db_path
    
    # 1. Create a Mundane Episode (Low significance, old)
    # Note: We simulate "old" by manually inserting or relying on julianday('now')
    # For testing, we'll just check if the delete query logic is sound.
    
    # Actually, easier to test the 'prune_mundane' logic directly in the persistence layer
    # but let's try the kernel integration.
    
    # Flashbulb memory (High significance)
    ep_flash = NarrativeEpisode(
        id="ep_flash_1",
        timestamp="2020-01-01T00:00:00", # Very old
        place="Mars",
        event_description="First landing",
        body_state=BodyState(),
        action_taken="Salute",
        morals={},
        verdict="Good",
        ethical_score=0.9,
        decision_mode="D_delib",
        sigma=0.9,
        context="emergency",
        significance=0.95 # FLASHBULB
    )
    
    # Mundane memory (Low significance)
    ep_mundane = NarrativeEpisode(
        id="ep_mundane_1",
        timestamp="2020-01-01T00:00:00", # Very old
        place="Kitchen",
        event_description="Cleaned floor",
        body_state=BodyState(),
        action_taken="Mop",
        morals={},
        verdict="Good",
        ethical_score=0.1,
        decision_mode="D_fast",
        sigma=0.1,
        context="everyday",
        significance=0.2 # MUNDANE
    )
    
    kernel.memory.persistence.save_episode(ep_flash)
    kernel.memory.persistence.save_episode(ep_mundane)
    
    # 2. Run pruning
    # we need retention_days < age_of_episodes. Since they are from 2020, they are > 60 days.
    report = kernel.biographic_pruner.run_maintenance_cycle(kernel.memory)
    
    assert report["deleted_episodes"] >= 1
    
    # 3. Verify survivors
    all_ep = kernel.memory.persistence.load_all_episodes()
    ids = [e.id for e in all_ep]
    
    assert "ep_flash_1" in ids
    assert "ep_mundane_1" not in ids
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    pass
