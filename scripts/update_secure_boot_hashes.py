"""
Update Secure Boot Golden Manifest (SHA-256 + HMAC-SHA256).
Run this as L1/L0 when critical kernel files are intentionally modified.
"""
import hashlib
import hmac
import json
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
    "src/modules/multimodal_trust.py",
    "src/modules/buffer.py",
    "src/modules/generative_candidates.py",
    "src/persistence/kernel_io.py",
    "src/persistence/snapshot_serde.py",
]

ROT_ANCHOR_BIAS = bytes.fromhex("4a75616e5f43756576617a615f4c657861725f4c30")

def compute_file_hash(root: Path, rel_path: str) -> str:
    path = root / rel_path
    if not path.exists():
        return "missing"
    sha = hashlib.sha256()
    sha.update(ROT_ANCHOR_BIAS)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

def update_manifest():
    root = Path(".")
    secret = os.environ.get("KERNEL_NOMAD_SECRET", "ethos_lan_dev_override_99x")
    
    # Files map
    files_map = {}
    for p in CRITICAL_PATHS:
        h = compute_file_hash(root, p)
        if h != "missing":
            files_map[p] = h
        else:
            print(f"[!] Warning: {p} is missing.")

    # Sort keys for consistent HMAC
    payload_str = json.dumps(files_map, sort_keys=True, separators=(",", ":"))
    signature = hmac.new(
        secret.encode("utf-8"),
        payload_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    manifest_doc = {
        "files": files_map,
        "signature": signature,
        "signed_by": "Antigravity (L1) - Hardening Pulse Recovery"
    }

    # Write to both target paths used by secure_boot.py
    for target in [root / "src/MANIFEST.json", root / "golden_manifest.json"]:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(manifest_doc, f, indent=2)
        print(f"[*] Manifest updated: {target}")

if __name__ == "__main__":
    update_manifest()
