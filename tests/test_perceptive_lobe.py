"""Tri-lobe PerceptiveLobe async httpx probe (optional env)."""

from __future__ import annotations

import asyncio

import pytest
from src.kernel_lobes.models import SemanticState
from src.kernel_lobes.perception_lobe import PerceptiveLobe


def test_observe_without_probe_no_http(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", raising=False)
    pl = PerceptiveLobe()
    try:
        state = asyncio.run(pl.observe("hello", None))
        assert isinstance(state, SemanticState)
        assert state.raw_prompt == "hello"
        assert state.timeout_trauma is None
        assert state.perception_confidence == 1.0
    finally:
        asyncio.run(pl.aclose())


def test_observe_with_probe_connection_error_sets_trauma(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", "http://127.0.0.1:1/")
    pl = PerceptiveLobe()
    try:
        state = asyncio.run(pl.observe("hello", None))
        assert state.timeout_trauma is not None
        assert state.timeout_trauma.source_lobe == "perceptive"
        assert state.perception_confidence < 1.0
    finally:
        asyncio.run(pl.aclose())


def test_classify_env_key_perceptive_lobe_probe() -> None:
    from src.validators.kernel_env_operator import classify_env_key

    assert classify_env_key("KERNEL_PERCEPTIVE_LOBE_PROBE_URL") == "Perception / sensors"
