import threading
import time
import random

class CerebellumNode(threading.Thread):
    """
    Subconsciente Adyacente (Daemon Thread).
    Monitors hardware sensors and simulates somatic interrupts.
    """
    def __init__(self, hardware_interrupt_event: threading.Event):
        super().__init__(daemon=True, name="CerebellumSomaticNode")
        self.interrupt_event = hardware_interrupt_event
        self.is_running = True
        
        # Simulated sensor state
        self.battery_level = 100.0
        self.cpu_temperature = 45.0
        self.emergency_stop = False

    def run(self):
        """Pure hardware polling loop."""
        from src.modules.vitality import critical_battery_threshold, critical_temperature_threshold
        
        t_bat = critical_battery_threshold()
        t_temp = critical_temperature_threshold()
        
        while self.is_running:
            # 1. Simulate drift
            self.battery_level -= 0.001
            self.cpu_temperature += random.uniform(-0.1, 0.1)
            
            # 2. Check critical thresholds (Vertical logic)
            if self.battery_level < 5.0:
                # Critical Battery Trauma
                self.interrupt_event.set()
                
            if self.cpu_temperature > 95.0:
                # Thermal Trauma
                self.interrupt_event.set()
                
            if self.emergency_stop:
                self.interrupt_event.set()

            time.sleep(0.01) # 100Hz

    def stop(self):
        self.is_running = False

    def get_somatic_snapshot(self) -> dict:
        """Returns current hardware state for the Perceptive Lobe."""
        return {
            "battery": round(self.battery_level, 2),
            "temp": round(self.cpu_temperature, 2),
            "e_stop": self.emergency_stop
        }
