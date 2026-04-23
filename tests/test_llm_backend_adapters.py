"""Unit tests for LLM adapter implementations (mock, HTTP JSON, Ollama-shaped HTTP)."""

import asyncio
import os
import sys
import threading
import types
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_backends import (
    CompletionOnlyAdapter,
    HttpJsonLLMBackend,
    MockLLMBackend,
    OllamaLLMBackend,
    coerce_to_llm_backend,
)


class _FakeCompletion:
    def complete(self, system: str, user: str) -> str:
        return f"{system[:4]}|{user[:4]}"


def test_coerce_to_llm_backend_none():
    assert coerce_to_llm_backend(None) is None


def test_coerce_to_llm_backend_wraps_protocol_instance():
    b = coerce_to_llm_backend(_FakeCompletion())
    assert b is not None
    assert b.completion("ab", "cd") == "ab|cd"
    assert b.embedding("x") is None


def test_mock_llm_backend_info_completion_embedding():
    b = MockLLMBackend(
        completion_text='{"ok": true}',
        embedding_vector=[3.0, 4.0],
        provider="mock_unit",
    )
    assert b.is_available() is True
    assert b.info()["provider"] == "mock_unit"
    assert b.completion("s", "u") == '{"ok": true}'
    emb = b.embedding("text")
    assert emb == [3.0, 4.0]


def test_mock_llm_backend_respects_availability_flag():
    b = MockLLMBackend(available=False)
    assert b.is_available() is False


def test_mock_llm_backend_completion_error():
    b = MockLLMBackend(completion_error=RuntimeError("down"))
    with pytest.raises(RuntimeError, match="down"):
        b.completion("a", "b")


def test_mock_llm_backend_embedding_error():
    b = MockLLMBackend(embedding_vector=[1.0], embedding_error=ValueError("embed"))
    with pytest.raises(ValueError, match="embed"):
        b.embedding("x")


def test_completion_only_adapter_delegates():
    inner = _FakeCompletion()
    ad = CompletionOnlyAdapter(inner)
    assert ad.complete("aa", "bb") == "aa|bb"
    assert ad.embedding("z") is None
    assert ad.is_available() is True


def test_http_json_llm_backend(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"text": "  hello  ", "extra": 1}

    class FakeClient:
        def __init__(self, *a, **k):
            self.post = MagicMock(return_value=FakeResp())

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr("src.modules.llm_backends.httpx.Client", FakeClient)
    b = HttpJsonLLMBackend("http://lab.example/infer", response_text_key="text")
    assert b.completion("sys", "usr") == "hello"
    assert b.embedding("x") is None
    assert b.info()["provider"] == "http_json"


def test_ollama_llm_backend_chat_and_embed(monkeypatch):
    class FakeResp:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return self._payload

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None):
            if url.endswith("/api/chat"):
                return FakeResp({"message": {"content": "  model out  "}})
            if url.endswith("/api/embeddings"):
                return FakeResp({"embedding": [0.0, 1.0, 0.0]})
            raise AssertionError(f"unexpected url {url!r}")

    monkeypatch.setattr("src.modules.llm_backends.httpx.Client", FakeClient)
    b = OllamaLLMBackend(
        "http://ollama.test",
        "llama",
        30.0,
        embed_model="nomic-embed-text",
    )
    assert b.completion("s", "u") == "model out"
    emb = b.embedding("phrase")
    assert emb == [0.0, 1.0, 0.0]


def test_ollama_llm_backend_completion_passes_temperature_in_options(monkeypatch):
    posted: list[dict] = []

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "x"}}

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None):
            if url.endswith("/api/chat"):
                posted.append(json or {})
                return FakeResp()
            raise AssertionError(url)

    monkeypatch.setattr("src.modules.llm_backends.httpx.Client", FakeClient)
    b = OllamaLLMBackend("http://ollama.test", "llama", 30.0)
    b.completion("s", "u", temperature=0.15)
    assert posted[0]["options"]["temperature"] == pytest.approx(0.15)


