"""
Read-only advisory telemetry (async). Does not change MalAbs, buffer, Bayes, poles, or will.

Uses :meth:`src.modules.drive_arbiter.DriveArbiter.evaluate` only — same advisory path as chat JSON.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.kernel import EthicalKernel
    from src.modules.drive_arbiter import DriveIntent


def advisory_snapshot(kernel: "EthicalKernel") -> List["DriveIntent"]:
    """One-shot advisory intents (deterministic given kernel state)."""
    return list(kernel.drive_arbiter.evaluate(kernel))


async def advisory_loop(
    kernel: "EthicalKernel",
    *,
    interval_s: float,
    stop: asyncio.Event,
) -> None:
    """
    Periodically re-evaluate advisory intents until ``stop`` is set.

    Safe to cancel via ``stop``; does not call the LLM or ``process``.
    """
    if interval_s <= 0:
        raise ValueError("interval_s must be positive")

    while not stop.is_set():
        kernel.drive_arbiter.evaluate(kernel)
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_s)
        except asyncio.TimeoutError:
            continue
        break
