"""
Async bridge for chat UI / WebSocket layers.

The kernel and LLM calls are synchronous; this wrapper runs them in a thread
pool so an asyncio event loop is not blocked by I/O.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .kernel import EthicalKernel, ChatTurnResult
    from .modules.sensor_contracts import SensorSnapshot


class RealTimeBridge:
    """Thin adapter: `process_chat_turn` in a worker thread."""

    def __init__(self, kernel: "EthicalKernel"):
        self.kernel = kernel

    async def process_chat(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: "SensorSnapshot | None" = None,
    ) -> "ChatTurnResult":
        return await asyncio.to_thread(
            self.kernel.process_chat_turn,
            user_input,
            agent_id,
            place,
            include_narrative,
            sensor_snapshot,
        )
