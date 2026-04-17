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

    def run(self):
        """Pure hardware polling loop."""
        while self.is_running:
            # TODO: Poll battery and thermal sensors
            # If critical:
            # self.interrupt_event.set()
            time.sleep(0.01)  # Ultra low latency polling (simulate 100hz)

    def stop(self):
        self.is_running = False
