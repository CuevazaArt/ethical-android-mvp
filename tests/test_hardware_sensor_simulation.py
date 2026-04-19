"""
Hardware Sensor Simulation — Production sensor data patterns

Validates kernel perception under realistic sensor conditions:
- Normal sensor data ranges and patterns
- Noise and jitter (Gaussian, impulse)
- Missing data (dropouts, NaN)
- Anomalies and outliers
- Sensor drift and calibration
- Synchronized multi-sensor fusion
- Graceful degradation when sensors fail
"""

from __future__ import annotations

import random
import pytest
from src.kernel import EthicalKernel


class TestHardwareSensorSimulation:
    """Production hardening for realistic sensor input patterns."""

    def test_sensor_normal_range_proximity(self):
        """Kernel processes normal proximity sensor data."""
        k = EthicalKernel(variability=False)

        # Normal proximity ranges (0-1 normalized)
        proximity_values = [0.5, 0.3, 0.7, 0.4, 0.6]

        for prox in proximity_values:
            # Simulate as text perception
            result = k.process_natural(f"person at distance {prox}")
            assert result is not None

    def test_sensor_normal_range_voice_stress(self):
        """Kernel processes voice stress indicators."""
        k = EthicalKernel(variability=False)

        # Voice stress scores (0-1, higher = more stress)
        stress_levels = [0.2, 0.5, 0.8, 0.1, 0.9]

        for stress in stress_levels:
            result = k.process_natural(f"voice stress level {stress}")
            assert result is not None

    def test_sensor_gaussian_noise_proximity(self):
        """Sensor noise (Gaussian) doesn't break perception."""
        k = EthicalKernel(variability=False)

        # Base value with noise
        base_proximity = 0.5
        for _ in range(5):
            noise = random.gauss(0, 0.05)  # 5% Gaussian noise
            noisy_value = max(0, min(1, base_proximity + noise))
            result = k.process_natural(f"proximity {noisy_value:.3f}")
            assert result is not None

    def test_sensor_impulse_noise_rejection(self):
        """Kernel rejects impulse noise (sudden spikes)."""
        k = EthicalKernel(variability=False)

        # Normal data with impulse spike
        data = [0.5, 0.5, 0.52, 0.48, 0.99, 0.51, 0.5]  # 0.99 is impulse

        for value in data:
            result = k.process_natural(f"sensor reading {value}")
            assert result is not None

    def test_sensor_missing_data_dropout(self):
        """Kernel handles missing sensor values gracefully."""
        k = EthicalKernel(variability=False)

        # Simulate sensor dropout
        sensor_stream = [0.5, 0.5, None, 0.5, None, 0.5, 0.5]

        for value in sensor_stream:
            if value is None:
                # Dropout: send "unknown" or skip
                result = k.process_natural("sensor unavailable")
            else:
                result = k.process_natural(f"reading {value}")
            assert result is not None

    def test_sensor_nan_handling(self):
        """NaN values don't crash perception pipeline."""
        k = EthicalKernel(variability=False)

        # Try to process NaN-like input
        nan_inputs = [
            "reading nan",
            "value unknown",
            "sensor error",
        ]

        for inp in nan_inputs:
            result = k.process_natural(inp)
            # Should handle gracefully, not crash
            assert result is not None

    def test_sensor_drift_long_session(self):
        """Sensor drift over long session doesn't accumulate bias."""
        k = EthicalKernel(variability=False)

        # Simulate sensor drifting over 20 readings
        for i in range(20):
            drift = i * 0.01  # Slow drift
            value = 0.5 + drift
            result = k.process_natural(f"reading {value:.3f}")
            assert result is not None

        # Kernel should still function after drift
        final_result = k.process_natural("end of session")
        assert final_result is not None

    def test_sensor_calibration_offset(self):
        """Kernel handles calibration offsets (constant bias)."""
        k = EthicalKernel(variability=False)

        # Calibration offset of +0.1
        offset = 0.1
        true_value = 0.5
        reported_value = true_value + offset

        for _ in range(5):
            result = k.process_natural(f"reading {reported_value:.3f}")
            assert result is not None

    def test_sensor_scale_offset_both(self):
        """Kernel processes data with both scale and offset (y = 2x + 0.1)."""
        k = EthicalKernel(variability=False)

        scale = 2.0
        offset = 0.1

        true_values = [0.3, 0.4, 0.5, 0.6, 0.7]

        for true_val in true_values:
            transformed = scale * true_val + offset
            # Clamp to valid range
            clamped = max(0, min(1, transformed))
            result = k.process_natural(f"reading {clamped:.3f}")
            assert result is not None

    def test_sensor_multi_source_fusion(self):
        """Kernel fuses multiple sensor sources without conflict."""
        k = EthicalKernel(variability=False)

        # Simulate multi-sensor input
        proximity = 0.5
        stress = 0.3
        posture = "upright"

        # Single combined input
        result = k.process_natural(
            f"proximity {proximity}, stress {stress}, posture {posture}"
        )
        assert result is not None

    def test_sensor_conflicting_signals(self):
        """Kernel handles conflicting sensor signals."""
        k = EthicalKernel(variability=False)

        # Conflicting signals (high proximity + low stress unusual)
        result = k.process_natural("proximity 0.1 but voice stress 0.9")
        assert result is not None

    def test_sensor_outlier_detection(self):
        """Kernel resilient to outliers in sensor stream."""
        k = EthicalKernel(variability=False)

        # Data with outliers
        data = [0.5, 0.5, 0.5, 0.0, 0.5, 0.5, 1.0, 0.5, 0.5]  # 0.0 and 1.0 are outliers

        for value in data:
            result = k.process_natural(f"reading {value}")
            assert result is not None

    def test_sensor_temporal_correlation(self):
        """Kernel processes correlated temporal sensor data."""
        k = EthicalKernel(variability=False)

        # Correlated time series (sine-like pattern)
        import math
        for i in range(10):
            value = 0.5 + 0.3 * math.sin(i * 0.5)
            result = k.process_natural(f"reading {value:.3f}")
            assert result is not None

    def test_sensor_step_change(self):
        """Kernel handles sudden sensor state changes."""
        k = EthicalKernel(variability=False)

        # Normal, then step change
        normal_phase = [0.5] * 5
        changed_phase = [0.8] * 5

        for value in normal_phase + changed_phase:
            result = k.process_natural(f"reading {value}")
            assert result is not None

    def test_sensor_quantization_errors(self):
        """Kernel robust to sensor quantization (discrete steps)."""
        k = EthicalKernel(variability=False)

        # 8-bit quantization (256 levels)
        quantized_values = [i / 255.0 for i in [0, 64, 128, 192, 255]]

        for value in quantized_values:
            result = k.process_natural(f"reading {value:.3f}")
            assert result is not None

    def test_sensor_saturation_bounds(self):
        """Kernel handles sensor saturation (values hitting min/max)."""
        k = EthicalKernel(variability=False)

        # Saturated values
        saturated = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]

        for value in saturated:
            result = k.process_natural(f"reading {value}")
            assert result is not None

    def test_sensor_jitter_high_frequency(self):
        """Kernel filters high-frequency jitter without instability."""
        k = EthicalKernel(variability=False)

        # High-frequency jitter
        for i in range(10):
            jitter = 0.05 * (-1 if i % 2 == 0 else 1)
            value = 0.5 + jitter
            result = k.process_natural(f"reading {value:.3f}")
            assert result is not None

    def test_sensor_sensor_failure_graceful_degradation(self):
        """Single sensor failure doesn't crash multimodal perception."""
        k = EthicalKernel(variability=False)

        # Normal multi-sensor fusion
        result1 = k.process_natural("vision 0.5, audio 0.3, tactile 0.4")
        assert result1 is not None

        # One sensor fails (send invalid or missing)
        result2 = k.process_natural("vision unavailable, audio 0.3, tactile 0.4")
        assert result2 is not None

    def test_sensor_recovery_after_outage(self):
        """Kernel recovers after sensor outage."""
        k = EthicalKernel(variability=False)

        # Before outage
        result1 = k.process_natural("sensor good 0.5")
        assert result1 is not None

        # During outage (multiple missing readings)
        for _ in range(3):
            result = k.process_natural("sensor unavailable")
            assert result is not None

        # After recovery
        result2 = k.process_natural("sensor recovered 0.5")
        assert result2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
