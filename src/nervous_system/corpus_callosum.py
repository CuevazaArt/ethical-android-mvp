import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from src.kernel_lobes.models import NervousPulse

_log = logging.getLogger(__name__)

class CorpusCallosum:
    """
    The central Nervous System Bus. 
    Implements an asynchronous Pub/Sub pattern with priority channels.
    Allows 'all-to-all' communication without sequential blocking.
    """
    def __init__(self):
        # We use a dictionary of list of subscribers per Pulse Type class
        self._subscribers: Dict[str, List[Callable]] = {}
        # Multi-priority queues for the bus modulator to observe
        self._queues: Dict[int, asyncio.Queue] = {
            0: asyncio.Queue(),  # Reflex / Critical
            1: asyncio.Queue(),  # Normal
            2: asyncio.Queue(),  # Background
        }
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None

    def subscribe(self, pulse_type: type, callback: Callable):
        """Register a lobe or node as a listener for a specific pulse class."""
        type_name = pulse_type.__name__
        if type_name not in self._subscribers:
            self._subscribers[type_name] = []
        self._subscribers[type_name].append(callback)
        _log.debug(f"CorpusCallosum: Subscribed listener to {type_name}")

    async def publish(self, pulse: NervousPulse):
        """Inject an impulse into the nervous system multithreaded bus."""
        priority = getattr(pulse, 'priority', 1)
        if priority not in self._queues:
            priority = 1
        
        await self._queues[priority].put(pulse)
        # In a real organic system, this 'all-to-all' happens at light speed.
        # Here we rely on the central dispatcher loop.
        _log.debug(f"CorpusCallosum: Pulse {pulse.pulse_id} injected into channel {priority}")

    def start(self):
        """Awaken the nervous system loop."""
        if not self._running:
            self._running = True
            self._loop_task = asyncio.create_task(self._dispatch_loop())
            _log.info("CorpusCallosum: Nervous system loop AWAKENED.")

    async def stop(self):
        """Shutdown the nervous system."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        _log.info("CorpusCallosum: Nervous system sequence TERMINATED.")

    async def _dispatch_loop(self):
        """The core sub-pulse dispatcher."""
        while self._running:
            # Order of consumption: 0 (Critical) first
            for priority in sorted(self._queues.keys()):
                queue = self._queues[priority]
                if not queue.empty():
                    pulse = await queue.get()
                    await self._notify_subscribers(pulse)
                    queue.task_done()
                    # After a critical pulse, we restart the priority scan
                    if priority == 0:
                        break
            
            # Prevent CPU pegging in idle state
            await asyncio.sleep(0.001)

    async def _notify_subscribers(self, pulse: NervousPulse):
        """Notify all interested lobes about a pulse."""
        type_name = type(pulse).__name__
        # Also notify generic 'NervousPulse' subscribers
        target_types = [type_name, "NervousPulse"]
        
        for t_name in target_types:
            if t_name in self._subscribers:
                for callback in self._subscribers[t_name]:
                    try:
                        # We spawn each notification as a task to avoid serial blocking
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.create_task(callback(pulse))
                        else:
                            callback(pulse)
                    except Exception as e:
                        _log.error(f"CorpusCallosum: Error notifying subscriber of {t_name}: {e}")
