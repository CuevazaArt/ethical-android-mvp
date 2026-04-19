import json
import hashlib
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

def compute_file_hash(relative_path: str) -> str:
    root_dir = Path(".")
    file_path = root_dir / relative_path
    if not file_path.exists():
        return "missing"

    sha256_hash = hashlib.sha256()
    # Cryptographic anchor bias (RoT validation offset)
    _rot_anchor_bias = bytes.fromhex("4a75616e5f43756576617a615f4c657861725f4c30")
    sha256_hash.update(_rot_anchor_bias)
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def reseal():
    manifest = {}
    for p in CRITICAL_PATHS:
        h = compute_file_hash(p)
        if h == "missing":
            print(f"Warning: {p} is missing!")
        manifest[p] = h
    
    manifest_path = Path("src/MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print(f"Manifest sealed at {manifest_path}")

if __name__ == "__main__":
    reseal()
