"""
Tests for Bloque 12.0 — Autocalibración Física y Corrección Sensorial

Covers:
- 12.1: RGB/BGR color_space parameter in MobileNetV2Adapter.infer()
- 12.2: SensorBaselineCalibrator warm-up window logic
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# 12.1 — RGB/BGR fix in MobileNetV2Adapter.infer()
# ---------------------------------------------------------------------------

class TestColorSpaceParameter:
    """Verify the color_space parameter prevents the Blue Veil artifact."""

    def test_mock_adapter_returns_inference_for_bgr(self):
        from src.modules.vision_adapter import MobileNetV2Adapter

        adapter = MobileNetV2Adapter()
        # Model NOT loaded → mock path
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        result = adapter.infer(frame, color_space="bgr")
        assert result.primary_label == "unknown (mock)"
        assert result.confidence == 0.0

    def test_mock_adapter_returns_inference_for_rgb(self):
        from src.modules.vision_adapter import MobileNetV2Adapter

        adapter = MobileNetV2Adapter()
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        result = adapter.infer(frame, color_space="rgb")
        assert result.primary_label == "unknown (mock)"

    def test_bgr_and_rgb_produce_different_arrays(self):
        """When model IS ready, BGR and RGB frames with different color channels
        must pass different tensors to the model (no channel inversion on RGB).
        This is validated by checking the PIL image passed downstream."""
        from src.modules.vision_adapter import MobileNetV2Adapter
        from PIL import Image

        captured_images: list[Image.Image] = []

        adapter = MobileNetV2Adapter()
        adapter._is_ready = True
        adapter.model = MagicMock()
        adapter._torch_device = MagicMock()
        adapter.categories = ["cat"]

        # Mock transform to capture the PIL image
        def fake_transform(img: Image.Image):
            captured_images.append(img.copy())
            import torch
            return torch.zeros(3, 224, 224)

        adapter.transform = fake_transform

        # Mock model output
        import torch
        mock_output = MagicMock()
        mock_softmax = torch.tensor([1.0])
        mock_conf = torch.tensor(1.0)
        mock_idx = torch.tensor(0)
        adapter.model.return_value = MagicMock()

        # Patch torch operations used inside infer
        with patch("torch.nn.functional.softmax") as mock_sm, \
             patch("torch.max") as mock_max, \
             patch("torch.topk") as mock_topk, \
             patch("torch.no_grad"):
            mock_sm.return_value = mock_softmax
            mock_max.return_value = (mock_conf, mock_idx)
            mock_topk.return_value = (torch.tensor([1.0]), torch.tensor([0]))

            # BGR frame: pure red in BGR = (0, 0, 255)
            bgr_frame = np.zeros((4, 4, 3), dtype=np.uint8)
            bgr_frame[:, :, 2] = 255  # Blue channel in BGR = Red visually

            adapter.infer(bgr_frame, color_space="bgr")
            bgr_pil = captured_images[-1]

            adapter.infer(bgr_frame, color_space="rgb")
            rgb_pil = captured_images[-1]

        # With color_space="bgr" the frame is flipped, so pixel[0,0] = (255,0,0) RGB
        # With color_space="rgb" no flip, so pixel[0,0] = (0,0,255) RGB
        assert bgr_pil.getpixel((0, 0)) != rgb_pil.getpixel((0, 0)), (
            "BGR and RGB frames should produce different PIL images"
        )

    def test_abstract_signature_accepts_color_space(self):
        """VisionAdapter ABC signature must include color_space."""
        import inspect
        from src.modules.vision_adapter import VisionAdapter
        sig = inspect.signature(VisionAdapter.infer)
        assert "color_space" in sig.parameters, (
            "VisionAdapter.infer must declare color_space parameter"
        )


# ---------------------------------------------------------------------------
# 12.2 — SensorBaselineCalibrator
# ---------------------------------------------------------------------------

@dataclass
class _FakeSnapshot:
    """Minimal duck-type snapshot for calibrator tests."""
    core_temperature: float | None = None
    accelerometer_jerk: float | None = None


class TestSensorBaselineCalibrator:

    def test_not_done_before_window(self):
        from src.modules.sensor_baseline_calibrator import SensorBaselineCalibrator

        cal = SensorBaselineCalibrator(window_seconds=60.0)
        cal.feed(_FakeSnapshot(core_temperature=50.0, accelerometer_jerk=0.1))
        assert not cal.is_done
        assert cal.compute_thresholds() is None

    def test_done_after_window_elapsed(self):
        from src.modules.sensor_baseline_calibrator import SensorBaselineCalibrator

        cal = SensorBaselineCalibrator(window_seconds=0.05)  # 50ms window
        for _ in range(5):
            cal.feed(_FakeSnapshot(core_temperature=60.0, accelerometer_jerk=0.2))
        time.sleep(0.06)
        # Next feed triggers finalization
        cal.feed(_FakeSnapshot(core_temperature=60.0, accelerometer_jerk=0.2))
        assert cal.is_done

    def test_thresholds_mean_plus_k_sigma(self):
        from src.modules.sensor_baseline_calibrator import SensorBaselineCalibrator

        cal = SensorBaselineCalibrator(window_seconds=0.05, sigma_k=2.0)
        temps = [60.0, 62.0, 64.0, 61.0, 63.0]
        jerks = [0.1, 0.15, 0.12, 0.11, 0.13]
        for t, j in zip(temps, jerks):
            cal.feed(_FakeSnapshot(core_temperature=t, accelerometer_jerk=j))
        time.sleep(0.06)
        cal.feed(_FakeSnapshot())  # trigger finalize

        t = cal.compute_thresholds()
        assert t is not None
        assert math.isfinite(t.temperature_threshold)
        assert math.isfinite(t.jerk_threshold)
        # threshold must be above the mean
        assert t.temperature_threshold > t.temperature_mean
        assert t.jerk_threshold >= t.jerk_mean

    def test_nan_inf_samples_ignored(self):
        from src.modules.sensor_baseline_calibrator import SensorBaselineCalibrator

        cal = SensorBaselineCalibrator(window_seconds=0.05, sigma_k=1.0)
        cal.feed(_FakeSnapshot(core_temperature=float("nan"), accelerometer_jerk=float("inf")))
        cal.feed(_FakeSnapshot(core_temperature=70.0, accelerometer_jerk=0.2))
        cal.feed(_FakeSnapshot(core_temperature=70.0, accelerometer_jerk=0.2))
        cal.feed(_FakeSnapshot(core_temperature=70.0, accelerometer_jerk=0.2))
        time.sleep(0.06)
        cal.feed(_FakeSnapshot())
        t = cal.compute_thresholds()
        assert t is not None
        assert math.isfinite(t.temperature_threshold)
        assert math.isfinite(t.jerk_threshold)

    def test_fallback_when_too_few_temp_samples(self):
        """With < 3 temperature samples, must fall back gracefully without raising."""
        from src.modules.sensor_baseline_calibrator import SensorBaselineCalibrator

        cal = SensorBaselineCalibrator(window_seconds=0.05, sigma_k=2.0)
        # Feed only jerk data, no temperature
        cal.feed(_FakeSnapshot(accelerometer_jerk=0.3))
        time.sleep(0.06)
        cal.feed(_FakeSnapshot())
        t = cal.compute_thresholds()
        assert t is not None
        assert math.isfinite(t.temperature_threshold)

    def test_jerk_threshold_clamped_to_1(self):
        """jerk_threshold must never exceed 1.0 (normalized field)."""
        from src.modules.sensor_baseline_calibrator import SensorBaselineCalibrator

        cal = SensorBaselineCalibrator(window_seconds=0.05, sigma_k=10.0)  # huge k
        for _ in range(5):
            cal.feed(_FakeSnapshot(core_temperature=50.0, accelerometer_jerk=0.9))
        time.sleep(0.06)
        cal.feed(_FakeSnapshot())
        t = cal.compute_thresholds()
        assert t is not None
        assert t.jerk_threshold <= 1.0
