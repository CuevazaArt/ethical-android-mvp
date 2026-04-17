"""
LLM adapters for :class:`LLMModule` (completion + optional embeddings).

**Unified contract:** :class:`LLMBackend` centralizes ``is_available()``, ``completion()``,
``embedding()``, and ``info()`` behind one interface (Ollama, Anthropic, HTTP JSON lab,
mock, and legacy :class:`TextCompletionBackend` via :class:`CompletionOnlyAdapter`).

The kernel still routes only through ``LLMModule``; semantic MalAbs may use
``embedding()`` when a backend is passed from ``EthicalKernel``.

**Inference-agnostic name:** :class:`LLMBackend` is the stable operator-facing
“inference provider” contract (completion + optional embeddings). Alias
``InferenceProvider`` documents intent without adding a second type hierarchy.
"""

from __future__ import annotations

import asyncio
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

import httpx

from .llm_http_cancel import raise_if_llm_cancel_requested


@runtime_checkable
class TextCompletionBackend(Protocol):
    def complete(self, system: str, user: str) -> str:
        """Return model text (may be JSON or prose depending on caller)."""
        ...


class LLMBackend(ABC):
    """
    Adapter contract for LLM providers (Phase 3+ robustness).

    ``complete()`` is a thin alias for :meth:`completion` for backward compatibility
    with :class:`TextCompletionBackend` call sites.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Whether this backend is configured for use (not a live health check unless documented)."""

    @abstractmethod
    def completion(self, system: str, user: str, **kwargs: Any) -> str:
        """Chat / instruction-following completion (optional ``temperature`` for supported backends)."""

    @abstractmethod
    def embedding(self, text: str) -> list[float] | None:
        """
        Return a raw embedding vector for ``text``, or ``None`` if unsupported / failed.

        Implementations may return unnormalized vectors; callers normalize as needed.
        """

    @abstractmethod
    def info(self) -> dict[str, Any]:
        """Stable, JSON-serializable metadata for operators and tests."""

    def complete(self, system: str, user: str) -> str:
        return self.completion(system, user)

    async def acompletion(self, system: str, user: str, **kwargs: Any) -> str:
        """
        Async completion; default runs sync :meth:`completion` in a worker thread.

        Subclasses that use ``httpx.AsyncClient`` override for true asyncio cancellation.
        """
        raise_if_llm_cancel_requested()
        return await asyncio.to_thread(lambda: self.completion(system, user, **kwargs))


class CompletionOnlyAdapter(LLMBackend):
    """Wrap a legacy :class:`TextCompletionBackend` (completion only; no embeddings)."""

    def __init__(self, inner: TextCompletionBackend) -> None:
        self._inner = inner

    def is_available(self) -> bool:
        return True

    def completion(self, system: str, user: str, **kwargs: Any) -> str:
        return self._inner.complete(system, user)

    def embedding(self, text: str) -> list[float] | None:
        return None

    def info(self) -> dict[str, Any]:
        return {"provider": "completion_only_adapter", "inner": type(self._inner).__name__}


def coerce_to_llm_backend(backend: Any) -> LLMBackend | None:
    """Normalize injectable backends to :class:`LLMBackend` when possible."""
    if backend is None:
        return None
    if isinstance(backend, LLMBackend):
        return backend
    if isinstance(backend, TextCompletionBackend):
        return CompletionOnlyAdapter(backend)
    return None


class AnthropicLLMBackend(LLMBackend):
    """Claude Messages API."""

    def __init__(self, client: Any, model: str) -> None:
        self._client = client
        self._model = model

    def is_available(self) -> bool:
        return self._client is not None

    def completion(self, system: str, user: str, **kwargs: Any) -> str:
        raise_if_llm_cancel_requested()
        t = kwargs.get("temperature")
        extra: dict[str, Any] = {}
        if t is not None:
            extra["temperature"] = float(t)
        response = self._client.messages.create(
            model=self._model,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user}],
            **extra,
        )
        return response.content[0].text

    def embedding(self, text: str) -> list[float] | None:
        return None

    def info(self) -> dict[str, Any]:
        return {"provider": "anthropic", "model": self._model}

    async def acompletion(self, system: str, user: str, **kwargs: Any) -> str:
        """Async Messages API so ``asyncio.wait_for`` can cancel in-flight requests."""
        raise_if_llm_cancel_requested()
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            return await super().acompletion(system, user, **kwargs)
        t = kwargs.get("temperature")
        extra: dict[str, Any] = {}
        if t is not None:
            extra["temperature"] = float(t)
        api_key = getattr(self._client, "api_key", None) or os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            return await super().acompletion(system, user, **kwargs)
        aclient = AsyncAnthropic(api_key=api_key)
        try:
            response = await aclient.messages.create(
                model=self._model,
                max_tokens=1000,
                system=system,
                messages=[{"role": "user", "content": user}],
                **extra,
            )
            return response.content[0].text
        finally:
            aclose = getattr(aclient, "close", None)
            if aclose is not None:
                await aclose()


