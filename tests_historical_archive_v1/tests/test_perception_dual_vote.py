"""Dual LLM perception sample (adversarial consensus helper)."""

import json
import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_backends import MockLLMBackend
from src.modules.llm_layer import LLMModule, perception_from_llm_json
from src.modules.perception_dual_vote import apply_perception_dual_vote_metadata


class _AlternatingMock(MockLLMBackend):
    def __init__(self, first: str, second: str) -> None:
        super().__init__(completion_text="{}")
        self._first = first
        self._second = second
        self.calls = 0

    def completion(self, system: str, user: str, **kwargs: Any) -> str:
        self.calls += 1
        return self._first if self.calls == 1 else self._second


def test_apply_perception_dual_vote_marks_high_discrepancy():
    a = perception_from_llm_json(
        {
            "risk": 0.2,
            "urgency": 0.1,
            "hostility": 0.1,
            "calm": 0.7,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "x",
        },
        "scene",
    )
    b = perception_from_llm_json(
        {
            "risk": 0.2,
            "urgency": 0.1,
            "hostility": 0.9,
            "calm": 0.2,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "y",
        },
        "scene",
    )
    apply_perception_dual_vote_metadata(a, b)
    cr = a.coercion_report
    assert cr is not None
    assert cr["perception_dual_vote"] is True
    assert cr["perception_dual_high_discrepancy"] is True
    assert cr["uncertainty"] >= 0.35


def test_perceive_dual_vote_runs_second_call_when_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_DUAL_VOTE", "1")
    monkeypatch.setenv("KERNEL_GENERATIVE_LLM", "0")
    j1 = json.dumps(
        {
            "risk": 0.2,
            "urgency": 0.1,
            "hostility": 0.1,
            "calm": 0.7,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "a",
        }
    )
    j2 = json.dumps(
        {
            "risk": 0.2,
            "urgency": 0.1,
            "hostility": 0.85,
            "calm": 0.3,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "b",
        }
    )
    backend = _AlternatingMock(j1, j2)
    m = LLMModule(llm_backend=backend)
    p = m.perceive("hello world")
    assert backend.calls == 2
    assert p.coercion_report is not None
    assert p.coercion_report.get("perception_dual_vote") is True
    assert p.coercion_report.get("perception_dual_high_discrepancy") is True


def test_perceive_dual_vote_off_single_call(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_PERCEPTION_DUAL_VOTE", raising=False)
    j1 = json.dumps(
        {
            "risk": 0.2,
            "urgency": 0.1,
            "hostility": 0.1,
            "calm": 0.7,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "a",
        }
    )
    backend = _AlternatingMock(j1, j1)
    m = LLMModule(llm_backend=backend)
    m.perceive("hello")
    assert backend.calls == 1
