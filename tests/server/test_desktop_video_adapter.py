from __future__ import annotations

import base64
import math

import cv2
import numpy as np

from src.core.vision import VisionSignals
from src.server.desktop_video_adapter import DesktopVideoAdapter


def _make_frame_b64(color: tuple[int, int, int] = (128, 128, 128)) -> str:
    frame = np.full((240, 320, 3), color, dtype=np.uint8)
    ok, jpeg = cv2.imencode(".jpg", frame)
    assert ok
    return base64.b64encode(jpeg.tobytes()).decode()


def test_process_video_frame_builds_contract_and_context() -> None:
    adapter = DesktopVideoAdapter()
    result = adapter.process_video_frame(
        {
            "image_b64": _make_frame_b64(),
            "frame_format": "jpeg",
            "width": 320,
            "height": 240,
        }
    )
    assert result.envelope["contract"] == "video_perception"
    assert result.envelope["version"] == "1.0"
    assert result.envelope["error"] is None
    assert math.isfinite(float(result.envelope["latency_ms"]))
    assert result.vision_context is not None
    assert math.isfinite(float(result.vision_context["motion"]))
    assert isinstance(result.vision_context["faces_detected"], int)


def test_process_video_frame_deterministic_motion_and_faces(monkeypatch) -> None:
    adapter = DesktopVideoAdapter()

    monkeypatch.setattr(
        adapter._vision,
        "process_b64",
        lambda _: VisionSignals(
            brightness=0.42,
            motion=0.67,
            faces_detected=2,
            face_present=True,
            low_light=False,
            latency_ms=12.0,
        ),
    )
    result = adapter.process_video_frame({"image_b64": "stub", "width": 320, "height": 240})
    assert result.envelope["error"] is None
    assert result.envelope["response"]["motion"] == 0.67
    assert result.envelope["response"]["faces_detected"] == 2
    assert "motion" in result.envelope["response"]["labels"]
    assert "face_present" in result.envelope["response"]["labels"]


def test_process_video_frame_rejects_non_finite_metrics(monkeypatch) -> None:
    adapter = DesktopVideoAdapter()

    monkeypatch.setattr(
        adapter._vision,
        "process_b64",
        lambda _: VisionSignals(
            brightness=0.50,
            motion=float("inf"),
            faces_detected=1,
            face_present=True,
            low_light=False,
            latency_ms=15.0,
        ),
    )
    result = adapter.process_video_frame({"image_b64": "stub", "width": 320, "height": 240})
    assert result.vision_context is None
    assert result.envelope["error"] is not None
    assert result.envelope["error"]["code"] == "NON_FINITE_METRIC"
