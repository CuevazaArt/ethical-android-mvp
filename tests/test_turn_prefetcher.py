"""Tests for MER Module 10.4 bridge prefetch (Team Copilot track)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.turn_prefetcher import TurnPrefetcher, ollama_generate_url
from src.kernel_lobes.models import EthicalSentence, SemanticState


@pytest.mark.asyncio
async def test_predict_bridge_heuristic_warm() -> None:
    pf = TurnPrefetcher(model_name=None)
    state = SemanticState(
        perception_confidence=0.85,
        raw_prompt="hello",
        scenario_summary="",
        suggested_context="everyday",
    )
    ethics = EthicalSentence(
        is_safe=True,
        social_tension_locus=0.2,
        morals={"harmonics": {"warmth": 0.95, "mystery": 0.1}},
    )
    out = await pf.predict_bridge(state, ethics)
    assert isinstance(out, str) and len(out) >= 2
    assert out in TurnPrefetcher.BRIDGES["warm"]


def test_ollama_generate_url_respects_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:11434/")
    assert ollama_generate_url() == "http://custom:11434/api/generate"
