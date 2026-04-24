"""
V2.19 — Integration tests for src/server/app.py.

Validates API endpoints and WebSocket protocol without Ollama.
All LLM calls are patched. No network calls.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from starlette.testclient import TestClient

from src.server.app import app


# ── Shared LLM mock ────────────────────────────────────────────────────────────

async def _fake_stream(*args, **kwargs):
    """Async generator yielding one stub token — satisfies chat_stream callers."""
    yield "Estoy aquí."


def _apply_patches():
    patches = [
        patch("src.core.llm.OllamaClient.is_available", new_callable=AsyncMock, return_value=True),
        patch("src.core.llm.OllamaClient.extract_json", new_callable=AsyncMock, return_value={}),
        patch("src.core.llm.OllamaClient.chat", new_callable=AsyncMock, return_value="Estoy aquí para ayudarte."),
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
        for field in ("model", "memory_episodes", "uptime", "status",
                      "identity_narrative", "identity_profile",
                      "last_latency_ms", "stt_available"):
            assert field in data, f"Missing field: {field}"
        assert data["status"] == "online"
    finally:
        _stop_patches(patches)


def test_ws_chat_receives_done_event():
    """WS /ws/chat: plain text must produce a 'done' event with blocked=false."""
    patches = _apply_patches()
    try:
        with TestClient(app) as client:
            with client.websocket_connect("/ws/chat") as ws:
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
        with TestClient(app) as client:
            with client.websocket_connect("/ws/chat") as ws:
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
