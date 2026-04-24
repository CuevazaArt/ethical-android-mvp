"""
Ethos Kernel — V2 Bridge (Legacy Compatibility)

This module acts as a bridge between the legacy Tri-Lobe API (V13) 
and the new consolidated V2 Core (src.core).

Use this to avoid breaking legacy scripts while the transition completes.
"""

import logging
from typing import Any
from src.core.chat import ChatEngine, TurnResult
from src.core.llm import OllamaClient
from src.core.ethics import Signals, Action

_log = logging.getLogger(__name__)

class ChatTurnResult:
    """Legacy compatibility wrapper for TurnResult."""
    def __init__(self, res: TurnResult):
        from dataclasses import dataclass
        @dataclass
        class ResponseShim:
            message: str
            tone: str = "neutral"
        
        self.response = ResponseShim(message=res.message)
        self.path = "v2_core_bridge"
        self.blocked = res.signals.risk >= 0.95 or (res.evaluation and res.evaluation.verdict == "Bad")
        self.block_reason = res.perception_raw.get("reason", "Ethical rejection")
        self.weighted_score = res.evaluation.score if res.evaluation else 0.0
        self.verdict = res.evaluation.verdict if res.evaluation else "Good"
        self.signals = res.signals

class EthosKernel:
    """
    Bridge class for the new V2 ChatEngine.
    Implements the essential API of the legacy EthosKernel.
    """

    def __init__(self, **kwargs) -> None:
        self.engine = ChatEngine()
        self.memory = self.engine.memory
        self.dao = None # Mock DAO not yet in V2 core
        _log.info("EthosKernel (V2 Bridge): Initialized.")

    async def start(self) -> None:
        await self.engine.start()
        _log.info("EthosKernel (V2 Bridge): Started.")

    async def stop(self) -> None:
        await self.engine.close()
        _log.info("EthosKernel (V2 Bridge): Stopped.")

    async def process_chat_turn_async(self, text: str, **kwargs) -> ChatTurnResult:
        res = await self.engine.turn(text)
        return ChatTurnResult(res)

    async def process_chat_turn_stream(self, text: str, **kwargs):
        async for event in self.engine.turn_stream(text):
            if event["type"] == "done":
                # Mock the old event structure
                yield {
                    "event_type": "turn_finished",
                    "payload": {"result": ChatTurnResult(TurnResult(
                        message=event["message"],
                        signals=Signals(context=event["context"], risk=1.0 if event["blocked"] else 0.0),
                        evaluation=None, # Simplified for bridge
                        perception_raw={"reason": event.get("reason", "")}
                    ))}
                }
            elif event["type"] == "token":
                yield {
                    "event_type": "thought_stream",
                    "payload": {"chunk": event["content"]}
                }

    def process_chat_turn(self, text: str, **kwargs) -> ChatTurnResult:
        import asyncio
        return asyncio.run(self.process_chat_turn_async(text, **kwargs))

    def dao_status(self) -> str:
        return "DAO Status: V2 Migration in progress (Governance Offline)"

    async def execute_sleep(self) -> str:
        return "Psi Sleep: Maintenance cycle completed (V2 Minimal)."

# Legacy Aliases
EthicalKernel = EthosKernel

__all__ = ["EthosKernel", "EthicalKernel", "ChatTurnResult"]
