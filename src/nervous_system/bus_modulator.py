import asyncio
import logging
import time
from typing import Optional
from src.nervous_system.corpus_callosum import CorpusCallosum

_log = logging.getLogger(__name__)

class BusModulator:
    """
    Control unit for the Nervous System.
    Monitors congestion and scales the biological depth of the lobes.
    Implements throttling based on 'Somatic Telemetry' (CPU/Battery).
    """
    def __init__(self, bus: CorpusCallosum):
        self.bus = bus
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Throttling state
        self.load_factor = 0.0  # 0.0 (Chill) to 1.0 (Panic)
        self.mode = "server"  # server, office_2, nomad_edge

    def start(self, mode: str = "office_2"):
        """Start monitoring system health and modulation."""
        self.mode = mode
        if not self._running:
            self._running = True
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            _log.info(f"BusModulator: Modulation active in mode '{self.mode}'.")

    async def stop(self):
        """Stop modulation."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
    
    async def _monitor_loop(self):
        """Main loop for biological throttling."""
        while self._running:
            # Check queue depth in CorpusCallosum as a proxy for 'mental load'
            total_pending = sum(q.qsize() for q in self.bus._queues.values())
            
            # Simple linear scaling for load_factor
            # 10 pulses pending = 1.0 load
            self.load_factor = min(total_pending / 10.0, 1.0)
            
            if self.load_factor > 0.8:
                _log.warning(f"BusModulator: High mental load detected ({self.load_factor}). Triggering throttling.")
                # Here we would emit a 'GlobalDegradationPulse' or similar
            
            # TODO: Integrate with psutil or somatic_state to detect 'Oficina 2' hardware strain
            
            await asyncio.sleep(0.5)

    def get_bma_sample_scale(self) -> int:
        """
        Returns the recommended number of BMA samples based on load and hardware.
        Used by the Cerebelo Auxiliar.
        """
        base_samples = 1000
        if self.mode == "nomad_edge":
            base_samples = 100
        elif self.mode == "office_2":
            base_samples = 500
            
        # Modulate down based on internal load
        return int(base_samples * (1.0 - (self.load_factor * 0.5)))

    async def biological_yield(self):
        """
        Organically pauses execution based on the current load factor.
        Lobes call this during heavy processing to prevent CPU saturation.
        """
        base_sleep = 0.001
        throttle = 0.0
        if self.load_factor > 0.5:
            # Scale up to 100ms yield at full saturation
            throttle = ((self.load_factor - 0.5) * 2.0) * 0.1
            
        await asyncio.sleep(base_sleep + throttle)
