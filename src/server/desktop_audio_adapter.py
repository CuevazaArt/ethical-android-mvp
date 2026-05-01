from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any

CONTRACT_VERSION = "1.0"
AUDIO_CONTRACT = "audio_perception"
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 96000


@dataclass(frozen=True)
class ContractError:
    code: str
    message: str
    retryable: bool


@dataclass(frozen=True)
class AudioPerceptionRequest:
    audio_b64: str
    sample_rate_hz: int
    request_payload: dict[str, Any]


def safe_latency_ms(start_time: float) -> float:
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    if not math.isfinite(elapsed_ms) or elapsed_ms < 0:
        return 0.0
    return round(elapsed_ms, 2)


def build_error_envelope(
    *,
    request_payload: dict[str, Any],
    error: ContractError,
    latency_ms: float,
) -> dict[str, Any]:
    return {
        "version": CONTRACT_VERSION,
        "contract": AUDIO_CONTRACT,
        "request": request_payload,
        "response": {"transcript": "", "confidence": 0.0},
        "error": {
            "code": error.code,
            "message": error.message,
            "retryable": error.retryable,
        },
        "latency_ms": latency_ms
        if math.isfinite(latency_ms) and latency_ms >= 0
        else 0.0,
    }


def build_success_envelope(
    *,
    request_payload: dict[str, Any],
    transcript: str,
    confidence: float,
    latency_ms: float,
) -> dict[str, Any]:
    safe_conf = float(confidence) if math.isfinite(float(confidence)) else 0.0
    safe_conf = max(0.0, min(1.0, safe_conf))
    return {
        "version": CONTRACT_VERSION,
        "contract": AUDIO_CONTRACT,
        "request": request_payload,
        "response": {
            "transcript": transcript,
            "confidence": safe_conf,
        },
        "error": None,
        "latency_ms": latency_ms
        if math.isfinite(latency_ms) and latency_ms >= 0
        else 0.0,
    }


def parse_audio_perception_payload(
    payload: Any,
) -> tuple[AudioPerceptionRequest | None, ContractError | None]:
    if not isinstance(payload, dict):
        return None, ContractError(
            code="INVALID_PAYLOAD",
            message="Payload must be a JSON object.",
            retryable=False,
        )

    request_payload = payload.get("request", {})
    version = payload.get("version")
    contract = payload.get("contract")

    if version != CONTRACT_VERSION:
        return None, ContractError(
            code="INVALID_VERSION",
            message=f"Expected version '{CONTRACT_VERSION}'.",
            retryable=False,
        )

    if contract != AUDIO_CONTRACT:
        return None, ContractError(
            code="INVALID_CONTRACT",
            message=f"Expected contract '{AUDIO_CONTRACT}'.",
            retryable=False,
        )

    if not isinstance(request_payload, dict):
        return None, ContractError(
            code="INVALID_REQUEST",
            message="'request' must be an object.",
            retryable=False,
        )

    audio_b64 = request_payload.get("audio_b64")
    sample_rate_hz = request_payload.get("sample_rate_hz")

    if not isinstance(audio_b64, str):
        return None, ContractError(
            code="INVALID_AUDIO_B64",
            message="'audio_b64' must be a base64 string.",
            retryable=False,
        )

    if not audio_b64.strip():
        return None, ContractError(
            code="AUDIO_DEVICE_UNAVAILABLE",
            message="No audio payload received. Check microphone permissions/device.",
            retryable=True,
        )

    try:
        sample_rate_int = int(sample_rate_hz)
    except (TypeError, ValueError):
        return None, ContractError(
            code="INVALID_SAMPLE_RATE",
            message="'sample_rate_hz' must be an integer between 8000 and 96000.",
            retryable=False,
        )

    if sample_rate_int < MIN_SAMPLE_RATE_HZ or sample_rate_int > MAX_SAMPLE_RATE_HZ:
        return None, ContractError(
            code="INVALID_SAMPLE_RATE",
            message="'sample_rate_hz' must be between 8000 and 96000.",
            retryable=False,
        )

    return (
        AudioPerceptionRequest(
            audio_b64=audio_b64,
            sample_rate_hz=sample_rate_int,
            request_payload=request_payload,
        ),
        None,
    )
