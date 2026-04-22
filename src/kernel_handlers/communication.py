Streaming communication hooks for :meth:`~src.kernel.EthosKernel.process_chat_turn_stream`.

MER / bridge-phrase expansion can replace these no-op defaults in full deployments.

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any


async def get_bridge_phrase(
    kernel: Any,
    stage: Any,
    decision: Any,
    user_input: str,
    agent_id: str,
) -> str | None:
    del kernel, stage, decision, user_input, agent_id
    return None


async def run_communication_stream(
    kernel: Any,
    decision: Any,
    user_input: str,
    conv: str,
    vitality_context: Any = None,
) -> AsyncGenerator[str, None]:
    del kernel, decision, user_input, conv, vitality_context
    if False:  # pragma: no cover — empty async generator
        yield ""
