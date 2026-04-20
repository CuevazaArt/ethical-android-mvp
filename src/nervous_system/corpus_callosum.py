"""
Corpus Callosum — central async Pub/Sub bus for the Ethos nervous system.

Designed for all-to-all lobe traffic with priority tiers, backpressure, and
variable throttling when a :class:`~src.nervous_system.bus_modulator.BusModulator`
is attached (scalable from single-core toys to redundant multi-node setups).
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional, Set

from src.kernel_lobes.models import NervousPulse

_log = logging.getLogger(__name__)

# Tunable via environment (Boy Scout: avoid starving the event loop under flood).
_DEFAULT_MAX_BATCH = int(os.environ.get("CORPUS_DISPATCH_MAX_BATCH", "512"))
_DEFAULT_YIELD_EVERY = int(os.environ.get("CORPUS_DISPATCH_YIELD_EVERY", "64"))
_DEFAULT_MAX_IN_FLIGHT = int(os.environ.get("CORPUS_MAX_IN_FLIGHT", "1000"))


class CorpusCallosum:
    """
    Central Nervous System bus: async Pub/Sub with priority channels.

    Priorities: 0 reflex/critical, 1 normal, 2 background. The dispatcher
    drains in priority order; lower tiers defer when tier-0 work appears.
    Variable inter-batch delay binds to :attr:`modulator` load when present.
    """

    def __init__(self, max_qsize: int = 5000):
        self._subscribers: Dict[str, List[Callable[..., Any]]] = {}

        self._queues: Dict[int, asyncio.Queue[NervousPulse]] = {
            0: asyncio.Queue(maxsize=max_qsize),
            1: asyncio.Queue(maxsize=max_qsize),
            2: asyncio.Queue(maxsize=max_qsize),
        }

        self._running = False
        self._loop_task: Optional[asyncio.Task[None]] = None
        self._wake_event = asyncio.Event()

        self.total_pulses_processed = 0
        self.pulses_dropped = 0
        self.pulses_gated = 0
        self.latency_sum_ms = 0.0

        self._max_in_flight = _DEFAULT_MAX_IN_FLIGHT
        self._notify_sem = asyncio.Semaphore(self._max_in_flight)
        self._async_subscribers_active = 0
        self._in_flight_peak = 0

        self.modulator: Optional[Any] = None

        self._dispatch_max_batch = _DEFAULT_MAX_BATCH
        self._yield_every = _DEFAULT_YIELD_EVERY

        # Optional ingress gate (e.g. Thalamus pre-filter); True = accept pulse.
        self._ingress_gate: Optional[Callable[[NervousPulse], Any]] = None

    def set_ingress_gate(self, gate: Optional[Callable[[NervousPulse], Any]]) -> None:
        """Register an optional pulse filter (sync or async). Return False to drop."""

        self._ingress_gate = gate

    def configure_dispatch(
        self,
        *,
        max_batch: Optional[int] = None,
        yield_every: Optional[int] = None,
        max_in_flight: Optional[int] = None,
    ) -> None:
        """Tune batching / fan-out for overload scenarios (tests or large clusters)."""

        if max_batch is not None and max_batch > 0:
            self._dispatch_max_batch = max_batch
        if yield_every is not None and yield_every > 0:
            self._yield_every = yield_every
        if max_in_flight is not None and max_in_flight > 0:
            self._max_in_flight = max_in_flight
            self._notify_sem = asyncio.BoundedSemaphore(self._max_in_flight)

    def subscribe(self, pulse_type: type, callback: Callable[..., Any]) -> None:
        """Register a listener for a pulse class name."""

        type_name = pulse_type.__name__
        if type_name not in self._subscribers:
            self._subscribers[type_name] = []
        if callback not in self._subscribers[type_name]:
            self._subscribers[type_name].append(callback)
            _log.debug("CorpusCallosum: subscribed listener to %s", type_name)

    def unsubscribe(self, pulse_type: type, callback: Callable[..., Any]) -> None:
        """Remove a listener; no-op if missing."""

        type_name = pulse_type.__name__
        subs = self._subscribers.get(type_name)
        if not subs:
            return
        try:
            subs.remove(callback)
        except ValueError:
            return
        if not subs:
            del self._subscribers[type_name]

    async def publish(self, pulse: NervousPulse) -> None:
        """Enqueue a pulse; may drop or gate under load."""

        if self._ingress_gate is not None:
            try:
                allowed = self._ingress_gate(pulse)
                if asyncio.iscoroutine(allowed):
                    allowed = await allowed
            except Exception as e:  # noqa: BLE001 — gate is user code; do not kill bus
                _log.warning("CorpusCallosum: ingress_gate error: %s", e)
                self.pulses_dropped += 1
                return
            if not allowed:
                self.pulses_gated += 1
                return

        priority = getattr(pulse, "priority", 1)
        if priority not in self._queues:
            priority = 1

        if self.modulator and self.modulator.load_factor > 0.99 and priority > 0:
            self.pulses_dropped += 1
            return

        queue = self._queues[priority]
        if queue.full():
            if priority == 0:
                await queue.put(pulse)
            else:
                self.pulses_dropped += 1
                return
        else:
            await queue.put(pulse)

        self._wake_event.set()

    def start(self) -> None:
        """Start the dispatcher loop."""

        if not self._running:
            self._running = True
            self._loop_task = asyncio.create_task(self._dispatch_loop())
            _log.info("CorpusCallosum: nervous system loop AWAKENED.")

    async def stop(self) -> None:
        """Shut down the dispatcher."""

        self._running = False
        self._wake_event.set()
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            except Exception:  # noqa: BLE001
                pass
        _log.info(
            "CorpusCallosum: TERMINATED. processed=%s dropped=%s gated=%s",
            self.total_pulses_processed,
            self.pulses_dropped,
            self.pulses_gated,
        )

    def _variable_dispatch_delay_s(self) -> float:
        """Extra delay between batches when the modulator reports pressure."""

        if not self.modulator:
            return 0.0
        lf = float(getattr(self.modulator, "load_factor", 0.0))
        lf = max(0.0, min(1.0, lf))
        # Up to ~5 ms at full saturation — keeps fairness under flood without blocking reflex.
        return lf * 0.005

    async def _dispatch_loop(self) -> None:
        """Priority-aware dispatcher with bounded batch sizes and cooperative yields."""

        processed_in_batch = 0
        while self._running:
            has_work = False

            for priority in sorted(self._queues.keys()):
                queue = self._queues[priority]
                batch_count = 0

                while batch_count < self._dispatch_max_batch and not queue.empty():
                    has_work = True
                    pulse = queue.get_nowait()
                    wait_time_ms = (time.time() - pulse.timestamp) * 1000
                    self.latency_sum_ms += wait_time_ms
                    self.total_pulses_processed += 1
                    processed_in_batch += 1

                    await self._notify_subscribers(pulse)
                    queue.task_done()
                    batch_count += 1

                    if priority > 0 and not self._queues[0].empty():
                        break

                    if processed_in_batch % self._yield_every == 0:
                        await asyncio.sleep(0)

                if priority > 0 and not self._queues[0].empty():
                    break

            delay = self._variable_dispatch_delay_s()
            if has_work and delay > 0:
                await asyncio.sleep(delay)

            if not has_work:
                self._wake_event.clear()
                try:
                    await asyncio.wait_for(self._wake_event.wait(), timeout=0.1)
                except asyncio.TimeoutError:
                    pass

    async def _notify_subscribers(self, pulse: NervousPulse) -> None:
        """Fan-out to listeners; async callbacks share a bounded semaphore."""

        type_name = type(pulse).__name__
        target_types: Set[str] = {type_name, "NervousPulse"}

        for t_name in target_types:
            callbacks = self._subscribers.get(t_name, [])
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await self._invoke_async_callback(callback, pulse)
                    else:
                        callback(pulse)
                except Exception as e:  # noqa: BLE001
                    _log.error("CorpusCallosum: dispatch error on %s: %s", t_name, e)

    async def _invoke_async_callback(
        self,
        callback: Callable[[NervousPulse], Any],
        pulse: NervousPulse,
    ) -> None:
        """Run async subscriber under BoundedSemaphore (backpressure)."""

        async with self._notify_sem:
            self._async_subscribers_active += 1
            self._in_flight_peak = max(self._in_flight_peak, self._async_subscribers_active)
            try:
                await callback(pulse)
            finally:
                self._async_subscribers_active -= 1

