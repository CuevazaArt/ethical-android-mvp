"""Block 26.0 — MemoryLobe / bus / MotivationEngine wiring (Tri-Lobe integration)."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.kernel_event_bus import (
    EVENT_KERNEL_AMNESIA_FORGET_EPISODE,
    EVENT_KERNEL_EPISODE_REGISTERED,
    EVENT_KERNEL_PROACTIVE_PULSE,
)


def test_event_bus_subscribes_memory_amnesia_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_EVENT_BUS", "1")
    k = EthicalKernel(variability=False, seed=1)
    assert k.event_bus is not None
    assert k.event_bus.subscriber_count(EVENT_KERNEL_AMNESIA_FORGET_EPISODE) >= 1


def test_emit_episode_registered_reaches_subscribers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_EVENT_BUS", "1")
    k = EthicalKernel(variability=False, seed=2)
    seen: list[dict] = []

    def _h(payload: dict) -> None:
        seen.append(dict(payload))

    k.subscribe_kernel_event(EVENT_KERNEL_EPISODE_REGISTERED, _h)
    k._emit_kernel_episode_registered(
        episode_id="ep-test-1",
        scenario="scenario",
        place="chat",
        context="everyday",
        final_action="converse",
        decision_mode="D_fast",
    )
    assert len(seen) == 1
    assert seen[0].get("episode_id") == "ep-test-1"
    assert seen[0].get("final_action") == "converse"


def test_seek_internal_purpose_returns_candidate_actions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_EVENT_BUS", "0")
    k = EthicalKernel(variability=False, seed=3)
    for _ in range(24):
        k.motivation.update_drives({"social_tension": 0.0, "uncertainty": 0.5, "energy": 1.0})
    out = k.seek_internal_purpose()
    assert isinstance(out, list)
    assert all(hasattr(a, "name") and hasattr(a, "description") for a in out)


def test_emit_proactive_pulse_when_idle(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.modules.motivation_engine import DriveType

    monkeypatch.setenv("KERNEL_EVENT_BUS", "1")
    monkeypatch.setenv("KERNEL_PROACTIVE_PULSE_IDLE_S", "0.001")
    k = EthicalKernel(variability=False, seed=4)
    pulses: list[dict] = []
    k.subscribe_kernel_event(EVENT_KERNEL_PROACTIVE_PULSE, lambda p: pulses.append(dict(p)))
    import time as _t

    k.motivation.drives[DriveType.CURIOSITY].value = 0.95
    k._last_external_chat_mono = _t.monotonic() - 10.0
    k._last_proactive_pulse_mono = 0.0
    assert k.emit_proactive_pulse_if_idle() is True
    assert pulses and "motive" in pulses[0]
