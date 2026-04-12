"""
Read-only advisory telemetry (async). Does not change MalAbs, buffer, Bayes, poles, or will.

Uses :meth:`src.modules.drive_arbiter.DriveArbiter.evaluate` only — same advisory path as chat JSON.
"""

from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.kernel import EthicalKernel
    from src.modules.drive_arbiter import DriveIntent


def advisory_interval_seconds_from_env() -> float:
    """
    If ``KERNEL_ADVISORY_INTERVAL_S`` is a positive float, WebSocket sessions run
    :func:`advisory_loop` in the background (Fase 1.3–1.4). Otherwise 0 (off).
    """
    raw = os.environ.get("KERNEL_ADVISORY_INTERVAL_S", "").strip()
    if not raw:
        return 0.0
    try:
        v = float(raw)
    except ValueError:
        return 0.0
    return v if v > 0 else 0.0


def advisory_snapshot(kernel: EthicalKernel) -> list[DriveIntent]:
    """One-shot advisory intents (deterministic given kernel state)."""
    return list(kernel.drive_arbiter.evaluate(kernel))


async def advisory_loop(
    kernel: EthicalKernel,
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
        except TimeoutError:
            continue
        break
