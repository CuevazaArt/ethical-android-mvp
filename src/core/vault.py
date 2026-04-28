# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Ethos Core — Secure Vault (V2.70)

A highly restricted, encrypted storage module for sensitive PII,
passwords, API keys, and personal directives.
This data is explicitly EXCLUDED from episodic memory and context windows,
and is only injected ephemerally when a specific tool call is authorized.
"""

import json
import logging
import os
from pathlib import Path

_log = logging.getLogger(__name__)


class SecureVault:
    """
    Manages sensitive user data.
    In production, this should wrap AES-256 encryption via OS Keychain.
    For V2.70, we implement the strict isolation boundary.
    """

    DEFAULT_PATH = str(Path.home() / ".ethos" / "vault.json")

    def __init__(self, storage_path: str | None = None):
        self._path = storage_path or os.environ.get(
            "ETHOS_VAULT_PATH", self.DEFAULT_PATH
        )
        self._store: dict[str, str] = {}
        self._is_unlocked = False
        self._load()

    def _load(self) -> None:
        """Loads the vault. Simulates decryption step."""
        try:
            p = Path(self._path)
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    self._store = json.load(f)
        except Exception as e:
            _log.warning("Could not load SecureVault: %s", e)
            self._store = {}

    def _save(self) -> None:
        """Saves the vault. Simulates encryption step."""
        p = Path(self._path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self._store, f, indent=2)

    def unlock(self, auth_token: str) -> bool:
        """
        Simulates biometric or token-based unlock.
        In a real scenario, auth_token is the decryption key.
        """
        # Stub for V2.70
        self._is_unlocked = True
        return True

    def lock(self) -> None:
        """Lock the vault immediately after use to minimize exposure window."""
        self._is_unlocked = False

    def get_secret(self, key: str, reason: str) -> str | None:
        """
        Retrieve a secret.
        Requires an explicit 'reason' for audit logging.
        """
        if not self._is_unlocked:
            _log.warning(
                "SECURITY ALERT: Attempted to read vault while locked (key: %s)", key
            )
            return None

        _log.info("VAULT ACCESS: Granted read for '%s'. Reason: %s", key, reason)
        return self._store.get(key)

    def set_secret(self, key: str, value: str) -> bool:
        """Store a new secret securely."""
        if not self._is_unlocked:
            return False

        self._store[key] = value
        self._save()
        _log.info("VAULT WRITE: Stored new secret for '%s'", key)
        return True

    def list_keys(self) -> list[str]:
        """Return available keys without exposing values, so the LLM knows what to ask for."""
        return list(self._store.keys())
