# Status: SCAFFOLD
import logging
import math
import statistics
import time
from dataclasses import dataclass

from src.modules.perception.sensor_contracts import SensorSnapshot

_log = logging.getLogger(__name__)


@dataclass
class CalibrationBaseline:
    mean: float = 0.0
    stddev: float = 0.0
    samples: int = 0
    unit: str = ""


class SensorBaselineCalibrator:
    """
    Bloque 12.2: Autocalibración Física (Aclimatación).
    Collects sensor data for a defined period to establish environmental
    baselines instead of using static global thresholds.
    """

    def __init__(self, duration_s: float = 60.0):
        self.duration_s = duration_s
        self.start_time: float | None = None
        self.is_active = False
        self.is_complete = False

        self._buffers: dict[str, list[float]] = {
            "core_temperature": [],
            "accelerometer_jerk": [],
            "ambient_noise": [],
            "vessel_latency": [],
            "motor_effort_avg": [],
            "stability_score": [],
        }

        self.baselines: dict[str, CalibrationBaseline] = {}

    def start(self):
        """Starts the acclimatization cycle."""
        self.start_time = time.perf_counter()
        self.is_active = True
        self.is_complete = False
        # Clear buffers
        for k in self._buffers:
            self._buffers[k] = []
        _log.info(
            "SensorBaselineCalibrator: Starting %.1fs acclimatization cycle.", self.duration_s
        )

    def update(self, snapshot: SensorSnapshot):
        """Feed latest sensor data into the calibration buffers."""
        if not self.is_active or self.is_complete:
            return

        now = time.perf_counter()
        if now - self.start_time > self.duration_s:
            self._finalize()
            return

        # Proactive accumulation from snapshot
        if snapshot.core_temperature is not None:
            self._buffers["core_temperature"].append(snapshot.core_temperature)
        if snapshot.accelerometer_jerk is not None:
            self._buffers["accelerometer_jerk"].append(snapshot.accelerometer_jerk)
        if snapshot.ambient_noise is not None:
            self._buffers["ambient_noise"].append(snapshot.ambient_noise)
        if snapshot.vessel_latency is not None:
            self._buffers["vessel_latency"].append(snapshot.vessel_latency)
        if snapshot.motor_effort_avg is not None:
            self._buffers["motor_effort_avg"].append(snapshot.motor_effort_avg)
        if snapshot.stability_score is not None:
            self._buffers["stability_score"].append(snapshot.stability_score)

    def _finalize(self):
        """Calculate means and standard deviations after sample window closes."""
        t0 = time.perf_counter()
        self.is_active = False
        self.is_complete = True

        results = {}
        for key, buffer in self._buffers.items():
            if not buffer:
                continue

            # Swarm Rule 2: Anti-NaN / Finite Hardening
            clean_buffer = [x for x in buffer if math.isfinite(x)]
            if not clean_buffer:
                continue

            mean = statistics.mean(clean_buffer)
            # Standard deviation requires at least 2 samples
            stddev = statistics.stdev(clean_buffer) if len(clean_buffer) > 1 else 0.0

            self.baselines[key] = CalibrationBaseline(
                mean=float(mean),
                stddev=float(stddev),
                samples=len(clean_buffer),
                unit="C"
                if key == "core_temperature"
                else "ms"
                if key == "vessel_latency"
                else "ratio",
            )
            results[key] = f"μ={mean:.2f}"

        latency = (time.perf_counter() - t0) * 1000
        _log.info(
            "SensorBaselineCalibrator: Calibration complete in %.2fms. Results: %s",
            latency,
            results,
        )

    def get_threshold(self, key: str, sigma: float = 3.0, default: float = 0.0) -> float:
        """
        Calculates a dynamic threshold: mean + (sigma * stddev).
        Helps define the 'Sweet Spot' (Punto Dulce) dynamically.
        """
        b = self.baselines.get(key)
        if not b:
            return default
        # Ensure result is finite
        val = b.mean + (sigma * b.stddev)
        return val if math.isfinite(val) else default


_CALIBRATOR = SensorBaselineCalibrator()


def get_sensor_calibrator() -> SensorBaselineCalibrator:
    return _CALIBRATOR
