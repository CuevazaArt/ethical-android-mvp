"""Bloque 22.2 — ``build_sync_identity_ws_message`` envelope for Nomad PWA."""

from __future__ import annotations

import pytest

from src.chat_server import build_sync_identity_ws_message
from src.kernel import EthosKernel


@pytest.mark.asyncio
async def test_build_sync_identity_ws_message_schema() -> None:
    k = EthosKernel(mode="office_2")
    await k.start()
    try:
        env = build_sync_identity_ws_message(k)
    finally:
        await k.stop()

    assert env.get("type") == "[SYNC_IDENTITY]"
    assert env.get("schema") == "sync_identity_v1"
    pl = env.get("payload")
    assert isinstance(pl, dict)
    assert isinstance(pl.get("gestalt_snapshot"), dict)
    assert "pad_state" in pl["gestalt_snapshot"]
    assert isinstance(pl.get("base_history"), list)
