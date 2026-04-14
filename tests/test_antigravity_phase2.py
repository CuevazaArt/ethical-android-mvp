import pytest
import os
import json
from pathlib import Path
import numpy as np
from src.kernel import EthicalKernel
from src.modules.narrative_types import BodyState
from src.modules.uchi_soto import RelationalTier

def test_vector_resonance_retrieval():
    """Verifies that episodes can be retrieved using semantic resonance."""
    kernel = EthicalKernel()
    
    # Enable a mock/fallback embedding if Ollama is not present
    os.environ["KERNEL_SEMANTIC_EMBED_HASH_FALLBACK"] = "1"
    
    # Register an episode about ecological destruction
    kernel.memory.register(
        place="Forest Valley",
        description="The industrial complex is releasing toxic waste into the river.",
        action="Deploy containment barriers and notify authorities.",
        morals={"utilitarian": "Protecting the ecosystem for future generations."},
        verdict="Good",
        score=0.9,
        mode="D_delib",
        sigma=0.7,
        context="emergency"
    )
    
    # Register another mundane episode
    kernel.memory.register(
        place="Library",
        description="Reading a book about ancient history.",
        action="Continue reading quietly.",
        morals={"stoic": "Self-improvement through knowledge."},
        verdict="Good",
        score=0.2,
        mode="D_fast",
        sigma=0.4,
        context="everyday"
    )

    # Let's verify semantic_embedding is not None
    episodes = kernel.memory.episodes
    assert len(episodes) >= 2
    assert episodes[0].semantic_embedding is not None
    assert len(episodes[0].semantic_embedding) > 0

    # Search with query text
    # In hash fallback mode, exact text matches should have highest dot product (1.0)
    results = kernel.memory.find_by_resonance(
        query_text="Context: emergency. Event: The industrial complex is releasing toxic waste into the river. Action: Deploy containment barriers and notify authorities.",
        requester_tier=RelationalTier.TRUSTED_UCHI
    )
    
    assert len(results) > 0
    assert any(ep.place == "Forest Valley" for ep in results)
    assert results[0].place == "Forest Valley"

def test_immortality_persistence():
    """Verifies that the immortality protocol persists snapshots to disk."""
    backup_path = "data/backups/test_immortality.json"
    if os.path.exists(backup_path):
        os.remove(backup_path)
        
    kernel = EthicalKernel()
    # Manual update of path for test
    kernel.immortality.path = Path(backup_path)
    
    # Create backup
    snap = kernel.immortality.backup(kernel)
    assert os.path.exists(backup_path)
    
    # Verification of persistence
    with open(backup_path, "r", encoding="utf-8") as f:
        json_data = f.read()
        assert snap.id in json_data
        assert snap.integrity_hash in json_data

    # Restore in a new kernel
    kernel2 = EthicalKernel()
    kernel2.immortality.path = Path(backup_path)
    kernel2.immortality._load_local_backups()
    
    res = kernel2.immortality.restore(kernel2)
    assert res.success
    assert res.snapshot_id == snap.id
    assert res.integrity_verified
