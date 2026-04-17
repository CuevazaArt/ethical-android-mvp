"""
Perceptive lobe — async sensor / probe I/O (tri-lobe track).

Optional HTTP probe: ``KERNEL_PERCEPTIVE_LOBE_PROBE_URL`` triggers a single GET via
``httpx.AsyncClient`` with bounded timeouts. On failure, ``SemanticState.timeout_trauma``
records the event (cooperative degradation; see ADR 0002).
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

from .models import SemanticState, TimeoutTrauma

_log = logging.getLogger(__name__)

# Cooperative timeouts (seconds) — keep connect short to avoid worker pool stalls.
_DEFAULT_CONNECT = 2.0
_DEFAULT_READ = 5.0


class PerceptiveLobe:
    """
    Left hemisphere: async I/O, parsing, timeout coercion.

    When ``KERNEL_PERCEPTIVE_LOBE_PROBE_URL`` is unset, ``observe`` returns immediately
    with measured latency only (no outbound HTTP).
    """
    def __init__(
        self,
        safety_interlock: SafetyInterlock,
        strategist: ExecutiveStrategist,
        llm_backend: Optional[Any] = None
    ):
        self.safety_interlock = safety_interlock
        self.strategist = strategist
        self.llm_backend = llm_backend # For semantic perception if needed

    def __init__(self) -> None:
        self._http: httpx.AsyncClient | None = None

    def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(
                timeout=httpx.Timeout(_DEFAULT_READ, connect=_DEFAULT_CONNECT),
                follow_redirects=False,
            )
        return self._http

    async def aclose(self) -> None:
        """Close the async HTTP client (call from orchestrator shutdown or tests)."""
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    async def observe(
        self, raw_input: str, multimodal_payload: dict[str, Any] | None = None
    ) -> SemanticState:
        """
        Map raw input to a :class:`SemanticState`.

        If ``KERNEL_PERCEPTIVE_LOBE_PROBE_URL`` is set, performs one GET to validate
        async cooperative I/O; transport errors become :class:`TimeoutTrauma`.
        """
        start_time = time.time()
        probe_url = os.environ.get("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", "").strip()
        if not probe_url:
            latency_ms = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=1.0,
                raw_prompt=raw_input,
                sensory_latency_lag=latency_ms,
            )

        try:
            client = self._client()
            t_req = time.time()
            await client.get(probe_url)
            latency_ms = int((time.time() - t_req) * 1000)
            return SemanticState(
                perception_confidence=1.0,
                raw_prompt=raw_input,
                sensory_latency_lag=latency_ms,
            )
        except httpx.RequestError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            _log.debug("PerceptiveLobe probe failed: %s", e)
            return SemanticState(
                perception_confidence=0.35,
                raw_prompt=raw_input,
                sensory_latency_lag=latency_ms,
                timeout_trauma=TimeoutTrauma(
                    source_lobe="perceptive",
                    latency_ms=latency_ms,
                    severity=0.7,
                    context=str(e)[:200],
                ),
            )
