"""V2.120 (A2): contract envelope helpers for the desktop voice_turn endpoint.

The voice_turn capability is the first text-mediated path that satisfies the
`DESKTOP_CONTRACT_SPINE_V1.md` shape without requiring captured audio. It lets
operators measure the cognitive turn (LLM + ethics) latency on hardware that
lacks microphone/speaker pipelines, which unblocks G2 evaluation under the
`text_mediated` mode introduced in V2.127.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.server.desktop_audio_adapter import (
    CONTRACT_VERSION,
    ContractError,
    safe_latency_ms,
)

VOICE_TURN_CONTRACT = "voice_turn"
MAX_UTTERANCE_LENGTH = 2000

__all__ = [
    "VOICE_TURN_CONTRACT",
    "CONTRACT_VERSION",
    "ContractError",
    "safe_latency_ms",
    "VoiceTurnRequest",
    "parse_voice_turn_payload",
    "build_voice_turn_error_envelope",
    "build_voice_turn_success_envelope",
]


@dataclass(frozen=True)
class VoiceTurnRequest:
    utterance: str
    request_payload: dict[str, Any]


def parse_voice_turn_payload(
    payload: Any,
) -> tuple[VoiceTurnRequest | None, ContractError | None]:
    """Validate the request envelope and return a typed request or contract error."""

    if not isinstance(payload, dict):
        return None, ContractError(
            code="INVALID_PAYLOAD",
            message="Payload must be a JSON object.",
            retryable=False,
        )

    version = payload.get("version")
    contract = payload.get("contract")
    request_payload = payload.get("request", {})

    if version != CONTRACT_VERSION:
        return None, ContractError(
            code="INVALID_VERSION",
            message=f"Expected version '{CONTRACT_VERSION}'.",
            retryable=False,
        )

    if contract != VOICE_TURN_CONTRACT:
        return None, ContractError(
            code="INVALID_CONTRACT",
            message=f"Expected contract '{VOICE_TURN_CONTRACT}'.",
            retryable=False,
        )

    if not isinstance(request_payload, dict):
        return None, ContractError(
            code="INVALID_REQUEST",
            message="'request' must be an object.",
            retryable=False,
        )

    utterance = request_payload.get("utterance")
    if not isinstance(utterance, str):
        return None, ContractError(
            code="INVALID_UTTERANCE",
            message="'utterance' must be a string.",
            retryable=False,
        )

    cleaned = utterance.strip()
    if not cleaned:
        return None, ContractError(
            code="EMPTY_UTTERANCE",
            message="'utterance' must not be empty after trimming.",
            retryable=False,
        )

    if len(cleaned) > MAX_UTTERANCE_LENGTH:
        return None, ContractError(
            code="UTTERANCE_TOO_LONG",
            message=(
                f"'utterance' exceeds maximum length of {MAX_UTTERANCE_LENGTH} "
                "characters."
            ),
            retryable=False,
        )

    return (
        VoiceTurnRequest(utterance=cleaned, request_payload=request_payload),
        None,
    )


def _safe_latency(latency_ms: float) -> float:
    if not math.isfinite(latency_ms) or latency_ms < 0:
        return 0.0
    return latency_ms


def build_voice_turn_error_envelope(
    *,
    request_payload: dict[str, Any],
    error: ContractError,
    latency_ms: float,
) -> dict[str, Any]:
    return {
        "version": CONTRACT_VERSION,
        "contract": VOICE_TURN_CONTRACT,
        "request": request_payload,
        "response": {"reply_text": "", "should_listen": False},
        "error": {
            "code": error.code,
            "message": error.message,
            "retryable": error.retryable,
        },
        "latency_ms": _safe_latency(latency_ms),
    }


def build_voice_turn_success_envelope(
    *,
    request_payload: dict[str, Any],
    reply_text: str,
    should_listen: bool,
    latency_ms: float,
    audio_b64: str | None = None,
) -> dict[str, Any]:
    response: dict[str, Any] = {
        "reply_text": reply_text,
        "should_listen": bool(should_listen),
    }
    if audio_b64:
        response["audio_b64"] = audio_b64
    return {
        "version": CONTRACT_VERSION,
        "contract": VOICE_TURN_CONTRACT,
        "request": request_payload,
        "response": response,
        "error": None,
        "latency_ms": _safe_latency(latency_ms),
    }