def test_ollama_llm_backend_embed_uses_env_model(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"embedding": [1.0]}

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None):
            return FakeResp()

    monkeypatch.setattr("src.modules.llm_backends.httpx.Client", FakeClient)
    os.environ["KERNEL_SEMANTIC_CHAT_EMBED_MODEL"] = "custom-embed"
    try:
        b = OllamaLLMBackend("http://x", "m", 1.0, embed_model=None)
        b.embedding("t")
        assert b.info()["embed_model"] == "custom-embed"
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_EMBED_MODEL", None)


def test_http_json_llm_backend_malformed_json_raises_valueerror(monkeypatch):
    class BadResp:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("boom")

        @property
        def text(self):
            return "not json"

        @property
        def status_code(self):
            return 200

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None, headers=None):
            return BadResp()

    monkeypatch.setattr("src.modules.llm_backends.httpx.Client", FakeClient)
    b = HttpJsonLLMBackend("http://lab.example/infer", response_text_key="text")
    with pytest.raises(ValueError, match="invalid JSON"):
        b.completion("sys", "usr")


def test_ollama_embedding_propagates_llm_cancel(monkeypatch):
    import threading

    from src.modules.llm_http_cancel import LLMHttpCancelledError, clear_llm_cancel_scope, set_llm_cancel_scope

    class NeverCalled:
        def __enter__(self):
            raise AssertionError("should not open client when cancelled first")

        def __exit__(self, *a):
            return False

    monkeypatch.setattr("src.modules.llm_backends.httpx.Client", NeverCalled)
    b = OllamaLLMBackend("http://ollama.test", "m", 1.0)
    ev = threading.Event()
    ev.set()
    set_llm_cancel_scope(ev)
    try:
        with pytest.raises(LLMHttpCancelledError):
            b.embedding("x")
    finally:
        clear_llm_cancel_scope()


def test_anthropic_llm_backend_messages_api(monkeypatch):
    from src.modules.llm_backends import AnthropicLLMBackend

    class FakeContent:
        text = "anthropic reply"

    class FakeMsg:
        content = [FakeContent()]

    client = MagicMock()
    client.messages.create.return_value = FakeMsg()
    b = AnthropicLLMBackend(client, "claude-3-test")
    assert b.completion("sys", "user") == "anthropic reply"
    assert b.embedding("x") is None
    client.messages.create.assert_called_once()


async def test_anthropic_acompletion_stream_cooperative_cancel_between_chunks(monkeypatch):
    from src.modules.llm_backends import AnthropicLLMBackend
    from src.modules.llm_http_cancel import (
        LLMHttpCancelledError,
        clear_llm_cancel_scope,
        set_llm_cancel_scope,
    )

    class FakeStream:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        class _TextIter:
            def __init__(self) -> None:
                self._i = 0

            def __aiter__(self):
                return self

            async def __anext__(self) -> str:
                self._i += 1
                if self._i > 40:
                    raise StopAsyncIteration
                await asyncio.sleep(0)
                return "x"

        @property
        def text_stream(self):
            return self._TextIter()

    class FakeMessages:
        def stream(self, **kwargs: object):
            return FakeStream()

    class FakeAsyncAnthropic:
        def __init__(self, api_key: str | None = None) -> None:
            self.messages = FakeMessages()

        async def close(self) -> None:
            pass

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-stream-cancel")
    fake_anthropic = types.ModuleType("anthropic")
    fake_anthropic.AsyncAnthropic = FakeAsyncAnthropic  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", fake_anthropic)

    sync_client = MagicMock()
    sync_client.api_key = "k"
    b = AnthropicLLMBackend(sync_client, "claude-test")

    ev = threading.Event()
    set_llm_cancel_scope(ev)
    try:

        async def consume() -> None:
            n = 0
            async for _t in b.acompletion_stream("sys", "usr"):
                n += 1
                if n >= 5:
                    ev.set()

        with pytest.raises(LLMHttpCancelledError):
            await consume()
    finally:
        clear_llm_cancel_scope()
