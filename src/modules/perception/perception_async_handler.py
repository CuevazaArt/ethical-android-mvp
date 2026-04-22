"""
Async Perception Handler — extracted from monolithic kernel.py.

Isolates perception stage (MalAbs → semantic → vitality assessment) into
standalone async handler, enabling better resource management and turnover.

Separates I/O-bound perception operations from CPU-bound ethical decisions,
matching hemisphere refactor architecture.
"""
# Status: SCAFFOLD


from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class PerceptionAsyncContext:
    """Context for async perception operations — extracted from kernel processing."""

    user_input: str
    conversation_context: str | None = None
    sensor_snapshot: dict[str, Any] | None = None
    include_semantic: bool = True


async def run_perception_async(
    ctx: PerceptionAsyncContext,
    malabs_evaluator: Any = None,
    semantic_backend: Any = None,
) -> dict[str, Any]:
    """
    Run perception stage asynchronously.

    Decouples from EthicalKernel monolith; enables cancellation and isolation
    of perception timeouts from ethical judgment path.

    Parameters:
            ctx: Perception context (input, conversation, sensors)
            malabs_evaluator: MalAbs gate; ``aevaluate_chat_text`` is used when present so
            semantic embeddings never run sync HTTP on the event loop.
            semantic_backend: Optional semantic embedding backend

    Returns:
            Perception result dict with malabs decision, confidence, etc.
    """
    result = {
        "user_input": ctx.user_input,
        "conversation_context": ctx.conversation_context,
        "sensor_snapshot": ctx.sensor_snapshot,
        "malabs_decision": None,
        "semantic_confidence": 0.0,
        "ready_for_ethical_stage": True,
    }

    # Run MalAbs without calling sync ``evaluate_chat_text`` on the event loop (Bloque 34.0).
    if malabs_evaluator is not None:
        try:
            aeval = getattr(malabs_evaluator, "aevaluate_chat_text", None)
            if callable(aeval):
                decision = await aeval(ctx.user_input, llm_backend=semantic_backend)
            else:
                decision = await asyncio.to_thread(
                    malabs_evaluator.evaluate_chat_text,
                    ctx.user_input,
                    semantic_backend,
                )
            result["malabs_decision"] = decision
            result["ready_for_ethical_stage"] = not decision.blocked
        except Exception as e:
            _log.warning("MalAbs evaluation failed: %s", e)
            result["malabs_decision"] = None

    return result
