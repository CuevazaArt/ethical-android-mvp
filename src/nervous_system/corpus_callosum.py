import asyncio
import logging
import time
from typing import Dict, List, Callable, Any, Optional, Set
from src.kernel_lobes.models import NervousPulse

_log = logging.getLogger(__name__)

class CorpusCallosum:
    """
    The central Nervous System Bus. 
    Implements an asynchronous Pub/Sub pattern with priority channels.
    Allows 'all-to-all' communication without sequential blocking.
    """
    def __init__(self, max_qsize: int = 5000):
        # Subscriber registry
        self._subscribers: Dict[str, List[Callable]] = {}
        
        # Multi-priority queues
        # 0: Reflex / Critical, 1: Normal, 2: Background
        self._queues: Dict[int, asyncio.Queue] = {
            0: asyncio.Queue(maxsize=max_qsize),
            1: asyncio.Queue(maxsize=max_qsize),
            2: asyncio.Queue(maxsize=max_qsize),
        }
        
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None
        self._wake_event = asyncio.Event()

        # Performance and Health Metrics
        self.total_pulses_processed = 0
        self.pulses_dropped = 0
        self.latency_sum_ms = 0.0
        self._in_flight_notifications = 0
        self._max_in_flight = 1000  # Cap for concurrent tasks

        # Modulator link (Throttling Variable)
        self.modulator: Optional[Any] = None

    def subscribe(self, pulse_type: type, callback: Callable):
        """Register a lobe or node as a listener for a specific pulse class."""
        type_name = pulse_type.__name__
        if type_name not in self._subscribers:
            self._subscribers[type_name] = []
        if callback not in self._subscribers[type_name]:
            self._subscribers[type_name].append(callback)
            _log.debug(f"CorpusCallosum: Subscribed listener to {type_name}")

    async def publish(self, pulse: NervousPulse):
        """Inject an impulse into the nervous system bus."""
        priority = getattr(pulse, 'priority', 1)
        if priority not in self._queues:
            priority = 1
        
        # Throttling Logic: Drop non-critical pulses if modulator reports excessive load
        if self.modulator and self.modulator.load_factor >= 0.99 and priority > 0:
            self.pulses_dropped += 1
            return

        queue = self._queues[priority]
        if queue.full():
            if priority == 0:
                # Critical pulses should block slightly rather than being dropped
                await queue.put(pulse)
            else:
                self.pulses_dropped += 1
                return
        else:
            await queue.put(pulse)
        
        # Wake the dispatcher loop
        self._wake_event.set()

    def start(self):
        """Awaken the dispatcher loop."""
        if not self._running:
            self._running = True
            self._loop_task = asyncio.create_task(self._dispatch_loop())
            _log.info("CorpusCallosum: Nervous system loop AWAKENED.")

    async def stop(self):
        """Shutdown the nervous system."""
        self._running = False
        self._wake_event.set()
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except (asyncio.CancelledError, Exception):
                pass
        _log.info(f"CorpusCallosum: Nervous system TERMINATED. Processed: {self.total_pulses_processed}, Dropped: {self.pulses_dropped}")

    async def _dispatch_loop(self):
        """High-speed pulse dispatcher."""
        while self._running:
            has_work = False
            
            # Priority-aware scan
            for priority in sorted(self._queues.keys()):
                queue = self._queues[priority]
                
                # Drain queue in batch
                while not queue.empty():
                    has_work = True
                    pulse = queue.get_nowait()
                    
                    # Latency Telemetry
                    wait_time_ms = (time.time() - pulse.timestamp) * 1000
                    self.latency_sum_ms += wait_time_ms
                    self.total_pulses_processed += 1
                        
                    await self._notify_subscribers(pulse)
                    queue.task_done()
                    
                    # Interrupt lower priority processing if priority 0 (Reflex) arrives
                    if priority > 0 and not self._queues[0].empty():
                        break
                
                if priority > 0 and not self._queues[0].empty():
                    break # Restart priority scan
            
            if not has_work:
                self._wake_event.clear()
                try:
                    await asyncio.wait_for(self._wake_event.wait(), timeout=0.1)
                except asyncio.TimeoutError:
                    pass

    async def _notify_subscribers(self, pulse: NervousPulse):
        """Fan-out to all registered callbacks."""
        type_name = type(pulse).__name__
        target_types = {type_name, "NervousPulse"}
        
        for t_name in target_types:
            callbacks = self._subscribers.get(t_name, [])
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        # Cap concurrent tasks
                        if self._in_flight_notifications > self._max_in_flight:
                            await callback(pulse)
                        else:
                            self._in_flight_notifications += 1
                            task = asyncio.create_task(callback(pulse))
                            task.add_done_callback(self._dec_in_flight)
                    else:
                        callback(pulse)
                except Exception as e:
                    _log.error(f"CorpusCallosum: Pulse Dispatch Error on {t_name}: {e}")

    def _dec_in_flight(self, _task):
        """Monitor concurrent task count."""
        self._in_flight_notifications = max(0, self._in_flight_notifications - 1)
