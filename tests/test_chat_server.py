"""HTTP + WebSocket smoke tests for src/chat_server.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from src.chat_server import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_root_lists_websocket():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("websocket") == "/ws/chat"


def test_websocket_chat_roundtrip():
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, I am testing the bridge."})
        data = ws.receive_json()
        assert "response" in data
        assert data["response"].get("message")
        assert data.get("path") in ("light", "heavy", "safety_block", "kernel_block")
        assert "identity" in data and "ascription" in data["identity"]
        assert "drive_intents" in data and isinstance(data["drive_intents"], list)
        assert "monologue" in data
        assert "affective_homeostasis" in data
        assert data["affective_homeostasis"].get("sigma") is not None
        assert "experience_digest" in data
        assert "user_model" in data
        assert "frustration_streak" in data["user_model"]
        assert "chronobiology" in data
        assert "turn_index" in data["chronobiology"]
        assert "premise_advisory" in data
        assert "flag" in data["premise_advisory"]
        assert "teleology_branches" in data
        assert "horizon_long_term" in data["teleology_branches"]


def test_websocket_homeostasis_omitted(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", "0")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, I am testing the bridge."})
        data = ws.receive_json()
        assert "affective_homeostasis" not in data


def test_websocket_invalid_json():
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_text("not-json")
        data = ws.receive_json()
        assert data.get("error") == "invalid_json"


def test_websocket_with_advisory_interval(monkeypatch):
    """Background advisory loop is optional; must not break chat lifecycle."""
    monkeypatch.setenv("KERNEL_ADVISORY_INTERVAL_S", "3600")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "ping"})
        data = ws.receive_json()
        assert "response" in data


def test_websocket_monologue_redacted(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_EXPOSE_MONOLOGUE", "0")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, I am testing the bridge."})
        data = ws.receive_json()
        assert data.get("monologue") == ""


def test_websocket_optional_sensor_v8():
    """Situated hints (v8) are optional; must not break the roundtrip."""
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json(
            {
                "text": "Hello with sensor hints.",
                "sensor": {
                    "battery_level": 0.5,
                    "place_trust": 0.9,
                    "backup_just_completed": False,
                },
            }
        )
        data = ws.receive_json()
        assert "response" in data
        assert data.get("path") in ("light", "heavy", "safety_block", "kernel_block")
