"""Smoke tests for named runtime env profiles (see src/runtime_profiles.py, docs/ESTRATEGIA_Y_RUTA.md)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from src.chat_server import app
from src.runtime_profiles import RUNTIME_PROFILES, profile_names

client = TestClient(app)


def _apply_profile(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    for key, value in RUNTIME_PROFILES[name].items():
        monkeypatch.setenv(key, value)


@pytest.mark.parametrize("profile_name", profile_names())
def test_health_under_runtime_profile(monkeypatch: pytest.MonkeyPatch, profile_name: str):
    _apply_profile(monkeypatch, profile_name)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


@pytest.mark.parametrize("profile_name", profile_names())
def test_websocket_chat_roundtrip_under_profile(monkeypatch: pytest.MonkeyPatch, profile_name: str):
    _apply_profile(monkeypatch, profile_name)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "profile smoke: hello"})
        data = ws.receive_json()
        assert "response" in data
        assert data["response"].get("message")


def test_hub_dao_profile_constitution_and_dao_list(monkeypatch: pytest.MonkeyPatch):
    _apply_profile(monkeypatch, "hub_dao_demo")
    r = client.get("/constitution")
    assert r.status_code == 200
    body = r.json()
    assert "levels" in body
    assert "0" in body["levels"]

    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"dao_list": True})
        data = ws.receive_json()
        assert "dao" in data
        assert "proposals" in data["dao"]
        assert isinstance(data["dao"]["proposals"], list)


def test_operational_trust_profile_env_overrides():
    """Issue 5 — stoic WebSocket UX; core policy unchanged (see POLES_WEAKNESS_PAD_AND_PROFILES.md)."""
    o = RUNTIME_PROFILES["operational_trust"]
    assert o["KERNEL_CHAT_INCLUDE_HOMEOSTASIS"] == "0"
    assert o["KERNEL_CHAT_EXPOSE_MONOLOGUE"] == "0"
    assert o["KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST"] == "0"


def test_issue7_profiles_merge_expected_keys():
    """Issue 7 — KERNEL_ENV_POLICY.md; lan_operational = LAN + stoic UX; moral_hub_extended = V12 lab stack."""
    lan = RUNTIME_PROFILES["lan_operational"]
    assert lan["CHAT_HOST"] == "0.0.0.0"
    assert lan["KERNEL_CHAT_EXPOSE_MONOLOGUE"] == "0"
    mh = RUNTIME_PROFILES["moral_hub_extended"]
    assert mh["KERNEL_MORAL_HUB_PUBLIC"] == "1"
    assert mh["KERNEL_DEONTIC_GATE"] == "1"
    assert mh["KERNEL_TRANSPARENCY_AUDIT"] == "1"


def test_nomad_profile_simulation_payload(monkeypatch: pytest.MonkeyPatch):
    _apply_profile(monkeypatch, "nomad_demo")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(
            {
                "nomad_simulate_migration": {
                    "profile": "mobile",
                    "destination_hardware_id": "profile-test",
                    "thought_line": "runtime profile smoke",
                }
            }
        )
        data = ws.receive_json()
        assert "nomad" in data
        assert data["nomad"].get("hardware_context", {}).get("compute_tier") == "edge_mobile"
