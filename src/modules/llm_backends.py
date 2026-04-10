"""
Text completion backends for :class:`LLMModule` (Fase 3.1).

Used for JSON-structured prompts (perceive / communicate / narrate) and optional
plain-text monologue embellishment. The kernel never calls these directly; only ``LLMModule`` does.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TextCompletionBackend(Protocol):
    def complete(self, system: str, user: str) -> str:
        """Return model text (may be JSON or prose depending on caller)."""
        ...


class AnthropicCompletion:
    """Claude Messages API."""

    def __init__(self, client, model: str):
        self._client = client
        self._model = model

    def complete(self, system: str, user: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text


class OllamaCompletion:
    """Ollama ``POST /api/chat`` (local, privacy-friendly)."""

    def __init__(self, base_url: str, model: str, timeout: float):
        self._base = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def complete(self, system: str, user: str) -> str:
        import httpx

        url = f"{self._base}/api/chat"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
        with httpx.Client(timeout=self._timeout) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        msg = data.get("message") or {}
        return (msg.get("content") or "").strip()