class OllamaLLMBackend(LLMBackend):
    """Ollama ``/api/chat`` + optional ``/api/embeddings`` (same base URL)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: float,
        *,
        embed_model: str | None = None,
        embed_timeout: float | None = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._model = model
        self._timeout = float(timeout)
        self._embed_model = (
            embed_model
            if embed_model is not None
            else os.environ.get("KERNEL_SEMANTIC_CHAT_EMBED_MODEL", "nomic-embed-text").strip()
            or "nomic-embed-text"
        )
        self._embed_timeout = float(embed_timeout) if embed_timeout is not None else 10.0

    def is_available(self) -> bool:
        return bool(self._base)

    def completion(self, system: str, user: str, **kwargs: Any) -> str:
        raise_if_llm_cancel_requested()
        url = f"{self._base}/api/chat"
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
        t = kwargs.get("temperature")
        if t is not None:
            payload["options"] = {"temperature": float(t)}
        with httpx.Client(timeout=self._timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        msg = data.get("message") or {}
        return (msg.get("content") or "").strip()

    async def acompletion(self, system: str, user: str, **kwargs: Any) -> str:
        """Async ``/api/chat`` so ``asyncio.wait_for`` can cancel an in-flight request."""
        raise_if_llm_cancel_requested()
        url = f"{self._base}/api/chat"
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
        t = kwargs.get("temperature")
        if t is not None:
            payload["options"] = {"temperature": float(t)}
        timeout = httpx.Timeout(self._timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        msg = data.get("message") or {}
        return (msg.get("content") or "").strip()

    def embedding(self, text: str) -> list[float] | None:
        if not (text or "").strip():
            return None
        url = f"{self._base}/api/embeddings"
        payload = {"model": self._embed_model, "prompt": text}
        try:
            with httpx.Client(timeout=self._embed_timeout) as client:
                r = client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return None
        emb = data.get("embedding")
        if not emb or not isinstance(emb, list):
            return None
        return [float(x) for x in emb]

    def info(self) -> dict[str, Any]:
        return {
            "provider": "ollama",
            "model": self._model,
            "base_url": self._base,
            "embed_model": self._embed_model,
        }


class HttpJsonLLMBackend(LLMBackend):
    """
    Lab / remote HTTP adapter: POST JSON ``{"system","user"}``, read ``text`` (or custom key).

    Embeddings are not supported (``None``).
    """

    def __init__(
        self,
        url: str,
        *,
        timeout: float = 60.0,
        response_text_key: str = "text",
        headers: dict[str, str] | None = None,
    ) -> None:
        self._url = url
        self._timeout = float(timeout)
        self._key = response_text_key
        self._headers = dict(headers or {})

    def is_available(self) -> bool:
        return bool(self._url)

    def completion(self, system: str, user: str, **kwargs: Any) -> str:
        raise_if_llm_cancel_requested()
        with httpx.Client(timeout=self._timeout) as client:
            r = client.post(
                self._url,
                json={"system": system, "user": user},
                headers=self._headers,
            )
            r.raise_for_status()
            data = r.json()
        return str(data.get(self._key) or "").strip()

    async def acompletion(self, system: str, user: str, **kwargs: Any) -> str:
        raise_if_llm_cancel_requested()
        timeout = httpx.Timeout(self._timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                self._url,
                json={"system": system, "user": user},
                headers=self._headers,
            )
            r.raise_for_status()
            data = r.json()
        return str(data.get(self._key) or "").strip()

    def embedding(self, text: str) -> list[float] | None:
        return None

    def info(self) -> dict[str, Any]:
        return {"provider": "http_json", "url": self._url, "response_key": self._key}


class MockLLMBackend(LLMBackend):
    """Deterministic backend for tests: latency, failures, custom vectors."""

    def __init__(
        self,
        *,
        completion_text: str = "{}",
        embedding_vector: list[float] | None = None,
        completion_delay_s: float = 0.0,
        embedding_delay_s: float = 0.0,
        completion_error: Exception | None = None,
        embedding_error: Exception | None = None,
        available: bool = True,
        provider: str = "mock",
    ) -> None:
        self._completion_text = completion_text
        self._embedding_vector = embedding_vector
        self._completion_delay_s = completion_delay_s
        self._embedding_delay_s = embedding_delay_s
        self._completion_error = completion_error
        self._embedding_error = embedding_error
        self._available = available
        self._provider = provider

    def is_available(self) -> bool:
        return self._available

    def completion(self, system: str, user: str, **kwargs: Any) -> str:
        if self._completion_error is not None:
            raise self._completion_error
        if self._completion_delay_s > 0:
            remaining = float(self._completion_delay_s)
            while remaining > 0:
                raise_if_llm_cancel_requested()
                step = min(0.05, remaining)
                time.sleep(step)
                remaining -= step
        return self._completion_text

    async def acompletion(self, system: str, user: str, **kwargs: Any) -> str:
        if self._completion_error is not None:
            raise self._completion_error
        if self._completion_delay_s > 0:
            remaining = float(self._completion_delay_s)
            while remaining > 0:
                raise_if_llm_cancel_requested()
                step = min(0.05, remaining)
                await asyncio.sleep(step)
                remaining -= step
        return self._completion_text

    def embedding(self, text: str) -> list[float] | None:
        if self._embedding_error is not None:
            raise self._embedding_error
        if self._embedding_delay_s > 0:
            time.sleep(self._embedding_delay_s)
        if self._embedding_vector is None:
            return None
        return list(self._embedding_vector)

    def info(self) -> dict[str, Any]:
        return {"provider": self._provider}


# Backward-compatible names (existing imports).
AnthropicCompletion = AnthropicLLMBackend
OllamaCompletion = OllamaLLMBackend

# Minimal public adapter names (same classes as *LLMBackend above).
OllamaRemote = OllamaLLMBackend
HTTPRemote = HttpJsonLLMBackend
MockBackend = MockLLMBackend

InferenceProvider = LLMBackend
