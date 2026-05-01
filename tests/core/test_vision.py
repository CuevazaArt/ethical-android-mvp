"""Tests for src/core/vision.py — Vision Engine."""

import base64
import math

import cv2
import numpy as np

from src.core.vision import VisionEngine, VisionSignals


def _make_frame_b64(
    color: tuple[int, int, int] = (128, 128, 128), w: int = 320, h: int = 240
) -> str:
    """Generate a synthetic JPEG frame in base64."""
    frame = np.full((h, w, 3), color, dtype=np.uint8)
    _, jpeg = cv2.imencode(".jpg", frame)
    return base64.b64encode(jpeg.tobytes()).decode()


# --- Basic processing ---


def test_process_returns_signals():
    engine = VisionEngine()
    sig = engine.process_b64(_make_frame_b64())
    assert sig is not None
    assert isinstance(sig, VisionSignals)


def test_brightness_bright_frame():
    engine = VisionEngine()
    sig = engine.process_b64(_make_frame_b64(color=(255, 255, 255)))
    assert sig.brightness > 0.9


def test_brightness_dark_frame():
    engine = VisionEngine()
    sig = engine.process_b64(_make_frame_b64(color=(5, 5, 5)))
    assert sig.brightness < 0.1
    assert sig.low_light is True


def test_no_motion_on_first_frame():
    """First frame has no previous to diff against — motion must be 0.0."""
    engine = VisionEngine()
    sig = engine.process_b64(_make_frame_b64())
    assert sig.motion == 0.0


def test_motion_detected_between_frames():
    engine = VisionEngine()
    engine.process_b64(_make_frame_b64(color=(50, 50, 50)))  # frame 1
    sig = engine.process_b64(
        _make_frame_b64(color=(200, 200, 200))
    )  # frame 2 — big diff
    assert sig.motion > 0.0


def test_no_motion_identical_frames():
    engine = VisionEngine()
    b64 = _make_frame_b64(color=(100, 100, 100))
    engine.process_b64(b64)  # frame 1
    sig = engine.process_b64(b64)  # frame 2 — identical
    assert sig.motion < 0.01


# --- Anti-NaN ---


def test_all_signals_finite():
    engine = VisionEngine()
    sig = engine.process_b64(_make_frame_b64())
    assert math.isfinite(sig.brightness)
    assert math.isfinite(sig.motion)
    assert math.isfinite(sig.latency_ms)


# --- Invalid input ---


def test_returns_none_on_invalid_b64():
    engine = VisionEngine()
    assert engine.process_b64("not_valid_base64!!!") is None


def test_returns_none_on_empty():
    engine = VisionEngine()
    assert engine.process_b64("") is None


# --- to_dict ---


def test_to_dict_has_required_keys():
    sig = VisionSignals(brightness=0.5, motion=0.1, faces_detected=1, face_present=True)
    d = sig.to_dict()
    for key in (
        "brightness",
        "motion",
        "faces_detected",
        "face_present",
        "low_light",
        "latency_ms",
    ):
        assert key in d


def test_latency_logged():
    engine = VisionEngine()
    sig = engine.process_b64(_make_frame_b64())
    assert sig.latency_ms >= 0.0
