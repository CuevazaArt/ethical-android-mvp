"""
Evidence Safe (Block 1.2: Encrypted Evidence and Anchoring).
Provides hashing and symmetric encryption for audit logs before off-chain storage or OGA anchoring.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

from cryptography.fernet import Fernet

_log = logging.getLogger(__name__)

DEFAULT_EVIDENCE_KEY_ENV = "KERNEL_EVIDENCE_KEY"


class EvidenceSafe:
    """
    Handles the preparation of 'Ethical Evidence' for the DAO.
    Ensures integrity (hashing) and privacy (encryption).
    """

    def __init__(self, fernet_key: str | None = None):
        # Fallback to env if not provided
        key = fernet_key or os.environ.get(DEFAULT_EVIDENCE_KEY_ENV, "")
        if not key:
            # Generate a transient key if none provided (not recommended for production persistence)
            self._fernet = Fernet(Fernet.generate_key())
            self._is_transient = True
        else:
            try:
                self._fernet = Fernet(key.encode("utf-8"))
                self._is_transient = False
            except (TypeError, ValueError) as exc:
                # Invalid key: operator-visible warning; do not fail closed (episodes still hash).
                _log.warning(
                    "KERNEL_EVIDENCE_KEY (or fernet_key) is invalid, using a transient key: %s",
                    exc,
                )
                self._fernet = Fernet(Fernet.generate_key())
                self._is_transient = True

    def hash_payload(self, payload: dict[str, Any]) -> str:
        """Computes a SHA-256 hash of the canonical JSON representation."""
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def encrypt_payload(self, payload: dict[str, Any]) -> bytes:
        """Encrypts the JSON payload for off-chain storage."""
        serialized = json.dumps(payload, sort_keys=True)
        return self._fernet.encrypt(serialized.encode())

    def decrypt_payload(self, token: bytes) -> dict[str, Any]:
        """Decrypts an evidence token back into a dictionary."""
        decrypted = self._fernet.decrypt(token)
        return json.loads(decrypted.decode())

    def prepare_anchoring_packet(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Builds a packet ready for the DAO.
        Includes the plain hash and the encrypted blob.
        """
        e_hash = self.hash_payload(payload)
        e_blob = self.encrypt_payload(payload)

        return {
            "evidence_hash": e_hash,
            "evidence_blob_b64": e_blob.decode(),  # base64 string for JSON compatibility
            "timestamp": payload.get("timestamp", 0.0),
            "episode_id": payload.get("episode_id", "0000"),
            "schema": "evidence_v1",
        }
