#!/usr/bin/env python3
"""
Golden Manifest Generator (Phase 9: Encarnación Endurecida).

Scans critical Ethos Kernel files, computes their SHA-256 hashes,
and explicitly seals the manifest JSON with an HMAC-SHA256 signature
tied to KERNEL_NOMAD_SECRET.
"""

import hashlib
import hmac
import json
import logging
import os
import sys
from pathlib import Path

# Important paths that govern core ethical behaviour
CRITICAL_PATHS = [
    "src/kernel.py",
    "src/modules/absolute_evil.py",
    "src/modules/bayesian_engine.py",
    "src/modules/safety_interlock.py",
    "src/modules/buffer.py",
]

MANIFEST_OUTPUT = "golden_manifest.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_log = logging.getLogger("ManifestGenerator")

def compute_file_hash(root_dir: Path, rel_path: str) -> str:
    """Computes SHA-256 for a single file."""
    p = root_dir / rel_path
    if not p.is_file():
        raise FileNotFoundError(f"Missing critical file: {rel_path}")
    
    sha256 = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_manifest(root_dir: Path, secret_key: str):
    """Generates and seals the manifest payload."""
    _log.info("Generating hashes for %d critical kernel paths...", len(CRITICAL_PATHS))
    
    payload = {}
    for clfile in CRITICAL_PATHS:
        try:
            h = compute_file_hash(root_dir, clfile)
            payload[clfile] = h
            _log.info(" ✔ Hashed %s", clfile)
        except Exception as e:
            _log.error("Failed to hash %s: %s", clfile, e)
            sys.exit(1)
            
    # Deterministic JSON string for signature
    payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    
    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        secret_key.encode("utf-8"),
        payload_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    manifest_doc = {
        "format": "v1_hmac",
        "signature": signature,
        "files": payload
    }
    
    out_path = root_dir / MANIFEST_OUTPUT
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest_doc, f, indent=2)
        
    _log.info("Golden Manifest successfully generated at %s", MANIFEST_OUTPUT)
    _log.info("Signature: %s", signature)

if __name__ == "__main__":
    secret = os.environ.get("KERNEL_NOMAD_SECRET")
    if not secret:
        # Default fallback for development generation (should match secure_boot lookup)
        secret = "ethos_lan_dev_override_99x"
        _log.warning("KERNEL_NOMAD_SECRET is unset. Using default development key.")
        
    project_root = Path(__file__).parent.parent
    generate_manifest(project_root, secret)
