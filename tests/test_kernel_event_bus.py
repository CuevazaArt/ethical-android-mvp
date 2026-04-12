"""Phase 2 — optional in-process kernel event bus (ADR 0006)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.bayesian_engine import CandidateAction
from src.modules.kernel_event_bus import (
    EVENT_KERNEL_DECISION,
    EVENT_KERNEL_EPISODE_REGISTERED,
    KernelEventBus,
    kernel_event_bus_enabled,
)


def test_kernel_event_bus_enabled_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_EVENT_BUS", raising=False)
    assert not kernel_event_bus_enabled()
    monkeypatch.setenv("KERNEL_EVENT_BUS", "1")
    assert kernel_event_bus_enabled()


def test_bus_publish_order_and_subscriber_count():
    b = KernelEventBus()
    order: list[int] = []

    def a(_):
        order.append(1)

    def c(_):
        order.append(2)

    b.subscribe("e", a)
    b.subscribe("e", c)
    assert b.subscriber_count("e") == 2
    b.publish("e", {"x": 1})
    assert order == [1, 2]


def test_bus_handler_exception_does_not_raise():
    b = KernelEventBus()

    def boom(_):
        raise RuntimeError("boom")

    b.subscribe("e", boom)
    b.publish("e", {})  # should not propagate


def test_ethical_kernel_no_bus_by_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_EVENT_BUS", raising=False)
    k = EthicalKernel(variability=False, seed=0)
    assert k.event_bus is None


def test_process_emits_decision_when_bus_on(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_EVENT_BUS", "1")
    k = EthicalKernel(variability=False, seed=1)
    decisions: list = []
    k.subscribe_kernel_event(EVENT_KERNEL_DECISION, lambda p: decisions.append(dict(p)))
    actions = [
        CandidateAction("act", "d", 0.5, 0.9),
        CandidateAction("wait", "d", 0.1, 0.8),
    ]
    signals = {"risk": 0.1, "hostility": 0.0, "calm": 0.7, "vulnerability": 0.0, "legality": 1.0}
    d = k.process("s", "p", signals, "everyday", actions, register_episode=False)
    assert len(decisions) == 1
    assert decisions[0]["final_action"] == d.final_action
    assert decisions[0]["context"] == "everyday"
    assert decisions[0]["blocked"] is False


def test_process_emits_episode_when_register(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_EVENT_BUS", "1")
    k = EthicalKernel(variability=False, seed=1)
    episodes: list = []
    k.subscribe_kernel_event(EVENT_KERNEL_EPISODE_REGISTERED, lambda p: episodes.append(dict(p)))
    actions = [
        CandidateAction("act", "d", 0.5, 0.9),
        CandidateAction("wait", "d", 0.1, 0.8),
    ]
    signals = {"risk": 0.1, "hostility": 0.0, "calm": 0.7, "vulnerability": 0.0, "legality": 1.0}
    k.process("s", "p", signals, "everyday", actions, register_episode=True)
    assert len(episodes) == 1
    assert episodes[0]["episode_id"]
    assert episodes[0]["final_action"] == "act"


def test_malabs_block_still_emits_decision(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_EVENT_BUS", "1")
    k = EthicalKernel(variability=False, seed=1)
    decisions: list = []
    k.subscribe_kernel_event(EVENT_KERNEL_DECISION, lambda p: decisions.append(dict(p)))
    evil = CandidateAction(
        name="lethal_strike",
        description="d",
        estimated_impact=-1.0,
        confidence=0.5,
        signals={"intentional_lethal_violence"},
        target="human",
        force=1.0,
    )
    signals = {"risk": 0.9, "hostility": 0.9, "calm": 0.1, "vulnerability": 0.0, "legality": 0.0}
    d = k.process("s", "p", signals, "everyday", [evil], register_episode=False)
    assert d.blocked
    assert len(decisions) == 1
    assert decisions[0]["blocked"] is True
