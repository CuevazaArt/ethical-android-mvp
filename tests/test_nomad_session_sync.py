"""Bloque 22.2 — ``nomad_session_sync`` payload shape for Nomad PWA."""

from __future__ import annotations

import pytest
from src.kernel import EthosKernel
from src.modules.nomad_session_sync import build_sync_identity_payload


@pytest.mark.asyncio
async def test_build_sync_identity_payload_schema() -> None:
    k = EthosKernel(mode="office_2")
    await k.start()
    try:
        body = build_sync_identity_payload(k)
    finally:
        await k.stop()

    assert body.get("schema") == "sync_identity_v1"
    assert isinstance(body.get("gestalt"), dict)
    assert "pad_state" in body["gestalt"]
    assert isinstance(body.get("base_history"), list)
    assert isinstance(body.get("narrative_identity"), dict)
    assert "ascription" in body
