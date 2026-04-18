"""Shared pytest fixtures for kernel tests."""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def clear_narrative_db(monkeypatch, tmp_path):
    """Clear narrative database before each test to prevent state pollution.

    Uses a temporary database path for each test, ensuring clean state.
    """
    db_path = tmp_path / "narrative_test.db"
    monkeypatch.setenv("KERNEL_NARRATIVE_DB_PATH", str(db_path))

    # Ensure the directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup after test
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            pass


@pytest.fixture(autouse=True)
def reset_audit_trail(monkeypatch, tmp_path):
    """Reset audit trail database before each test."""
    audit_path = tmp_path / "audit_test.db"
    monkeypatch.setenv("KERNEL_AUDIT_DB_PATH", str(audit_path))

    yield

    if audit_path.exists():
        try:
            audit_path.unlink()
        except Exception:
            pass
