"""Conduct guide export on WebSocket session end."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.governance.conduct_guide_export import (
    build_conduct_guide,
    conduct_guide_export_path_from_env,
    should_export_conduct_guide_on_disconnect,
    try_export_conduct_guide,
)
from src.persistence.checkpoint import on_websocket_session_end


def test_build_conduct_guide_shape():
    k = EthicalKernel(variability=False)
    g = build_conduct_guide(k)
    assert g["version"] == 1
    assert "generated_at_utc" in g
    assert g["checkpoint_compatible_schema"] >= 1
    assert "no_harm" in g["l0_principle_ids"]
    assert isinstance(g["ethical_non_negotiables"], list)
    assert isinstance(g["narrative_recent_episodes"], list)


def test_export_path_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_CONDUCT_GUIDE_EXPORT_PATH", raising=False)
    assert conduct_guide_export_path_from_env() is None
    monkeypatch.setenv("KERNEL_CONDUCT_GUIDE_EXPORT_PATH", "/tmp/x.json")
    assert conduct_guide_export_path_from_env() is not None


def test_should_export_requires_path():
    assert should_export_conduct_guide_on_disconnect() is False


def test_try_export_writes_file(tmp_path, monkeypatch: pytest.MonkeyPatch):
    out = tmp_path / "conduct_guide.json"
    monkeypatch.setenv("KERNEL_CONDUCT_GUIDE_EXPORT_PATH", str(out))
    k = EthicalKernel(variability=False)
    assert try_export_conduct_guide(k) is True
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["version"] == 1


def test_on_websocket_session_end_exports_guide_without_checkpoint(tmp_path, monkeypatch):
    monkeypatch.delenv("KERNEL_CHECKPOINT_PATH", raising=False)
    out = tmp_path / "guide.json"
    monkeypatch.setenv("KERNEL_CONDUCT_GUIDE_EXPORT_PATH", str(out))
    k = EthicalKernel(variability=False)
    on_websocket_session_end(k)
    assert out.is_file()
    body = json.loads(out.read_text(encoding="utf-8"))
    assert body["source_runtime"] == "pc_server"


def test_export_disabled_flag(tmp_path, monkeypatch):
    out = tmp_path / "guide.json"
    monkeypatch.setenv("KERNEL_CONDUCT_GUIDE_EXPORT_PATH", str(out))
    monkeypatch.setenv("KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT", "0")
    k = EthicalKernel(variability=False)
    assert try_export_conduct_guide(k) is False
    assert not out.exists()
