"""
Validation script for ChromaDB persistence in Ethos Kernel.
Ensures that anchors are saved to the .chroma/ directory and can be reloaded.
"""

import os
import shutil
import numpy as np
import logging
from src.modules.semantic_anchor_store import create_anchor_store

logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)

def test_chroma_persistence():
    test_path = ".chroma_test/"
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    
    _log.info(f"--- Testing Chroma Persistence at {test_path} ---")
    
    # 1. Start store and insert
    store = create_anchor_store(backend="chroma", persist_path=test_path)
    dummy_vec = np.random.rand(384).tolist()
    anchor_id = "test-anchor-1"
    anchor_text = "The quick brown fox jumps over the lazy dog."
    
    _log.info("Upserting test anchor...")
    store.upsert_anchor(
        id=anchor_id,
        text=anchor_text,
        embedding=dummy_vec,
        metadata={"category": "test", "importance": 0.9}
    )
    
    # Explicitly close or cleanup if needed (PersistentClient should handle it)
    del store
    
    # 2. Re-initialize and verify
    _log.info("Re-initializing store from path...")
    store2 = create_anchor_store(backend="chroma", persist_path=test_path)
    
    record = store2.get(anchor_id)
    if record is None:
        _log.error("FAIL: Anchor not found after reload!")
        return False
    
    if record.text != anchor_text:
        _log.error(f"FAIL: Text mismatch! Expected '{anchor_text}', got '{record.text}'")
        return False
    
    _log.info("Verifying similarity query...")
    neighbors = store2.query_neighbors(dummy_vec, k=1)
    if not neighbors or neighbors[0][0] != anchor_id:
        _log.error("FAIL: Neighbor query failed after reload!")
        return False
    
    similarity = neighbors[0][1]
    _log.info(f"Similarity score: {similarity:.4f}")
    
    if similarity < 0.99:
        _log.error("FAIL: Low similarity on identical vector!")
        return False

    _log.info("PASS: ChromaDB persistence verified.")
    
    # Cleanup
    shutil.rmtree(test_path)
    return True

if __name__ == "__main__":
    success = test_chroma_persistence()
    if not success:
        exit(1)
