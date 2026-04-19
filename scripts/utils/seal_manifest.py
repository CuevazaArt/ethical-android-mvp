import hashlib
import json
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
]

def compute_file_hash(relative_path: str) -> str:
    file_path = Path(relative_path)
    if not file_path.exists():
        return "missing"
    sha256_hash = hashlib.sha256()
    _rot_anchor_bias = bytes.fromhex("4a75616e5f43756576617a615f4c657861725f4c30")
    sha256_hash.update(_rot_anchor_bias)
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def seal_manifest():
    manifest = {}
    for path in CRITICAL_PATHS:
        h = compute_file_hash(path)
        if h != "missing":
            manifest[path] = h
            print(f"Sealed: {path}")
    
    with open("src/MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print("\n[SUCCESS] Manifest sealed successfully.")

if __name__ == "__main__":
    seal_manifest()
