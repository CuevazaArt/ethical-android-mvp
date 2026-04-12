"""EthicalKernel dependency injection: LLM module and checkpoint persistence ports."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.llm_layer import LLMModule, resolve_llm_mode
from src.persistence.checkpoint import (
    checkpoint_persistence_from_env,
    should_load_checkpoint,
    should_save_on_disconnect,
    try_load_checkpoint,
    try_save_checkpoint,
)
from src.persistence.checkpoint_adapters import JsonFileCheckpointAdapter, SqliteCheckpointAdapter


def test_checkpoint_persistence_from_env_matches_path(tmp_path, monkeypatch):
    monkeypatch.setenv("KERNEL_CHECKPOINT_PATH", str(tmp_path / "x.json"))
    adapter = checkpoint_persistence_from_env()
    assert adapter is not None
    monkeypatch.delenv("KERNEL_CHECKPOINT_PATH", raising=False)
    assert checkpoint_persistence_from_env() is None


def test_injected_llm_instance_used():
    custom = LLMModule(mode=resolve_llm_mode("local"))
    k = EthicalKernel(variability=False, llm=custom)
    assert k.llm is custom


def test_json_checkpoint_adapter_without_env_path(tmp_path, monkeypatch):
    monkeypatch.delenv("KERNEL_CHECKPOINT_PATH", raising=False)
    path = tmp_path / "ckpt.json"
    adapter = JsonFileCheckpointAdapter(path)
    k = EthicalKernel(variability=False, checkpoint_persistence=adapter)
    assert should_save_on_disconnect(k) is True
    assert should_load_checkpoint(k) is True
    assert try_save_checkpoint(k) is True
    assert path.is_file()
    k2 = EthicalKernel(variability=False, checkpoint_persistence=adapter)
    assert try_load_checkpoint(k2) is True


def test_sqlite_checkpoint_adapter_roundtrip(tmp_path, monkeypatch):
    monkeypatch.delenv("KERNEL_CHECKPOINT_PATH", raising=False)
    db = tmp_path / "k.db"
    adapter = SqliteCheckpointAdapter(db)
    k = EthicalKernel(variability=False, checkpoint_persistence=adapter)
    assert try_save_checkpoint(k) is True
    assert db.is_file()
    k2 = EthicalKernel(variability=False, checkpoint_persistence=adapter)
    assert try_load_checkpoint(k2) is True
