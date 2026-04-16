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
import json
import logging
from pathlib import Path

_log = logging.getLogger(__name__)

_CRITICAL_PATHS: list[str] = [
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


class SecureBoot:
    """
    **Demo** Root of Trust (RoT) scaffold.

    Computes SHA-256 hashes for critical kernel files and checks file presence.
    Hash *comparison* against a signed manifest is **not yet implemented** —
    see module-level warning.
    """

    def __init__(self, root_dir: str | Path = "."):
        self.root_dir = Path(root_dir)
        self.manifest_path = self.root_dir / "src" / "MANIFEST.json"
        self.golden_manifest: dict[str, str] = {}
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Carga el manifiesto sellado desde el disco."""
        if not self.manifest_path.exists():
            _log.warning("SecureBoot: MANIFEST.json not found at %s. Running in UNSAFE mode.", self.manifest_path)
            # Fallback to presence only for first boot
            self.golden_manifest = {p: "presence_only" for p in _CRITICAL_PATHS}
            return

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                self.golden_manifest = json.load(f)
            _log.info("SecureBoot: Manifest loaded with %d critical entries.", len(self.golden_manifest))
        except Exception as e:
            _log.error("SecureBoot: Failed to parse manifest: %s", e)
            self.golden_manifest = {p: "presence_only" for p in _CRITICAL_PATHS}

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
        """
        Ejecuta la validación de integridad (Bloque 5.2.G2).
        Compara los hashes SHA-256 actuales contra los del manifiesto sellado.
        """
        _log.info("SecureBoot: Initiating Root of Trust verification...")

        all_ok = True
        violations = []

        for rel_path, expected_hash in self.golden_manifest.items():
            actual_hash = self.compute_file_hash(rel_path)
            
            if actual_hash == "missing":
                _log.critical("SECURE BOOT FAILURE: %s is missing!", rel_path)
                violations.append(f"{rel_path}: MISSING")
                all_ok = False
            elif expected_hash == "presence_only":
                 _log.warning("SecureBoot: %s verified by presence (HASH PENDING).", rel_path)
            elif actual_hash != expected_hash:
                _log.critical("SECURE BOOT FAILURE: %s hash mismatch!", rel_path)
                _log.debug("Expected: %s | Actual: %s", expected_hash, actual_hash)
                violations.append(f"{rel_path}: TAMPERED")
                all_ok = False
            else:
                _log.info("SecureBoot: %s verified (HASH MATCH).", rel_path)

        if all_ok:
            _log.info("SecureBoot: Chain of trust established. Integrity verified.")
        else:
            _log.error("INTEGRITY BREACH DETECTED: %d violations.", len(violations))

        return all_ok


class IntegrityError(Exception):
    """Raised when the secure boot chain is broken."""
