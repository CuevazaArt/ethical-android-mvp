"""
Pytest defaults for Ethos V2 Core Minimal.
Isolates tests from production defaults and provides shared fixtures.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Core environment defaults for tests
os.environ.setdefault("KERNEL_ENV_VALIDATION", "warn")
os.environ.setdefault("KERNEL_IGNORE_BOOT_FAILURE", "1")
os.environ.setdefault("KERNEL_SEMANTIC_CHAT_GATE", "0")

@pytest.fixture(autouse=True)
def _test_env_isolation(monkeypatch, tmp_path):
    """Isolate memory and identity paths for each test."""
    monkeypatch.setenv("ETHOS_MEMORY_PATH", str(tmp_path / "test_memory.json"))
    monkeypatch.setenv("KERNEL_AUDIT_DB_PATH", str(tmp_path / "test_audit.db"))

@pytest.fixture
def engine():
    """Shared ChatEngine fixture for integration tests."""
    from src.core.chat import ChatEngine
    from src.core.memory import Memory
    
    # Use a temp file for memory to avoid conflicts
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name
    
    mem = Memory(storage_path=tmp_path)
    mem.clear()
    e = ChatEngine(memory=mem)
    yield e
    
    if os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
        except OSError:
            pass

@pytest.fixture
def mock_ollama():
    """Mock for OllamaClient to avoid real HTTP calls."""
    mock = AsyncMock()
    mock.is_available = AsyncMock(return_value=True)
    mock.chat = AsyncMock(return_value="Respuesta de prueba")
    mock.chat_stream = AsyncMock()
    mock.extract_json = AsyncMock(return_value={})
    return mock

@pytest.fixture
def mock_stt():
    """Mock for STT service."""
    mock = AsyncMock()
    mock.is_available = AsyncMock(return_value=True)
    mock.transcribe = AsyncMock(return_value="Texto transcripto")
    return mock
