"""
Async bridge for chat UI / WebSocket layers.

The kernel and LLM calls are synchronous; this wrapper runs them in a thread
pool (Starlette/FastAPI ``run_in_threadpool``) so the asyncio event loop is not
blocked by deliberation or I/O.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.concurrency import run_in_threadpool

if TYPE_CHECKING:
    from .kernel import ChatTurnResult, EthicalKernel
    from .modules.sensor_contracts import SensorSnapshot


class RealTimeBridge:
    """Thin adapter: `process_chat_turn` in a worker thread."""

    def __init__(self, kernel: EthicalKernel):
        self.kernel = kernel

    async def process_chat(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: SensorSnapshot | None = None,
        escalate_to_dao: bool = False,
    ) -> ChatTurnResult:
        return await run_in_threadpool(
            self.kernel.process_chat_turn,
            user_input,
            agent_id,
            place,
            include_narrative,
            sensor_snapshot,
            escalate_to_dao,
        )
