"""
Pytest defaults: isolate tests from production MalAbs defaults.

Production defaults (unset env): semantic MalAbs + hash embedding fallback are **on** — see
``semantic_chat_gate.semantic_chat_gate_env_enabled`` and ``semantic_embedding_client``.

Tests default to lexical-only MalAbs unless they enable semantic explicitly, so the suite stays
fast and deterministic without Ollama.

**KERNEL_* drift:** this isolation is intentional; CI defaults are not identical to an unset
production shell — see ``docs/proposals/README.md`` (Issue 7).
"""

from __future__ import annotations

import os
from pathlib import Path

# chat_server validates env at import time; production default is strict. Tests default to warn
# unless a case overrides KERNEL_ENV_VALIDATION so developer shells need not be perfect.
os.environ.setdefault("KERNEL_ENV_VALIDATION", "warn")

import pytest


@pytest.fixture(autouse=True)
def _malabs_test_env_isolation(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> None:
    # Use a temporary file for SQLite during tests to support multi-connection persistence
    # while maintaining isolation between test session runs.
    db_file = tmp_path_factory.mktemp("data") / "test_narrative.db"
    monkeypatch.setenv("KERNEL_NARRATIVE_DB_PATH", str(db_file))
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    monkeypatch.setenv("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", "0")


@pytest.fixture(autouse=True)
def _immortality_backup_isolation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Fresh immortality snapshot counter per test (avoids shared data/backups state)."""
    monkeypatch.setenv("KERNEL_IMMORTALITY_BACKUP_PATH", str(tmp_path / "immortality.json"))
