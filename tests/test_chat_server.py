"""HTTP + WebSocket smoke tests for src/chat_server.py."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from src.chat_server import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_constitution_404_when_moral_hub_public_off():
    r = client.get("/constitution")
    assert r.status_code == 404


def test_constitution_200_when_moral_hub_public_on(monkeypatch):
    monkeypatch.setenv("KERNEL_MORAL_HUB_PUBLIC", "1")
    r = client.get("/constitution")
    assert r.status_code == 200
    body = r.json()
    assert "levels" in body
    assert "0" in body["levels"]


def test_root_lists_websocket():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("websocket") == "/ws/chat"
    assert "constitution" in body


def test_root_protocol_mentions_multimodal_and_sensor_fields():
    r = client.get("/")
    proto = (r.json().get("protocol") or "").lower()
    assert "multimodal" in proto
    assert "vitality" in proto
    assert "guardian" in proto
    assert "epistemic" in proto
    assert "audio_emergency" in proto or "sensor" in proto


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
        assert "multimodal_trust" in data
        assert data["multimodal_trust"].get("state") in ("aligned", "doubt", "no_claim")
        assert "vitality" in data
        assert "is_critical" in data["vitality"]
        assert "critical_threshold" in data["vitality"]
        assert "guardian_mode" in data
        assert data["guardian_mode"] is False
        assert "epistemic_dissonance" in data
        assert data["epistemic_dissonance"]["active"] is False
        assert "decision" in data
        assert data["decision"].get("chosen_action_source") == "builtin"


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


def test_websocket_sensor_preset_env(monkeypatch):
    """KERNEL_SENSOR_PRESET merges with optional client sensor (v8)."""
    monkeypatch.setenv("KERNEL_SENSOR_PRESET", "hostile_soto")
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Ping with preset only.", "sensor": {"battery_level": 0.9}})
        data = ws.receive_json()
        assert "response" in data
        assert data.get("path") in ("light", "heavy", "safety_block", "kernel_block")


@pytest.mark.parametrize(
    "env_key,env_val,absent_key",
    [
        ("KERNEL_CHAT_INCLUDE_MULTIMODAL", "0", "multimodal_trust"),
        ("KERNEL_CHAT_INCLUDE_USER_MODEL", "0", "user_model"),
        ("KERNEL_CHAT_INCLUDE_CHRONO", "0", "chronobiology"),
        ("KERNEL_CHAT_INCLUDE_PREMISE", "0", "premise_advisory"),
        ("KERNEL_CHAT_INCLUDE_TELEOLOGY", "0", "teleology_branches"),
        ("KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST", "0", "experience_digest"),
        ("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", "0", "affective_homeostasis"),
        ("KERNEL_CHAT_INCLUDE_VITALITY", "0", "vitality"),
        ("KERNEL_CHAT_INCLUDE_GUARDIAN", "0", "guardian_mode"),
        ("KERNEL_CHAT_INCLUDE_EPISTEMIC", "0", "epistemic_dissonance"),
    ],
)
def test_websocket_kernel_chat_json_env_matrix(monkeypatch, env_key, env_val, absent_key):
    """Regression: each KERNEL_CHAT_* toggle omits the expected JSON key without crashing."""
    monkeypatch.setenv(env_key, env_val)
    with client.websocket_connect("/ws/chat") as ws:
        ws.send_json({"text": "Hello, env matrix regression test."})
        data = ws.receive_json()
    assert "response" in data
    assert absent_key not in data
