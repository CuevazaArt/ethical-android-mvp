import threading
import time
import random
import logging
from typing import Dict

_log = logging.getLogger(__name__)

class CerebellumNode(threading.Thread):
    """
    Subconsciente Adyacente (Daemon Thread).
    Monitors hardware sensors and simulates somatic interrupts.
    """
    def __init__(self, hardware_interrupt_event: threading.Event) -> None:
        super().__init__(daemon=True, name="CerebellumSomaticNode")
        self.interrupt_event = hardware_interrupt_event
        self.is_running = True
        
        # Simulated sensor state
        self.battery_level: float = 100.0
        self.cpu_temperature: float = 45.0
        self.emergency_stop: bool = False

    def run(self) -> None:
        """Pure hardware polling loop."""
        try:
            from src.modules.vitality import critical_battery_threshold, critical_temperature_threshold
            t_bat = critical_battery_threshold()
            t_temp = critical_temperature_threshold()
        except Exception as exc:
            _log.warning("CerebellumNode: could not load vitality thresholds (%s); using defaults.", exc)
            t_bat = 0.15  # 15% battery
            t_temp = 80.0  # 80°C
        
        while self.is_running:
            # 1. Simulate drift
            self.battery_level -= 0.001
            self.cpu_temperature += random.uniform(-0.1, 0.1)
            
            # 2. Check critical thresholds (Vertical logic)
            # battery_level is 0-100, t_bat is 0-1
            if self.battery_level < (t_bat * 100.0):
                # Critical Battery Trauma
                self.interrupt_event.set()
                
            if self.cpu_temperature > t_temp:
                # Thermal Trauma
                self.interrupt_event.set()
                
            if self.emergency_stop:
                self.interrupt_event.set()

            time.sleep(0.01) # 100Hz

    def stop(self) -> None:
        self.is_running = False

    def get_somatic_snapshot(self) -> Dict[str, float]:
        """Returns current hardware state for the Perceptive Lobe."""
        return {
            "battery": round(self.battery_level, 2),
            "temp": round(self.cpu_temperature, 2),
            "e_stop": float(self.emergency_stop)
        }
