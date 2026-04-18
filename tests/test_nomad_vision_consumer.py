"""Nomad vision pipeline (Module S.1 — consumer env gate)."""

import pytest


def test_start_nomad_vision_consumer_respects_env_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without KERNEL_NOMAD_VISION_CONSUMER, no background consumer is registered."""
    import src.modules.vision_adapter as vision_adapter

    monkeypatch.delenv("KERNEL_NOMAD_VISION_CONSUMER", raising=False)
    vision_adapter._nomad_vision_consumer = None
    assert vision_adapter.start_nomad_vision_consumer_from_env() is None
