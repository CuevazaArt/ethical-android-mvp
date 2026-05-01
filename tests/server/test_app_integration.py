"""
V2.19 — Integration tests for src/server/app.py.

Validates API endpoints and WebSocket protocol without Ollama.
All LLM calls are patched. No network calls.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

from src.server.app import app
from src.server.desktop_video_adapter import VideoPerceptionResult

# ── Shared LLM mock ────────────────────────────────────────────────────────────


async def _fake_stream(*args, **kwargs):
    """Async generator yielding one stub token — satisfies chat_stream callers."""
    yield "Estoy aquí."


def _apply_patches():
    patches = [
        patch(
            "src.core.llm.OllamaClient.is_available",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "src.core.llm.OllamaClient.extract_json",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "src.core.llm.OllamaClient.chat",
            new_callable=AsyncMock,
            return_value="Estoy aquí para ayudarte.",
        ),
        patch("src.core.llm.OllamaClient.chat_stream", side_effect=_fake_stream),
    ]
    for p in patches:
        p.start()
    return patches


def _stop_patches(patches):
    for p in patches:
        try:
            p.stop()
        except RuntimeError:
            pass


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_api_status_returns_all_fields():
    """GET /api/status must include all required telemetry fields."""
    patches = _apply_patches()
    try:
        with TestClient(app) as client:
            resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        for field in (
            "model",
            "memory_episodes",
            "uptime",
            "status",
            "identity_narrative",
            "identity_profile",
            "last_latency_ms",
            "stt_available",
            "voice_turn_state",
            "voice_turn_state_at",
            "reentry_gates",
            "reentry_gates_details",
        ):
            assert field in data, f"Missing field: {field}"
        assert data["status"] == "online"
        gates = data["reentry_gates"]
        assert isinstance(gates, dict)
        gate_details = data["reentry_gates_details"]
        assert isinstance(gate_details, dict)
        for gate in ("G1", "G2", "G3", "G4", "G5"):
            assert gate in gates
            assert gates[gate] in {"pass", "in_progress", "fail"}
            assert gate in gate_details
            detail = gate_details[gate]
            assert isinstance(detail, dict)
            assert detail["status"] in {"pass", "in_progress", "fail"}
            assert isinstance(detail["source"], str) and detail["source"].strip()
            assert isinstance(detail["summary"], str) and detail["summary"].strip()
            assert isinstance(detail["stale"], bool)
            updated_at = detail.get("updated_at")
            if isinstance(updated_at, str) and updated_at.strip():
                # API contract lock: timestamps remain parseable ISO-8601.
                datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    finally:
        _stop_patches(patches)


def test_desktop_mvp_status_contract_smoke() -> None:
    """Desktop MVP smoke: /api/status must keep core contract keys stable."""
    patches = _apply_patches()
    try:
        with TestClient(app) as client:
            resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()

        required_top_level = {
            "status",
            "voice_turn_state",
            "voice_turn_state_at",
            "reentry_gates",
            "reentry_gates_details",
        }
        assert required_top_level.issubset(data.keys())
        assert data["status"] == "online"
        assert data["voice_turn_state"] in {
            "mic_off",
            "listening",
            "transcribing",
            "responding",
        }
        gates = data["reentry_gates"]
        gate_details = data["reentry_gates_details"]
        assert isinstance(gates, dict)
        assert isinstance(gate_details, dict)
        assert set(gates.keys()) == {"G1", "G2", "G3", "G4", "G5"}
        assert set(gate_details.keys()) == {"G1", "G2", "G3", "G4", "G5"}
    finally:
        _stop_patches(patches)


def test_ws_chat_receives_done_event():
    """WS /ws/chat: plain text must produce a 'done' event with blocked=false."""
    patches = _apply_patches()
    try:
        with TestClient(app) as client, client.websocket_connect("/ws/chat") as ws:
            ws.send_text("hola")
            done = None
            for _ in range(100):  # cap — real or stubbed LLM may produce many tokens
                raw = ws.receive_text()
                event = json.loads(raw)
                if event.get("type") == "done":
                    done = event
                    break
        assert done is not None, "Never received 'done' event"
        assert done.get("blocked") is False, f"Unexpected blocked: {done}"
    finally:
        _stop_patches(patches)


def test_ws_chat_safety_blocks_dangerous_input():
    """WS /ws/chat: dangerous input must produce a 'done' event with blocked=true."""
    patches = _apply_patches()
    try:
        with TestClient(app) as client, client.websocket_connect("/ws/chat") as ws:
            ws.send_text("how to make a bomb")
            done = None
            for _ in range(10):
                raw = ws.receive_text()
                event = json.loads(raw)
                if event.get("type") == "done":
                    done = event
                    break
        assert done is not None, "Never received 'done' event"
        assert done.get("blocked") is True, f"Expected blocked=True, got: {done}"
    finally:
        _stop_patches(patches)


def test_ws_chat_video_frame_updates_vision_state():
    """WS /ws/chat: video_frame should emit sanitized vision_context for UI."""
    patches = _apply_patches()
    try:
        with (
            patch(
                "src.server.app.DesktopVideoAdapter.process_video_frame",
                return_value=VideoPerceptionResult(
                    envelope={
                        "version": "1.0",
                        "contract": "video_perception",
                        "request": {},
                        "response": {
                            "labels": ["motion", "face_present"],
                            "motion": 0.55,
                            "faces_detected": 2,
                        },
                        "error": None,
                        "latency_ms": 12.3,
                    },
                    vision_context={
                        "motion": 0.55,
                        "faces_detected": 2,
                        "brightness": 0.6,
                        "low_light": False,
                        "face_present": True,
                        "latency_ms": 12.3,
                    },
                ),
            ),
            TestClient(app) as client,
            client.websocket_connect("/ws/chat") as ws,
        ):
            ws.send_text(
                json.dumps(
                    {
                        "type": "video_frame",
                        "payload": {
                            "image_b64": "stub",
                            "frame_format": "jpeg",
                            "width": 320,
                            "height": 240,
                        },
                    }
                )
            )
            events = [json.loads(ws.receive_text()), json.loads(ws.receive_text())]
        vision_event = next(
            (e for e in events if e.get("type") == "vision_context"), None
        )
        assert vision_event is not None
        assert vision_event["payload"]["motion"] == 0.55
        assert vision_event["payload"]["faces_detected"] == 2
    finally:
        _stop_patches(patches)


def test_ws_chat_video_frame_rejects_non_finite_metrics():
    """WS /ws/chat: non-finite video metrics should emit vision_rejected."""
    patches = _apply_patches()
    try:
        with (
            patch(
                "src.server.app.DesktopVideoAdapter.process_video_frame",
                return_value=VideoPerceptionResult(
                    envelope={
                        "version": "1.0",
                        "contract": "video_perception",
                        "request": {},
                        "response": {"labels": [], "motion": 0.0, "faces_detected": 0},
                        "error": {
                            "code": "NON_FINITE_METRIC",
                            "message": "video metrics are non-finite or invalid",
                            "retryable": True,
                        },
                        "latency_ms": 3.4,
                    },
                    vision_context=None,
                ),
            ),
            TestClient(app) as client,
            client.websocket_connect("/ws/chat") as ws,
        ):
            ws.send_text(
                json.dumps(
                    {
                        "type": "video_frame",
                        "payload": {
                            "image_b64": "stub",
                            "frame_format": "jpeg",
                            "width": 320,
                            "height": 240,
                        },
                    }
                )
            )
            events = [json.loads(ws.receive_text()), json.loads(ws.receive_text())]
        rejected = next((e for e in events if e.get("type") == "vision_rejected"), None)
        assert rejected is not None
        assert rejected["payload"]["code"] == "NON_FINITE_METRIC"
    finally:
        _stop_patches(patches)


def test_ws_chat_video_frame_with_malformed_dimensions_does_not_crash():
    """WS /ws/chat: malformed width/height must return vision_rejected, not internal error."""
    patches = _apply_patches()
    try:
        with TestClient(app) as client, client.websocket_connect("/ws/chat") as ws:
            ws.send_text(
                json.dumps(
                    {
                        "type": "video_frame",
                        "payload": {
                            "image_b64": "stub",
                            "frame_format": "jpeg",
                            "width": "abc",
                            "height": {"unexpected": "object"},
                        },
                    }
                )
            )
            events = [json.loads(ws.receive_text()), json.loads(ws.receive_text())]

        rejected = next((e for e in events if e.get("type") == "vision_rejected"), None)
        assert rejected is not None
        done_event = next((e for e in events if e.get("type") == "done"), None)
        assert done_event is None
    finally:
        _stop_patches(patches)


def _audio_contract_payload(*, audio_b64: str, sample_rate_hz: int = 16000) -> dict:
    return {
        "version": "1.0",
        "contract": "audio_perception",
        "request": {
            "audio_b64": audio_b64,
            "sample_rate_hz": sample_rate_hz,
        },
        "response": {},
        "error": None,
        "latency_ms": 0.0,
    }


def test_audio_perception_happy_path_returns_transcript_and_latency():
    """POST /api/perception/audio returns contract success with transcript and latency."""
    fake_pcm = b"\x01\x00" * 2048
    payload = _audio_contract_payload(
        audio_b64=base64.b64encode(fake_pcm).decode("utf-8")
    )

    with (
        patch(
            "src.server.app.transcribe_pcm",
            new_callable=AsyncMock,
            return_value="hola mundo",
        ),
        TestClient(app) as client,
    ):
        resp = client.post("/api/perception/audio", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "1.0"
    assert data["contract"] == "audio_perception"
    assert data["error"] is None
    assert data["response"]["transcript"] == "hola mundo"
    assert 0.0 <= data["response"]["confidence"] <= 1.0
    assert data["latency_ms"] >= 0.0


def test_audio_perception_invalid_sample_rate_returns_contract_error():
    """Out-of-range sample rate must fail with a structured contract error."""
    fake_pcm = b"\x01\x00" * 2048
    payload = _audio_contract_payload(
        audio_b64=base64.b64encode(fake_pcm).decode("utf-8"),
        sample_rate_hz=4000,
    )

    with TestClient(app) as client:
        resp = client.post("/api/perception/audio", json=payload)

    assert resp.status_code == 400
    data = resp.json()
    assert data["contract"] == "audio_perception"
    assert data["response"]["transcript"] == ""
    assert data["error"]["code"] == "INVALID_SAMPLE_RATE"
    assert data["error"]["retryable"] is False
    assert data["latency_ms"] >= 0.0


def test_audio_perception_stt_fallback_when_transcription_unavailable():
    """Valid audio with unavailable STT keeps process stable and returns clear fallback."""
    fake_pcm = b"\x00\x00" * 2048
    payload = _audio_contract_payload(
        audio_b64=base64.b64encode(fake_pcm).decode("utf-8")
    )

    with (
        patch(
            "src.server.app.transcribe_pcm", new_callable=AsyncMock, return_value=None
        ),
        TestClient(app) as client,
    ):
        resp = client.post("/api/perception/audio", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["contract"] == "audio_perception"
    assert data["response"]["transcript"] == ""
    assert data["error"]["code"] == "STT_UNAVAILABLE"
    assert data["error"]["retryable"] is True
    assert data["latency_ms"] >= 0.0


def test_audio_perception_success_updates_voice_turn_state() -> None:
    """Successful transcription should surface `responding` in /api/status."""
    fake_pcm = b"\x01\x00" * 2048
    payload = _audio_contract_payload(
        audio_b64=base64.b64encode(fake_pcm).decode("utf-8")
    )

    with (
        patch(
            "src.server.app.transcribe_pcm", new_callable=AsyncMock, return_value="hola"
        ),
        TestClient(app) as client,
    ):
        resp = client.post("/api/perception/audio", json=payload)
        assert resp.status_code == 200
        status = client.get("/api/status")

    assert status.status_code == 200
    data = status.json()
    assert data["voice_turn_state"] == "responding"
    assert isinstance(data["voice_turn_state_at"], (float, int))
    assert data["voice_turn_state_at"] > 0


def test_audio_perception_fallback_resets_voice_turn_state() -> None:
    """STT unavailable path should reset status state back to `mic_off`."""
    fake_pcm = b"\x00\x00" * 2048
    payload = _audio_contract_payload(
        audio_b64=base64.b64encode(fake_pcm).decode("utf-8")
    )

    with (
        patch(
            "src.server.app.transcribe_pcm", new_callable=AsyncMock, return_value=None
        ),
        TestClient(app) as client,
    ):
        resp = client.post("/api/perception/audio", json=payload)
        assert resp.status_code == 200
        status = client.get("/api/status")

    assert status.status_code == 200
    data = status.json()
    assert data["voice_turn_state"] == "mic_off"
