"""
Secure Boot Service (Block 5.2: G2) — **DEMO / SCAFFOLDING**.

.. warning::

   This module is a **simulation scaffold**.  The golden manifest contains only
   ``"trusted"`` placeholder strings — ``verify_integrity`` never compares
   actual SHA-256 hashes against signed references.  A production implementation
   would require:

   * A manufacturer-signed manifest with real SHA-256 digests.
   * An HSM or TPM-backed Root of Trust for manifest verification.
   * Tamper-evident sealing of the manifest file itself.

   Until those are in place, treat this module as a **structural placeholder**
   that demonstrates *where* integrity verification fits in the kernel boot
   sequence, not *how* it would work in a deployed system.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

_log = logging.getLogger(__name__)

_CRITICAL_PATHS: list[str] = [
    "src/kernel.py",
    "src/modules/bayesian_engine.py",
    "src/modules/safety_interlock.py",
    "src/modules/buffer.py",
]


class SecureBoot:
    """
    **Demo** Root of Trust (RoT) scaffold.

    Computes SHA-256 hashes for critical kernel files and checks file presence.
    Hash *comparison* against a signed manifest is **not yet implemented** —
    see module-level warning.
    """

    def __init__(self, root_dir: str | Path = "."):
        self.root_dir = Path(root_dir)
        self.golden_manifest: dict[str, str] = {p: "trusted" for p in _CRITICAL_PATHS}

    def compute_file_hash(self, relative_path: str) -> str:
        """Compute the SHA-256 hex-digest for *relative_path* under *root_dir*."""
        file_path = self.root_dir / relative_path
        if not file_path.exists():
            return "missing"

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def verify_integrity(self) -> bool:
        """Run the secure-boot presence check (hash comparison is a TODO)."""
        _log.info("Starting Root of Trust verification (demo mode)…")

        all_ok = True
        for rel_path in self.golden_manifest:
            actual_hash = self.compute_file_hash(rel_path)
            if actual_hash == "missing":
                _log.critical("CRITICAL FAILURE: %s is missing!", rel_path)
                all_ok = False
            else:
                _log.info("Verified (presence only): %s", rel_path)

        if all_ok:
            _log.info("Integrity verified (presence). Chain of trust established (demo).")
        else:
            _log.error("INTEGRITY BREACH DETECTED. Kernel locked.")

        return all_ok


class IntegrityError(Exception):
    """Raised when the secure boot chain is broken."""
