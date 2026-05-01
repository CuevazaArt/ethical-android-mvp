from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any

from src.core.vision import VisionEngine


def _safe_non_negative_int(value: Any, *, default: int = 0) -> int:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(numeric) or numeric < 0.0:
        return default
    return int(numeric)


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


def _strict_bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        if float(value) == 1.0:
            return True
        if float(value) == 0.0:
            return False
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n", ""}:
            return False
    return None


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

        brightness_raw = payload.get("brightness")
        motion_raw = payload.get("motion")
        faces_raw = payload.get("faces_detected")
        latency_raw = payload.get("latency_ms")

        brightness = _finite01(brightness_raw)
        motion = _finite01(motion_raw)
        faces_detected = _finite_non_negative_int(faces_raw)
        latency_ms = _finite_non_negative(latency_raw)
        low_light_raw = payload.get("low_light", False)
        face_present_raw = payload.get("face_present", False)
        low_light = _strict_bool_or_none(low_light_raw)
        face_present = _strict_bool_or_none(face_present_raw)

        if brightness_raw is not None and brightness is None:
            return None
        if motion_raw is not None and motion is None:
            return None
        if faces_raw is not None and faces_detected is None:
            return None
        if latency_raw is not None and latency_ms is None:
            return None
        if low_light is None or face_present is None:
            return None

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
        width = _safe_non_negative_int(request.get("width", 0), default=0)
        height = _safe_non_negative_int(request.get("height", 0), default=0)

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
            "frame_b64": str(
                request.get("image_b64") or request.get("frame_b64") or ""
            ),
            "frame_format": str(request.get("frame_format", "jpeg")).lower(),
            "width": _safe_non_negative_int(request.get("width", 0), default=0),
            "height": _safe_non_negative_int(request.get("height", 0), default=0),
        }
        safe_elapsed = (
            elapsed_ms if math.isfinite(elapsed_ms) and elapsed_ms >= 0 else 0.0
        )
        return {
            "version": "1.0",
            "contract": "video_perception",
            "request": request_envelope,
            "response": {"labels": [], "motion": 0.0, "faces_detected": 0},
            "error": {"code": code, "message": message, "retryable": retryable},
            "latency_ms": safe_elapsed,
        }
