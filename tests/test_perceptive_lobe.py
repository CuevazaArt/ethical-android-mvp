"""Tri-lobe PerceptiveLobe async httpx probe (optional env)."""

from __future__ import annotations

import asyncio

import pytest
from src.kernel_lobes.models import SemanticState
from src.kernel_lobes.perception_lobe import PerceptiveLobe

class MockComponent:
    pass

@pytest.mark.asyncio
async def test_observe_without_probe_no_http(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", raising=False)
    pl = PerceptiveLobe(
        safety_interlock=MockComponent(),
        strategist=MockComponent(),
        llm=MockComponent(),
        somatic_store=MockComponent(),
        buffer=MockComponent(),
        absolute_evil=MockComponent(),
        subjective_clock=MockComponent()
    )
    state = await pl.observe("hello", None)
    assert isinstance(state, SemanticState)
    assert state.raw_prompt == "hello"
    assert getattr(state, 'timeout_trauma', None) is None
    assert state.perception_confidence == 1.0


@pytest.mark.asyncio
async def test_observe_with_probe_connection_error_sets_trauma(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", "http://127.0.0.1:1/")
    
    class FakeBus:
        def __init__(self):
            self.published = []
        async def publish(self, pulse):
            self.published.append(pulse)
        def subscribe(self, *args, **kwargs):
            pass
            
    fake_bus = FakeBus()
    pl = PerceptiveLobe(
        safety_interlock=MockComponent(),
        strategist=MockComponent(),
        llm=MockComponent(),
        somatic_store=MockComponent(),
        buffer=MockComponent(),
        absolute_evil=MockComponent(),
        subjective_clock=MockComponent(),
        bus=fake_bus
    )
    
    # We test the survival fallback via the async dispatcher hook
    await pl._deliberate_observation_async("hello", "ref-123")
    
    assert len(fake_bus.published) > 0
    pulse = fake_bus.published[0]
    state = pulse.state_ref
    
    assert state.timeout_trauma is not None
    assert state.timeout_trauma.source_lobe == "perceptive"
    assert state.perception_confidence < 1.0


def test_classify_env_key_perceptive_lobe_probe() -> None:
    from src.validators.kernel_env_operator import classify_env_key

    assert classify_env_key("KERNEL_PERCEPTIVE_LOBE_PROBE_URL") == "Perception / sensors"
