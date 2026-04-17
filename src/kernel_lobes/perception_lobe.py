from __future__ import annotations

import asyncio
import os
import time
from typing import TYPE_CHECKING, Any

from src.kernel_lobes.models import SemanticState, TimeoutTrauma

if TYPE_CHECKING:
    from src.modules.llm_layer import LLMModule

_DEFAULT_OBSERVE_TIMEOUT = 30.0  # seconds; override via KERNEL_LOBE_OBSERVE_TIMEOUT


def _observe_timeout() -> float:
    try:
        return float(os.environ.get("KERNEL_LOBE_OBSERVE_TIMEOUT", _DEFAULT_OBSERVE_TIMEOUT))
    except ValueError:
        return _DEFAULT_OBSERVE_TIMEOUT


class PerceptiveLobe:
    """
    Hemisferio Izquierdo: Async I/O, Parsing, and Timeout Coercion.

    Uses ``httpx.AsyncClient`` (via ``LLMModule.aperceive``) with a hard
    ``asyncio.wait_for`` deadline.  On timeout the lobe returns a
    :class:`~src.kernel_lobes.models.SemanticState` carrying a
    :class:`~src.kernel_lobes.models.TimeoutTrauma` so the LimbicLobe can
    apply the appropriate Bayesian penalty downstream.
    """

    def __init__(self, llm: LLMModule | None = None) -> None:
        self._llm = llm

    async def observe(
        self,
        raw_input: str,
        multimodal_payload: dict[str, Any] | None = None,
        conversation_context: str = "",
    ) -> SemanticState:
        """
        Takes raw input, queries LLMs via async HTTP with strict timeouts.

        Returns a :class:`SemanticState` with ``timeout_trauma`` set when the
        LLM call exceeds ``KERNEL_LOBE_OBSERVE_TIMEOUT`` or raises an error.
        """
        start_time = time.time()
        timeout = _observe_timeout()

        if self._llm is None:
            # No LLM configured — fast degraded path, high confidence stub
            latency = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=1.0,
                raw_prompt=raw_input,
                sensory_latency_lag=latency,
            )

        try:
            perception = await asyncio.wait_for(
                self._llm.aperceive(raw_input, conversation_context=conversation_context),
                timeout=timeout,
            )
            latency = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=perception.confidence,
                raw_prompt=raw_input,
                sensory_latency_lag=latency,
            )
        except asyncio.TimeoutError:
            latency = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=0.0,
                raw_prompt=raw_input,
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    source_lobe="PerceptiveLobe",
                    latency_ms=latency,
                    severity=1.0,
                    context=f"LLM aperceive timeout after {timeout}s",
                ),
            )
        except Exception as exc:
            latency = int((time.time() - start_time) * 1000)
            return SemanticState(
                perception_confidence=0.0,
                raw_prompt=raw_input,
                sensory_latency_lag=latency,
                timeout_trauma=TimeoutTrauma(
                    source_lobe="PerceptiveLobe",
                    latency_ms=latency,
                    severity=0.8,
                    context=f"LLM aperceive error: {type(exc).__name__}",
                ),
            )
