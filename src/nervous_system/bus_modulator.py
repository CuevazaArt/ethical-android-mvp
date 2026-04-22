import asyncio
import logging

from src.nervous_system.corpus_callosum import CorpusCallosum

_log = logging.getLogger(__name__)


class BusModulator:
    """
    Control unit for the Nervous System.
    Monitors congestion and scales the biological depth of the lobes.
    """

    def __init__(self, bus: CorpusCallosum):
        self.bus = bus
        self._running = False
        self._monitor_task: asyncio.Task | None = None

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
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self):
        """Main loop for biological throttling with awareness of queue caps."""
        from src.kernel_lobes.models import GlobalDegradationPulse

        cpu_ema = 0.0
        while self._running:
            # Check saturation percentage per channel
            saturation_scores = []
            for _priority, queue in self.bus._queues.items():
                if queue.maxsize > 0:
                    sat = queue.qsize() / queue.maxsize
                    saturation_scores.append(sat)

            queue_load = max(saturation_scores) if saturation_scores else 0.0

            cpu_load = 0.0
            try:
                import psutil  # type: ignore[import-untyped]

                cpu_load = float(psutil.cpu_percent(interval=None)) / 100.0
            except Exception:
                cpu_load = 0.0
            cpu_ema = (cpu_ema * 0.85) + (cpu_load * 0.15)

            # Blend queue saturation with CPU so multi-node / single host spikes both modulate.
            new_load = max(queue_load, cpu_ema * 0.95)

            # Exponential smoothing
            self.load_factor = (self.load_factor * 0.7) + (new_load * 0.3)

            if self.load_factor > 0.8:
                _log.warning(
                    f"BusModulator: CRITICAL SATURATION ({self.load_factor:.2f}). Triggering degradation."
                )
                pulse = GlobalDegradationPulse(degradation_factor=self.load_factor, priority=0)
                await self.bus.publish(pulse)

            # Polling rate of clinical state
            await asyncio.sleep(0.1)

    def get_bma_sample_scale(self) -> int:
        """Modulate Bayesian sampling based on load."""
        base_samples = 500
        if self.mode == "nomad_edge":
            base_samples = 100

        return int(base_samples * (1.0 - (self.load_factor * 0.5)))

    async def biological_yield(self):
        """Organically pauses execution based on load."""
        base_sleep = 0.001
        throttle = 0.0
        if self.load_factor > 0.5:
            throttle = ((self.load_factor - 0.5) * 2.0) * 0.1

        await asyncio.sleep(base_sleep + throttle)
