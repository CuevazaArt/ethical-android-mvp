import hashlib
import json
from pathlib import Path

_CRITICAL_PATHS = [
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

# Must match ``SecureBoot.compute_file_hash`` in ``src/modules/secure_boot.py`` (RoT anchor prefix).
_ROT_ANCHOR_BIAS = bytes.fromhex("4a75616e5f43756576617a615f4c657861725f4c30")


def compute_hash(path: Path) -> str:
    sha256 = hashlib.sha256()
    sha256.update(_ROT_ANCHOR_BIAS)
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()

def main():
    manifest = {}
    root = Path(".")
    for rel_path in _CRITICAL_PATHS:
        full_path = root / rel_path
        if full_path.exists():
            manifest[rel_path] = compute_hash(full_path)
            print(f"Hashed: {rel_path}")
        else:
            print(f"Warning: {rel_path} not found!")
    
    with open("src/MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print("Manifest saved to src/MANIFEST.json")

if __name__ == "__main__":
    main()
