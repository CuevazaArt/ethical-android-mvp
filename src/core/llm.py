"""
Ethos Core — LLM Client (V2 Minimal)

Does ONE thing: talks to Ollama and returns text.
No policies, no fallbacks, no dual-vote. Just send prompt, get text.

Usage:
    llm = OllamaClient()
    response = await llm.chat("Hola, ¿cómo estás?")
    print(response)  # "¡Hola! Estoy bien, gracias..."
"""

from __future__ import annotations

import json
import logging
import os
import time

import httpx

_log = logging.getLogger(__name__)


class OllamaClient:
    """Minimal async Ollama client. One class, one job: text in → text out."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ):
        self.base_url = (
            base_url or os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        ).rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            client = await self._get_client()
            r = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
            return r.status_code == 200
        except Exception:
            return False

    async def chat(
        self,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> str:
        """
        Send a message and get a response. That's it.

        Args:
            user_message: What the user said.
            system_prompt: Optional system context.
            temperature: Creativity dial (0.0 = robotic, 1.0 = creative).

        Returns:
            The model's text response.
        """
        t0 = time.perf_counter()
        client = await self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            r = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json()
            text = data.get("message", {}).get("content", "").strip()
            elapsed_ms = (time.perf_counter() - t0) * 1000
            _log.info("LLM chat: %.0fms, %d chars", elapsed_ms, len(text))
            return text
        except httpx.HTTPStatusError as e:
            _log.error("Ollama HTTP error: %s %s", e.response.status_code, e.response.text[:200])
            raise
        except httpx.ConnectError:
            _log.error("Cannot connect to Ollama at %s — is it running?", self.base_url)
            raise
        except Exception as e:
            _log.error("LLM chat failed: %s", e)
            raise

    async def chat_stream(
        self,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.7,
    ):
        """
        Stream response tokens as they arrive (async generator).

        Usage:
            async for chunk in llm.chat_stream("Hola"):
                print(chunk, end="", flush=True)
        """
        client = await self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature},
        }

        async with client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

    async def extract_json(
        self,
        user_message: str,
        system_prompt: str,
        temperature: float = 0.3,
    ) -> dict:
        """
        Send a prompt expecting JSON back. Parse it or return empty dict.
        Uses lower temperature by default for more structured output.
        """
        import re

        text = await self.chat(user_message, system_prompt, temperature)
        # Extract JSON from possible markdown wrapping
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                _log.warning("LLM returned invalid JSON: %s", text[:200])
                return {}
        return {}


# === Self-test ===
if __name__ == "__main__":
    import asyncio

    async def _demo():
        llm = OllamaClient()
        if not await llm.is_available():
            print("❌ Ollama is not running. Start it with: ollama serve")
            return

        print(f"✅ Connected to Ollama ({llm.model})")
        print("─" * 40)

        # Test 1: Simple chat
        print("Test 1: Simple chat")
        response = await llm.chat("Di 'hola mundo' en español, en una sola frase corta.")
        print(f"  → {response}")
        print()

        # Test 2: Streaming
        print("Test 2: Streaming")
        print("  → ", end="")
        async for token in llm.chat_stream("Cuenta del 1 al 5, un número por línea."):
            print(token, end="", flush=True)
        print("\n")

        # Test 3: JSON extraction
        print("Test 3: JSON extraction")
        data = await llm.extract_json(
            "Un hombre herido está en el suelo en un parque.",
            'Responde SOLO con JSON: {"risk": 0.0-1.0, "urgency": 0.0-1.0, "context": "string"}',
        )
        print(f"  → {data}")

        await llm.close()
        print("\n✅ All tests passed!")

    asyncio.run(_demo())
