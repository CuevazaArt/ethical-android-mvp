import threading
import time

class CerebellumNode(threading.Thread):
    """
    Subconsciente Adyacente (Daemon Thread).
    Monitors hardware sensors at ultra-high frequency.
    Interrumpe al Lóbulo Ejecutivo si los motores o batería están en estado crítico.
    """
    def __init__(self, hardware_interrupt_event: threading.Event):
        super().__init__(daemon=True, name="CerebellumSomaticNode")
        self.interrupt_event = hardware_interrupt_event
        self.is_running = True
        self.mock_critical = False # For testing/red-teaming

    def run(self):
        """Pure hardware polling loop."""
        from src.modules.vitality import critical_battery_threshold, critical_temperature_threshold
        
        t_bat = critical_battery_threshold()
        t_temp = critical_temperature_threshold()
        
        while self.is_running:
            # En un entorno real, aquí leeríamos de i2c o sysfs
            # Simulamos lectura de sensores
            current_bat = 0.5   # 50%
            current_temp = 45.0 # celius
            
            # Chequeo de seguridad subconsciente
            is_critical = (current_bat < t_bat) or (current_temp >= t_temp) or self.mock_critical
            
            if is_critical:
                if not self.interrupt_event.is_set():
                    # Activamos el freno de emergencia
                    self.interrupt_event.set()
            else:
                if self.interrupt_event.is_set():
                    # Recuperación automática si los niveles vuelven a la normalidad
                    self.interrupt_event.clear()

            time.sleep(0.01) # Ultra low latency polling (100hz)

    def stop(self):
        self.is_running = False
