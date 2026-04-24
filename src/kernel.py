"""
Ethos Kernel — V2 Bridge (Legacy Compatibility Shim)

Exposes EthosKernel / EthicalKernel backed by the new V2 ChatEngine.
Used by legacy scripts (adversarial_suite.py, etc.) until they are
migrated to call src.core.chat.ChatEngine directly.
"""

from __future__ import annotations

import logging
from src.core.chat import ChatEngine, TurnResult
from src.core.ethics import Signals

_log = logging.getLogger(__name__)


class _ResponseShim:
    def __init__(self, message: str):
        self.message = message
        self.tone = "neutral"


class ChatTurnResult:
    """Minimal shim matching the legacy KernelTurnResult API."""
    def __init__(self, res: TurnResult):
        self.response = _ResponseShim(res.message)
        self.path = "v2_core"
        self.blocked = res.perception_raw.get("blocked", False)
        self.block_reason = res.perception_raw.get("reason", "")
        self.weighted_score = res.evaluation.score if res.evaluation else 0.0
        self.verdict = res.evaluation.verdict if res.evaluation else "Good"
        self.signals = res.signals


class EthosKernel:
    """V2 shim — wraps ChatEngine with the legacy EthosKernel API."""

    def __init__(self, **_kwargs) -> None:
        self.engine = ChatEngine()
        self.memory = self.engine.memory

    async def start(self) -> None:
        await self.engine.start()

    async def stop(self) -> None:
        await self.engine.close()

    async def process_chat_turn_stream(self, text: str, **_kw):
        async for event in self.engine.turn_stream(text):
            if event["type"] == "done":
                result = ChatTurnResult(TurnResult(
                    message=event["message"],
                    signals=Signals(
                        context=event["context"],
                        risk=1.0 if event["blocked"] else 0.0,
                    ),
                    evaluation=None,
                    perception_raw={
                        "blocked": event["blocked"],
                        "reason": event.get("reason", ""),
                    },
                ))
                yield {"event_type": "turn_finished", "payload": {"result": result}}
            elif event["type"] == "token":
                yield {"event_type": "thought_stream", "payload": {"chunk": event["content"]}}

    def dao_status(self) -> str:
        return "DAO: V2 Core (governance offline)"

    async def execute_sleep(self) -> str:
        return "Psi Sleep: V2 maintenance cycle complete."


# Legacy alias
EthicalKernel = EthosKernel

__all__ = ["EthosKernel", "EthicalKernel", "ChatTurnResult"]
