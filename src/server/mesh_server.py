# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
MeshServer — WebSocket endpoint for the Nomad Physical Mesh protocol.

Handles two frame types from Android mesh nodes:
  - Text (JSON):  TelemetryPayload — periodic hardware snapshots.
  - Binary:       AudioChunkPayload — [4B header_len LE][JSON header][PCM bytes].

Active nodes are tracked in a dict keyed by device_id so that future
routing (broadcast, unicast, load-balancing) can address individual nodes.
"""

from __future__ import annotations

import json
import logging
import struct
import time
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.core.models.mesh_models import AudioChunkHeader, TelemetryPayload

_log = logging.getLogger("ethos.mesh")

# ── Active Node Registry ───────────────────────────────────────


@dataclass
class MeshNode:
    """Runtime state for a connected mesh node."""

    device_id: str
    websocket: WebSocket
    connected_at: float = field(default_factory=time.time)
    last_telemetry: dict[str, Any] | None = None
    audio_chunks_received: int = 0


# Global registry — keyed by device_id.
_active_nodes: dict[str, MeshNode] = {}

# ── Router ─────────────────────────────────────────────────────

router = APIRouter()


@router.websocket("/ws/mesh")
async def websocket_mesh(websocket: WebSocket) -> None:
    await websocket.accept()

    device_id: str | None = None
    node: MeshNode | None = None

    try:
        while True:
            message = await websocket.receive()
            msg_type = message.get("type", "")

            # ── Text frame (JSON) ──────────────────────────────
            if msg_type == "websocket.receive" and "text" in message:
                raw_text: str = message["text"]
                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError:
                    _log.warning("[MESH] Malformed JSON from %s", device_id or "unknown")
                    continue

                frame_type = data.get("type", "")

                if frame_type == "telemetry":
                    _handle_telemetry(data, websocket)
                    # Lazily register the node on first telemetry.
                    if device_id is None:
                        device_id = data.get("device_id", "unknown")
                        node = MeshNode(device_id=device_id, websocket=websocket)
                        _active_nodes[device_id] = node
                        _log.info(
                            "[MESH] Node registered: %s (total: %d)", device_id, len(_active_nodes)
                        )
                    if node is not None:
                        node.last_telemetry = data

                elif frame_type == "discovery":
                    _log.info(
                        "[MESH] Discovery from %s: %s",
                        data.get("device_id"),
                        data.get("capabilities"),
                    )

                elif frame_type == "ping":
                    await websocket.send_json(
                        {"type": "pong", "timestamp_ms": int(time.time() * 1000)}
                    )

                else:
                    _log.debug("[MESH] Unknown text frame type '%s' from %s", frame_type, device_id)

            # ── Binary frame (Audio) ───────────────────────────
            elif msg_type == "websocket.receive" and "bytes" in message:
                raw_bytes: bytes = message["bytes"]
                _handle_audio_binary(raw_bytes, device_id, node)

    except WebSocketDisconnect:
        _log.info("[MESH] Node disconnected: %s", device_id or "unknown")
    except Exception:
        _log.exception("[MESH] Unexpected error on node %s", device_id or "unknown")
    finally:
        if device_id and device_id in _active_nodes:
            del _active_nodes[device_id]
            _log.info("[MESH] Node removed: %s (remaining: %d)", device_id, len(_active_nodes))


# ── Frame Handlers ─────────────────────────────────────────────


def _handle_telemetry(data: dict[str, Any], websocket: WebSocket) -> None:
    """Parse and log a telemetry frame."""
    try:
        payload = TelemetryPayload.from_dict(dict(data))  # defensive copy — from_dict pops keys
        _log.info(
            "[MESH/TELEM] %s — battery=%.0f%% charging=%s cpu=%.1f°C ram=%s/%sMB",
            payload.device_id,
            payload.battery.level * 100,
            payload.battery.is_charging,
            payload.cpu.temperature_c,
            payload.memory.available_mb if payload.memory else "?",
            payload.memory.total_mb if payload.memory else "?",
        )
    except Exception:
        _log.exception("[MESH/TELEM] Failed to parse telemetry")


def _handle_audio_binary(raw: bytes, device_id: str | None, node: MeshNode | None) -> None:
    """
    Decode an AudioChunkPayload binary frame.

    Wire format:
      [4 bytes: header_length as uint32 LE]
      [header_length bytes: JSON header (UTF-8)]
      [remaining bytes: raw PCM audio]
    """
    if len(raw) < 4:
        _log.warning("[MESH/AUDIO] Binary frame too short (%d bytes) from %s", len(raw), device_id)
        return

    header_length = struct.unpack("<I", raw[:4])[0]

    if header_length > 65536 or header_length > len(raw) - 4:
        _log.warning(
            "[MESH/AUDIO] Invalid header_length=%d (frame=%d bytes) from %s",
            header_length,
            len(raw),
            device_id,
        )
        return

    try:
        header_json = raw[4 : 4 + header_length].decode("utf-8")
        header_data = json.loads(header_json)
        header = AudioChunkHeader.from_dict(header_data)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError, KeyError) as exc:
        _log.warning("[MESH/AUDIO] Malformed audio header from %s: %s", device_id, exc)
        return

    pcm_bytes = raw[4 + header_length :]
    pcm_len = len(pcm_bytes)

    if pcm_len != header.pcm_length_bytes:
        _log.warning(
            "[MESH/AUDIO] PCM length mismatch: header says %d, got %d from %s",
            header.pcm_length_bytes,
            pcm_len,
            device_id,
        )

    _log.info(
        "[MESH/AUDIO] %s seq=%d — %d bytes PCM @ %dHz",
        header.device_id,
        header.seq,
        pcm_len,
        header.sample_rate_hz,
    )

    if node is not None:
        node.audio_chunks_received += 1

    # Future: feed pcm_bytes into the audio processing pipeline.


# ── Utility ────────────────────────────────────────────────────


def get_active_nodes() -> list[dict[str, Any]]:
    """Returns a snapshot of all connected mesh nodes for telemetry/dashboard."""
    return [
        {
            "device_id": n.device_id,
            "connected_at": n.connected_at,
            "audio_chunks": n.audio_chunks_received,
            "last_battery": (n.last_telemetry or {}).get("battery", {}).get("level"),
        }
        for n in _active_nodes.values()
    ]
