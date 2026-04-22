"""
Bloque 34.4: build src/server/ws_chat.py and trim src/chat_server.py.
Run from repo root: python scripts/build_bloque_34_4_ws_chat.py
"""

from __future__ import annotations

from pathlib import Path

WS_CHAT_HEADER = '''"""Core WebSocket chat: ``/ws/chat`` and turn JSON (Bloque 34.4)."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import threading
import time
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..kernel import ChatTurnResult, EthicalKernel
from ..kernel_utils import kernel_dao_as_mock
from src.modules.somatic.affective_homeostasis import homeostasis_telemetry
from src.modules.cognition.consequence_projection import qualitative_temporal_branches
from src.modules.safety.guardian_mode import (
    is_guardian_mode_active,
    public_routines_snapshot,
)
from ..modules.internal_monologue import compose_monologue_line
from src.modules.ethics.ml_ethics_tuner import maybe_log_gray_zone_tuning_opportunity
from src.modules.governance.moral_hub import (
    add_constitution_draft,
    audit_transparency_event,
    constitution_draft_ws_enabled,
    ethos_payroll_record_mock,
)
from src.modules.governance.nomad_identity import nomad_identity_public
from src.modules.perception.perception_schema import perception_report_from_dict
from src.modules.perception.perceptual_abstraction import snapshot_from_layers
from src.modules.perception.sensor_contracts import SensorPayloadValidationError
from ..observability.context import clear_request_context, set_request_id
from ..observability.metrics import (
    observe_chat_turn,
    record_chat_turn_async_timeout,
    record_llm_cancel_scope_signaled,
    record_malabs_block,
)
from ..persistence.checkpoint import (
    checkpoint_persistence_from_env,
    init_session_checkpoint_state,
    maybe_autosave_episodes,
    on_websocket_session_end,
    try_load_checkpoint,
)
from ..real_time_bridge import RealTimeBridge
from ..runtime.chat_feature_flags import (
    chat_expose_monologue,
    chat_include_chrono,
    chat_include_constitution,
    chat_include_epistemic,
    chat_include_experience_digest,
    chat_include_guardian,
    chat_include_guardian_routines,
    chat_include_homeostasis,
    chat_include_judicial,
    chat_include_light_risk,
    chat_include_malabs_trace,
    chat_include_multimodal_trust,
    chat_include_nomad_identity,
    chat_include_premise,
    chat_include_reality_verification,
    chat_include_teleology,
    chat_include_transparency_s10,
    chat_include_user_model,
    chat_include_vitality,
    coerce_public_int,
    env_truthy,
)
from ..runtime.telemetry import advisory_interval_seconds_from_env, advisory_loop
from .identity_envelope import build_sync_identity_ws_message, identity_state_public_dict
from .lan_governance_ws import (
    DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
    DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
    _merge_lan_governance_ws_payloads,
)
from .ws_governance import (
    _collect_dao_ws_actions,
    _collect_integrity_ws_action,
    _collect_lan_governance_coordinator,
    _collect_lan_governance_dao_batch,
    _collect_lan_governance_envelope,
    _collect_lan_governance_integrity_batch,
    _collect_lan_governance_judicial_batch,
    _collect_lan_governance_mock_court_batch,
    _collect_nomad_ws_actions,
)

logger = logging.getLogger(__name__)

router = APIRouter()


'''


def _patch_body(body: str) -> str:
    body = body.replace("_identity_state_public_dict(", "identity_state_public_dict(")
    body = body.replace("from .settings import kernel_settings", "from ..settings import kernel_settings")
    body = body.replace("from .modules.perception.nomad_bridge", "from src.modules.perception.nomad_bridge")
    body = body.replace("from src.modules.safety.transparency_s10", "from src.modules.safety.transparency_s10")
    # Only the chat route decorator
    if "@app.websocket" in body:
        body = body.replace("@app.websocket", "@router.websocket", 1)
    return body


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cs = root / "src" / "chat_server.py"
    lines = cs.read_text(encoding="utf-8").splitlines(keepends=True)
    n = len(lines)
    if n < 2420:
        raise SystemExit(f"chat_server.py too short: {n} lines (need >= 2420)")

    # 0-based: lines 537-912 -> [536:912] — _tri_lobe .. end of _chat_turn_to_jsonable (return out)
    # 0-based: lines 2027-2421 -> [2026:2421] — @app /ws/chat .. end of ws_chat (before get_uvicorn)
    part_a = "".join(lines[536:912])
    part_b = "".join(lines[2026:2421])
    if "def _tri_lobe_chat_ws_contract_defaults" not in part_a or "async def ws_chat" not in part_b:
        raise SystemExit("unexpected extract — marker strings missing")

    body = _patch_body(part_a + part_b)
    (root / "src" / "server" / "ws_chat.py").write_text(WS_CHAT_HEADER + body, encoding="utf-8")
    print("Wrote src/server/ws_chat.py")

    new_lines = lines[:322] + lines[2421:]
    s = "".join(new_lines)
    if "def get_uvicorn_bind" not in s:
        raise SystemExit("splice failed: get_uvicorn_bind not in result")

    # Inject imports and includes after the field_control import line
    needle_import = "from .server.routes_field_control import router as field_control_http_router\n"
    inject_imports = (
        "from .server.ws_chat import _chat_turn_to_jsonable, router as ws_chat_router\n"
        "from .server.ws_sidecar import router as ws_sidecar_router\n"
    )
    if needle_import not in s:
        raise SystemExit("field_control import not found")
    s = s.replace(needle_import, needle_import + inject_imports, 1)

    needle_incl = "app.include_router(field_control_http_router)\n"
    inject_incl = (
        "app.include_router(field_control_http_router)\n"
        "app.include_router(ws_sidecar_router)\n"
        "app.include_router(ws_chat_router)\n"
    )
    s = s.replace(needle_incl, inject_incl, 1)

    cs.write_text(s, encoding="utf-8")
    print("Updated src/chat_server.py, new length", len(s.splitlines()), "lines")


if __name__ == "__main__":
    main()
