"""
Sensor Baseline Calibrator — Bloque 12.2
=========================================
Aclimatación autónoma del entorno durante los primeros N segundos de boot.

En lugar de usar umbrales fijos (ej. 75 ºC o jerk 0.6), esta clase acumula
muestras reales del entorno durante una ventana de *warm-up* y calcula medias
y desviaciones estándar para definir el "Punto Dulce" relativo al contexto
actual.  Los umbrales resultantes se exponen como overrides que el kernel puede
usar para reemplazar los valores por defecto de las funciones
``critical_temperature_threshold`` y ``critical_jerk_threshold``.

Uso típico::

    calibrator = SensorBaselineCalibrator()
    calibrator.feed(snapshot)          # llamar en cada tick mientras running
    if calibrator.is_done:
        overrides = calibrator.compute_thresholds()
        # overrides: {"temperature_sigma_k": float, "jerk_sigma_k": float,
        #              "temperature_mean": float, "jerk_mean": float}

Env vars
--------
``KERNEL_CALIBRATION_WINDOW_S``  — duración de la ventana (default 60 s).
``KERNEL_CALIBRATION_SIGMA_K``   — multiplicador de sigma para el umbral crítico
                                   (default 2.0).  Umbral = mean + k·sigma.
"""

from __future__ import annotations

import logging
import math
import os
import time
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)


def _calibration_window_seconds() -> float:
    raw = os.environ.get("KERNEL_CALIBRATION_WINDOW_S", "").strip()
    if not raw:
        return 60.0
    try:
        v = float(raw)
        return v if math.isfinite(v) and v > 0 else 60.0
    except (TypeError, ValueError):
        return 60.0


def _calibration_sigma_k() -> float:
    raw = os.environ.get("KERNEL_CALIBRATION_SIGMA_K", "").strip()
    if not raw:
        return 2.0
    try:
        v = float(raw)
        return v if math.isfinite(v) and v > 0 else 2.0
    except (TypeError, ValueError):
        return 2.0


@dataclass
class BaselineThresholds:
    """Computed thresholds from the calibration window."""

    temperature_mean: float
    temperature_std: float
    temperature_threshold: float  # mean + k*std (critical above this)

    jerk_mean: float
    jerk_std: float
    jerk_threshold: float  # mean + k*std (critical above this)

    sample_count: int
    window_seconds: float
    sigma_k: float


class _Welford:
    """Online mean/variance using Welford's algorithm. NaN/Inf safe."""

    def __init__(self) -> None:
        self.n: int = 0
        self._mean: float = 0.0
        self._M2: float = 0.0

    def add(self, x: float) -> None:
        if not math.isfinite(x):
            return
        self.n += 1
        delta = x - self._mean
        self._mean += delta / self.n
        delta2 = x - self._mean
        self._M2 += delta * delta2

    @property
    def mean(self) -> float:
        return self._mean

    @property
    def variance(self) -> float:
        if self.n < 2:
            return 0.0
        return self._M2 / (self.n - 1)

    @property
    def std(self) -> float:
        return math.sqrt(self.variance)


class SensorBaselineCalibrator:
    """
    Accumulates SensorSnapshot samples during boot warm-up and derives
    environment-relative critical thresholds.
    """

    def __init__(
        self,
        window_seconds: float | None = None,
        sigma_k: float | None = None,
    ) -> None:
        self._window = (
            window_seconds if window_seconds is not None else _calibration_window_seconds()
        )
        self._k = sigma_k if sigma_k is not None else _calibration_sigma_k()
        self._start: float = time.perf_counter()
        self._temp_acc: _Welford = _Welford()
        self._jerk_acc: _Welford = _Welford()
        self._done: bool = False
        self._thresholds: BaselineThresholds | None = None
        _log.info(
            "SensorBaselineCalibrator: started (window=%.0fs, sigma_k=%.1f)",
            self._window,
            self._k,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_done(self) -> bool:
        """True once the warm-up window has elapsed."""
        return self._done

    @property
    def elapsed(self) -> float:
        """Seconds since calibration started."""
        return time.perf_counter() - self._start

    def feed(self, snapshot: Any) -> None:
        """
        Consume one SensorSnapshot sample.  Safe to call after the window
        has closed (samples are silently discarded).

        Args:
            snapshot: A ``SensorSnapshot`` instance; non-conforming objects are ignored.
        """
        if self._done:
            return

        elapsed = self.elapsed
        if elapsed >= self._window:
            self._finalize()
            return

        # Accept duck-typed snapshot (avoid hard import cycle)
        temp = getattr(snapshot, "core_temperature", None)
        jerk = getattr(snapshot, "accelerometer_jerk", None)

        if temp is not None:
            try:
                self._temp_acc.add(float(temp))
            except (TypeError, ValueError):
                pass

        if jerk is not None:
            try:
                self._jerk_acc.add(float(jerk))
            except (TypeError, ValueError):
                pass

    def compute_thresholds(self) -> BaselineThresholds | None:
        """
        Return the computed :class:`BaselineThresholds` once calibration is done,
        or ``None`` if the window has not yet closed.
        """
        if not self._done:
            # Force finalize if window has already elapsed
            if self.elapsed >= self._window:
                self._finalize()
            else:
                return None
        return self._thresholds

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _finalize(self) -> None:
        """Close the window and compute thresholds from accumulated stats."""
        t_mean = self._temp_acc.mean
        t_std = self._temp_acc.std
        j_mean = self._jerk_acc.mean
        j_std = self._jerk_acc.std

        # Fallback to conservative defaults when insufficient samples
        if self._temp_acc.n < 3:
            _log.warning(
                "SensorBaselineCalibrator: too few temperature samples (%d), "
                "falling back to env default.",
                self._temp_acc.n,
            )
            from .vitality import critical_temperature_threshold

            t_mean = critical_temperature_threshold() - 5.0  # assume near-threshold baseline
            t_std = 1.0

        if self._jerk_acc.n < 3:
            _log.warning(
                "SensorBaselineCalibrator: too few jerk samples (%d), falling back to env default.",
                self._jerk_acc.n,
            )
            from .vitality import critical_jerk_threshold

            j_mean = critical_jerk_threshold() * 0.5
            j_std = 0.05

        t_thresh = t_mean + self._k * t_std
        j_thresh = min(1.0, j_mean + self._k * j_std)  # jerk is [0,1]

        self._thresholds = BaselineThresholds(
            temperature_mean=t_mean,
            temperature_std=t_std,
            temperature_threshold=t_thresh,
            jerk_mean=j_mean,
            jerk_std=j_std,
            jerk_threshold=j_thresh,
            sample_count=max(self._temp_acc.n, self._jerk_acc.n),
            window_seconds=self._window,
            sigma_k=self._k,
        )
        self._done = True
        _log.info(
            "SensorBaselineCalibrator: calibration complete "
            "(samples=%d, temp=%.1f±%.1f→thresh=%.1f°C, "
            "jerk=%.3f±%.3f→thresh=%.3f) in %.1fs",
            self._thresholds.sample_count,
            t_mean,
            t_std,
            t_thresh,
            j_mean,
            j_std,
            j_thresh,
            self.elapsed,
        )
