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
