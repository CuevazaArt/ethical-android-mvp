"""
Secure Boot Manifest Generator
Usage: python scripts/generate_secure_boot_manifest.py
Seals the current state of src/ into src/MANIFEST.json.
"""

import json
import hashlib
import os
from pathlib import Path

CRITICAL_PATHS = [
    "src/kernel.py",
    "src/kernel_lobes/models.py",
    "src/kernel_lobes/executive_lobe.py",
    "src/kernel_lobes/memory_lobe.py",
    "src/kernel_lobes/perception_lobe.py",
    "src/kernel_lobes/thalamus_node.py",
    "src/modules/absolute_evil.py",
    "src/modules/nomad_bridge.py",
    "src/modules/secure_boot.py",
    "src/modules/immortality.py",
    "src/modules/bayesian_engine.py",
    "src/modules/weighted_ethics_scorer.py",
    "src/modules/semantic_chat_gate.py",
    "src/modules/uchi_soto.py",
    "src/modules/sympathetic.py",
    "src/persistence/kernel_io.py",
    "src/persistence/snapshot_serde.py",
]

def compute_hash(path: Path) -> str:
    sha256 = hashlib.sha256()
    # RO-T Anchor Bias (consistent with src/modules/secure_boot.py)
    _rot_anchor_bias = bytes.fromhex("4a75616e5f43756576617a615f4c657861725f4c30")
    sha256.update(_rot_anchor_bias)
    
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()

def main():
    root = Path(".")
    manifest = {}
    
    print("Locked files for Secure Boot:")
    for rel_path in CRITICAL_PATHS:
        full_path = root / rel_path
        if full_path.exists():
            h = compute_hash(full_path)
            manifest[rel_path] = h
            print(f"  [SEALED] {rel_path}: {h[:16]}...")
        else:
            print(f"  [ERROR]  {rel_path}: NOT FOUND")
            
    manifest_path = root / "src" / "MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"\nManifest written to {manifest_path}")
    print("Hardware Trust chain established (Simulated).")

if __name__ == "__main__":
    main()
