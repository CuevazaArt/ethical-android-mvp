from __future__ import annotations

import threading
import time
from collections.abc import Callable

from src.modules.vitality import critical_battery_threshold, critical_temperature_threshold

# How often the cerebellum polls sensors (seconds).  100 Hz by default; override
# via ``KERNEL_CEREBELLUM_POLL_HZ`` (positive float).
_DEFAULT_POLL_HZ = 100.0

SensorReadCallback = Callable[[], tuple[float | None, float | None]]
"""
Callable that returns ``(battery_level, core_temperature_celsius)`` on demand.

Either value may be ``None`` when the hardware channel is not available.
"""


def _poll_interval_seconds() -> float:
    import os

    try:
        hz = float(os.environ.get("KERNEL_CEREBELLUM_POLL_HZ", _DEFAULT_POLL_HZ))
        if hz <= 0:
            hz = _DEFAULT_POLL_HZ
    except (TypeError, ValueError):
        hz = _DEFAULT_POLL_HZ
    return 1.0 / hz


class CerebellumNode(threading.Thread):
    """
    Subconsciente Adyacente (Daemon Thread).

    Monitors hardware sensors at high frequency (default 100 Hz).  Fires
    ``hardware_interrupt_event`` when battery or core temperature cross the
    critical thresholds defined by ``KERNEL_VITALITY_CRITICAL_BATTERY`` and
    ``KERNEL_VITALITY_CRITICAL_TEMP``.

    Pass a :data:`SensorReadCallback` to supply real or simulated readings.
    When no callback is provided the node runs in a no-op monitoring mode.
    """

    def __init__(
        self,
        hardware_interrupt_event: threading.Event,
        sensor_read_callback: SensorReadCallback | None = None,
    ) -> None:
        super().__init__(daemon=True, name="CerebellumSomaticNode")
        self.interrupt_event = hardware_interrupt_event
        self._sensor_read = sensor_read_callback
        self.is_running = True

        # Last observed readings (for diagnostics / tests)
        self.last_battery: float | None = None
        self.last_temperature: float | None = None

    def run(self) -> None:
        """Pure hardware polling loop at ``KERNEL_CEREBELLUM_POLL_HZ``."""
        poll_interval = _poll_interval_seconds()
        batt_crit = critical_battery_threshold()
        temp_crit = critical_temperature_threshold()

        while self.is_running:
            if self._sensor_read is not None:
                try:
                    battery, temperature = self._sensor_read()
                    self.last_battery = battery
                    self.last_temperature = temperature

                    if battery is not None and battery < batt_crit:
                        self.interrupt_event.set()

                    if temperature is not None and temperature >= temp_crit:
                        self.interrupt_event.set()

                except Exception:
                    pass  # Hardware read failures degrade silently; loop continues

            time.sleep(poll_interval)

    def stop(self) -> None:
        self.is_running = False
