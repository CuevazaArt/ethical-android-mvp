"""Public governance and discovery GET routes (Bloque 34.1)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..chat_settings import chat_server_settings
from ..modules.buffer import PreloadedBuffer
from ..modules.moral_hub import (
    constitution_snapshot,
    dao_governance_api_enabled,
    moral_hub_public_enabled,
)
from ..modules.nomad_discovery import (
    build_nomad_discovery_payload,
    nomad_discovery_service_name,
    nomad_discovery_service_type,
)

router = APIRouter(tags=["governance"])


@router.get("/discovery/nomad")
def nomad_discovery(request: Request) -> dict[str, Any]:
    """Bloque 14.1: endpoint consumido por PWA para auto-descubrimiento LAN."""
    st = chat_server_settings()
    host = request.url.hostname or st.chat_host
    scheme = request.url.scheme or "http"
    announcer = getattr(request.app.state, "nomad_discovery_announcer", None)
    return build_nomad_discovery_payload(
        request_host=host,
        request_scheme=scheme,
        bind_host=st.chat_host,
        bind_port=st.chat_port,
        mdns_registered=bool(getattr(announcer, "registered", False)),
        mdns_service_name=nomad_discovery_service_name(),
        mdns_service_type=nomad_discovery_service_type(),
    )


@router.get("/dao/governance")
def dao_governance_meta() -> dict[str, Any]:
    """V12.3 — whether DAO vote pipeline is enabled and which WebSocket JSON keys to use."""
    return {
        "enabled": dao_governance_api_enabled(),
        "transport": "websocket",
        "path": "/ws/chat",
        "env": "KERNEL_MORAL_HUB_DAO_VOTE",
        "messages": {
            "dao_list": True,
            "dao_submit_draft": {"level": 1, "draft_id": "uuid"},
            "dao_vote": {
                "proposal_id": "PROP-0001",
                "participant_id": "community_01",
                "n_votes": 1,
                "in_favor": True,
            },
            "dao_resolve": {"proposal_id": "PROP-0001"},
        },
        "note": "Governance runs on the per-connection kernel; use participants from MockDAO (e.g. community_01).",
    }


@router.get("/constitution")
def constitution_public() -> JSONResponse:
    """
    Read-only Level-0 ethical principles (current PreloadedBuffer) as JSON.

    Enabled when KERNEL_MORAL_HUB_PUBLIC=1. Does not expose L1/L2 drafts until governance exists.
    See docs/proposals/README.md (DemocraticBuffer vision).
    """
    if not moral_hub_public_enabled():
        return JSONResponse(
            {"error": "disabled", "hint": "set KERNEL_MORAL_HUB_PUBLIC=1"},
            status_code=404,
        )
    return JSONResponse(constitution_snapshot(PreloadedBuffer()))
