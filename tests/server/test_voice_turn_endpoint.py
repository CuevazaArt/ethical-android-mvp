"""V2.120 (A2): tests for the text-mediated voice_turn endpoint.

Validates the contract envelope (`DESKTOP_CONTRACT_SPINE_V1`) and the basic
happy/error paths without requiring a real LLM backend or TTS engine.
"""

from __future__ import annotations

import math
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from src.server.app import app
from src.server.desktop_voice_adapter import (
    CONTRACT_VERSION,
    VOICE_TURN_CONTRACT,
    parse_voice_turn_payload,
)


def _envelope(utterance: str) -> dict:
    return {
        "version": CONTRACT_VERSION,
        "contract": VOICE_TURN_CONTRACT,
        "request": {"utterance": utterance},
        "response": {},
        "error": None,
        "latency_ms": 0.0,
    }


def test_parse_voice_turn_rejects_non_dict() -> None:
    parsed, err = parse_voice_turn_payload("not a dict")
    assert parsed is None
    assert err is not None
    assert err.code == "INVALID_PAYLOAD"


def test_parse_voice_turn_rejects_wrong_version() -> None:
    parsed, err = parse_voice_turn_payload(
        {
            "version": "9.9",
            "contract": VOICE_TURN_CONTRACT,
            "request": {"utterance": "hi"},
        }
    )
    assert parsed is None
    assert err is not None
    assert err.code == "INVALID_VERSION"


def test_parse_voice_turn_rejects_wrong_contract() -> None:
    parsed, err = parse_voice_turn_payload(
        {
            "version": CONTRACT_VERSION,
            "contract": "audio_perception",
            "request": {"utterance": "hi"},
        }
    )
    assert parsed is None
    assert err is not None
    assert err.code == "INVALID_CONTRACT"


def test_parse_voice_turn_rejects_empty_utterance() -> None:
    parsed, err = parse_voice_turn_payload(_envelope("   "))
    assert parsed is None
    assert err is not None
    assert err.code == "EMPTY_UTTERANCE"


def test_parse_voice_turn_rejects_oversized_utterance() -> None:
    parsed, err = parse_voice_turn_payload(_envelope("x" * 5000))
    assert parsed is None
    assert err is not None
    assert err.code == "UTTERANCE_TOO_LONG"


def test_parse_voice_turn_accepts_valid_request() -> None:
    parsed, err = parse_voice_turn_payload(_envelope("hola"))
    assert err is None
    assert parsed is not None
    assert parsed.utterance == "hola"


def _patch_chat_engine(reply_text: str = "Estoy aquí", *, blocked: bool = False):
    perception = {"blocked": blocked} if blocked else {"risk": 0.1, "context": "ok"}

    class _StubResult:
        def __init__(self) -> None:
            self.message = reply_text
            self.signals = None
            self.evaluation = None
            self.perception_raw = perception
            self.latency_ms = {"total": 12.0}

    return [
        patch(
            "src.server.app.ChatEngine.start",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "src.server.app.ChatEngine.turn",
            new_callable=AsyncMock,
            return_value=_StubResult(),
        ),
        patch(
            "src.server.app.ChatEngine.close",
            new_callable=AsyncMock,
            return_value=None,
        ),
    ]


def test_voice_turn_endpoint_returns_success_envelope() -> None:
    patches = _patch_chat_engine("Hola mundo")
    for p in patches:
        p.start()
    try:
        with TestClient(app) as client:
            response = client.post("/api/voice_turn", json=_envelope("hola"))
        body = response.json()
    finally:
        for p in patches:
            try:
                p.stop()
            except RuntimeError:
                pass

    assert response.status_code == 200
    assert body["version"] == CONTRACT_VERSION
    assert body["contract"] == VOICE_TURN_CONTRACT
    assert body["error"] is None
    assert body["response"]["reply_text"] == "Hola mundo"
    assert body["response"]["should_listen"] is True
    assert isinstance(body["latency_ms"], (int, float))
    assert math.isfinite(body["latency_ms"]) and body["latency_ms"] >= 0.0


def test_voice_turn_endpoint_marks_should_listen_false_when_blocked() -> None:
    patches = _patch_chat_engine("No puedo ayudar con eso.", blocked=True)
    for p in patches:
        p.start()
    try:
        with TestClient(app) as client:
            response = client.post("/api/voice_turn", json=_envelope("eres malo"))
        body = response.json()
    finally:
        for p in patches:
            try:
                p.stop()
            except RuntimeError:
                pass

    assert response.status_code == 200
    assert body["response"]["should_listen"] is False
    assert body["error"] is None


def test_voice_turn_endpoint_returns_400_on_empty_utterance() -> None:
    with TestClient(app) as client:
        response = client.post("/api/voice_turn", json=_envelope(""))
    body = response.json()
    assert response.status_code == 400
    assert body["error"] is not None
    assert body["error"]["code"] == "EMPTY_UTTERANCE"
    assert body["response"]["reply_text"] == ""
    assert body["response"]["should_listen"] is False


def test_voice_turn_endpoint_returns_503_when_llm_unavailable() -> None:
    patches = [
        patch(
            "src.server.app.ChatEngine.start",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch(
            "src.server.app.ChatEngine.close",
            new_callable=AsyncMock,
            return_value=None,
        ),
    ]
    for p in patches:
        p.start()
    try:
        with TestClient(app) as client:
            response = client.post("/api/voice_turn", json=_envelope("hola"))
        body = response.json()
    finally:
        for p in patches:
            try:
                p.stop()
            except RuntimeError:
                pass

    assert response.status_code == 503
    assert body["error"]["code"] == "LLM_UNAVAILABLE"
    assert body["response"]["should_listen"] is False
