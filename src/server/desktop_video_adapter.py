from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any

from src.core.vision import VisionEngine, VisionSignals


def _finite01(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric):
        return None
    return max(0.0, min(1.0, numeric))


def _finite_non_negative(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric) or numeric < 0.0:
        return None
    return numeric


def _finite_non_negative_int(value: Any) -> int | None:
    finite = _finite_non_negative(value)
    if finite is None:
        return None
    return int(finite)


@dataclass
class VideoPerceptionResult:
    envelope: dict[str, Any]
    vision_context: dict[str, Any] | None


class DesktopVideoAdapter:
    """Desktop camera frame -> contract envelope + sanitized vision context."""

    def __init__(self, vision_engine: VisionEngine | None = None) -> None:
        self._vision = vision_engine if vision_engine is not None else VisionEngine()

    def sanitize_vision_context(self, payload: Any) -> dict[str, Any] | None:
        if not isinstance(payload, dict):
            return None

        brightness = _finite01(payload.get("brightness"))
        motion = _finite01(payload.get("motion"))
        faces_detected = _finite_non_negative_int(payload.get("faces_detected"))
        latency_ms = _finite_non_negative(payload.get("latency_ms"))
        low_light = bool(payload.get("low_light", False))
        face_present = bool(payload.get("face_present", False))

        if brightness is None and motion is None and faces_detected is None:
            return None

        if faces_detected is not None and faces_detected > 0:
            face_present = True

        return {
            "brightness": brightness if brightness is not None else 0.0,
            "motion": motion if motion is not None else 0.0,
            "faces_detected": faces_detected if faces_detected is not None else 0,
            "face_present": face_present,
            "low_light": low_light,
            "latency_ms": latency_ms if latency_ms is not None else 0.0,
        }

    def _labels_from_signals(self, signals: dict[str, Any]) -> list[str]:
        labels: list[str] = []
        if signals["motion"] > 0.15:
            labels.append("motion")
        if signals["faces_detected"] > 0:
            labels.append("face_present")
        if signals["low_light"]:
            labels.append("low_light")
        return labels

    def process_video_frame(self, payload: Any) -> VideoPerceptionResult:
        t0 = time.perf_counter()
        request = payload if isinstance(payload, dict) else {}
        frame_b64 = request.get("image_b64") or request.get("frame_b64") or ""
        frame_format = str(request.get("frame_format", "jpeg")).lower()
        width = int(request.get("width", 0) or 0)
        height = int(request.get("height", 0) or 0)

        if not isinstance(frame_b64, str) or not frame_b64.strip():
            return VideoPerceptionResult(
                envelope=self._error_envelope(
                    code="EMPTY_FRAME",
                    message="video frame payload is empty",
                    retryable=True,
                    request=request,
                    elapsed_ms=(time.perf_counter() - t0) * 1000.0,
                ),
                vision_context=None,
            )

        sig = self._vision.process_b64(frame_b64)
        if sig is None:
            return VideoPerceptionResult(
                envelope=self._error_envelope(
                    code="FRAME_DECODE_FAILED",
                    message="could not decode desktop frame",
                    retryable=True,
                    request=request,
                    elapsed_ms=(time.perf_counter() - t0) * 1000.0,
                ),
                vision_context=None,
            )

        vision_context = self.sanitize_vision_context(sig.to_dict())
        if vision_context is None:
            return VideoPerceptionResult(
                envelope=self._error_envelope(
                    code="NON_FINITE_METRIC",
                    message="video metrics are non-finite or invalid",
                    retryable=True,
                    request=request,
                    elapsed_ms=(time.perf_counter() - t0) * 1000.0,
                ),
                vision_context=None,
            )

        labels = self._labels_from_signals(vision_context)
        response = {
            "labels": labels,
            "motion": vision_context["motion"],
            "faces_detected": vision_context["faces_detected"],
        }
        request_envelope = {
            "frame_b64": frame_b64,
            "frame_format": frame_format if frame_format in {"jpeg", "png"} else "jpeg",
            "width": width if width > 0 else 1,
            "height": height if height > 0 else 1,
        }
        latency_ms = (time.perf_counter() - t0) * 1000.0
        envelope = {
            "version": "1.0",
            "contract": "video_perception",
            "request": request_envelope,
            "response": response,
            "error": None,
            "latency_ms": latency_ms if math.isfinite(latency_ms) else 0.0,
        }
        return VideoPerceptionResult(envelope=envelope, vision_context=vision_context)

    def _error_envelope(
        self,
        *,
        code: str,
        message: str,
        retryable: bool,
        request: dict[str, Any],
        elapsed_ms: float,
    ) -> dict[str, Any]:
        request_envelope = {
            "frame_b64": str(request.get("image_b64") or request.get("frame_b64") or ""),
            "frame_format": str(request.get("frame_format", "jpeg")).lower(),
            "width": int(request.get("width", 0) or 0),
            "height": int(request.get("height", 0) or 0),
        }
        safe_elapsed = elapsed_ms if math.isfinite(elapsed_ms) and elapsed_ms >= 0 else 0.0
        return {
            "version": "1.0",
            "contract": "video_perception",
            "request": request_envelope,
            "response": {"labels": [], "motion": 0.0, "faces_detected": 0},
            "error": {"code": code, "message": message, "retryable": retryable},
            "latency_ms": safe_elapsed,
        }
