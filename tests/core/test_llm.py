"""Tests for src/core/llm.py — OllamaClient (mocked HTTP)."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.core.llm import OllamaClient


# ── Fixtures ────────────────────────────────────────────────────────────────────

@pytest.fixture
def llm():
    return OllamaClient(base_url="http://fake:11434", model="test-model", timeout=5.0)


# ── Constructor ─────────────────────────────────────────────────────────────────

def test_init_defaults(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    c = OllamaClient()
    assert "11434" in c.base_url
    assert c.model  # non-empty


def test_init_env_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:9999")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma3:4b")
    c = OllamaClient()
    assert "9999" in c.base_url
    assert c.model == "gemma3:4b"


def test_init_explicit_args():
    c = OllamaClient(base_url="http://x:1234", model="my-model")
    assert "1234" in c.base_url
    assert c.model == "my-model"


def test_base_url_strips_trailing_slash():
    c = OllamaClient(base_url="http://x:1234/")
    assert not c.base_url.endswith("/")


# ── is_available ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_is_available_true(llm):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client
    assert await llm.is_available() is True


@pytest.mark.asyncio
async def test_is_available_false_on_error(llm):
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
    mock_client.is_closed = False
    llm._client = mock_client
    assert await llm.is_available() is False


@pytest.mark.asyncio
async def test_is_available_false_on_non_200(llm):
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client
    assert await llm.is_available() is False


# ── chat ────────────────────────────────────────────────────────────────────────

def _make_chat_response(content: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={"message": {"content": content}})
    return mock_resp


@pytest.mark.asyncio
async def test_chat_returns_text(llm):
    mock_resp = _make_chat_response("Hola mundo")
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    result = await llm.chat("Di hola")
    assert result == "Hola mundo"


@pytest.mark.asyncio
async def test_chat_with_system_prompt(llm):
    mock_resp = _make_chat_response("OK")
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    await llm.chat("msg", system_prompt="Eres un asistente")
    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
    messages = payload["messages"]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


@pytest.mark.asyncio
async def test_chat_no_system_prompt_omits_system(llm):
    mock_resp = _make_chat_response("OK")
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    await llm.chat("hello")
    call_kwargs = mock_client.post.call_args
    payload = call_kwargs.kwargs.get("json") or call_kwargs.args[1]
    roles = [m["role"] for m in payload["messages"]]
    assert "system" not in roles


@pytest.mark.asyncio
async def test_chat_raises_on_connect_error(llm):
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
    mock_client.is_closed = False
    llm._client = mock_client

    with pytest.raises(httpx.ConnectError):
        await llm.chat("hello")


@pytest.mark.asyncio
async def test_chat_strips_whitespace(llm):
    mock_resp = _make_chat_response("  respuesta con espacios  ")
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    result = await llm.chat("x")
    assert result == "respuesta con espacios"


# ── extract_json ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_extract_json_valid(llm):
    mock_resp = _make_chat_response('{"risk": 0.8, "urgency": 0.9}')
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    result = await llm.extract_json("scenario", "system")
    assert result["risk"] == 0.8
    assert result["urgency"] == 0.9


@pytest.mark.asyncio
async def test_extract_json_wrapped_in_markdown(llm):
    mock_resp = _make_chat_response('```json\n{"key": "val"}\n```')
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    result = await llm.extract_json("x", "y")
    assert result.get("key") == "val"


@pytest.mark.asyncio
async def test_extract_json_invalid_returns_empty(llm):
    mock_resp = _make_chat_response("no json here at all")
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    result = await llm.extract_json("x", "y")
    assert result == {}


@pytest.mark.asyncio
async def test_extract_json_malformed_returns_empty(llm):
    mock_resp = _make_chat_response("{bad json}")
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.is_closed = False
    llm._client = mock_client

    result = await llm.extract_json("x", "y")
    assert result == {}


# ── close ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_close_no_client(llm):
    """close() with no client should not raise."""
    llm._client = None
    await llm.close()  # must not raise


@pytest.mark.asyncio
async def test_close_closes_client(llm):
    mock_client = AsyncMock()
    mock_client.is_closed = False
    llm._client = mock_client
    await llm.close()
    mock_client.aclose.assert_called_once()
    assert llm._client is None
