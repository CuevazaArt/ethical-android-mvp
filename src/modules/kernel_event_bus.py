"""
In-process synchronous event bus for Phase 2 hardening (PRODUCTION_HARDENING_ROADMAP).

**Design:** single-threaded, deterministic ``publish`` order; subscriber exceptions are
logged and **do not** abort ``EthicalKernel.process``. Opt-in via ``KERNEL_EVENT_BUS=1``.

This is **not** a distributed bus; it decouples optional listeners (telemetry, bridges,
future ``ethos-extensions``) from the core decision path without async or threads.
"""

from __future__ import annotations

import logging
import os
from collections import defaultdict
from collections.abc import Callable
from typing import Any

_log = logging.getLogger(__name__)

EVENT_KERNEL_DECISION = "kernel.decision"
EVENT_KERNEL_EPISODE_REGISTERED = "kernel.episode_registered"
EVENT_KERNEL_WEIGHTS_UPDATED = (
    "kernel.weights_updated"  # I2 — emitted when hypothesis_weights change
)
EVENT_GOVERNANCE_THRESHOLD_UPDATED = "kernel.governance_threshold_updated"
EVENT_SENSORY_STRESS_ALERT = "kernel.sensory_stress_alert"

KernelEventHandler = Callable[[dict[str, Any]], None]

__all__ = [
    "EVENT_KERNEL_DECISION",
    "EVENT_KERNEL_EPISODE_REGISTERED",
    "EVENT_KERNEL_WEIGHTS_UPDATED",
    "EVENT_GOVERNANCE_THRESHOLD_UPDATED",
    "EVENT_SENSORY_STRESS_ALERT",
    "KernelEventBus",
    "KernelEventHandler",
    "kernel_event_bus_enabled",
]


def kernel_event_bus_enabled() -> bool:
    v = os.environ.get("KERNEL_EVENT_BUS", "").strip().lower()
    return v in ("1", "true", "yes", "on")


class KernelEventBus:
    """Minimal pub/sub registry; handlers run synchronously in subscription order."""

    def __init__(self) -> None:
        self._subs: defaultdict[str, list[KernelEventHandler]] = defaultdict(list)

    def subscribe(self, event: str, handler: KernelEventHandler) -> None:
        if not event or handler is None:
            return
        self._subs[event].append(handler)

    def publish(self, event: str, payload: dict[str, Any]) -> None:
        if not event:
            return
        data = dict(payload)
        for h in self._subs.get(event, []):
            try:
                h(data)
            except Exception:
                _log.exception("kernel event handler failed event=%r", event)

    def subscriber_count(self, event: str) -> int:
        return len(self._subs.get(event, ()))
