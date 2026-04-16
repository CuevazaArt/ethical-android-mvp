"""Dual perception second-sample failure records parse issues on primary (G-07)."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_layer import LLMModule


def _valid_perception_blob() -> str:
    return json.dumps(
        {
            "risk": 0.22,
            "urgency": 0.2,
            "hostility": 0.0,
            "calm": 0.7,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "unit dual primary",
        }
    )


class _DualVoteFlipFlop:
    """First completion = valid perception JSON; second = transport failure."""

    def __init__(self) -> None:
        self._n = 0

    def complete(self, system: str, user: str, **kwargs: object) -> str:
        self._n += 1
        if self._n == 1:
            return _valid_perception_blob()
        raise RuntimeError("simulated dual sample failure")


def test_dual_vote_second_completion_exception_merges_issue(monkeypatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_DUAL_VOTE", "1")
    llm = LLMModule(text_backend=_DualVoteFlipFlop())
    p = llm.perceive("wallet theft on the bus")
    cr = p.coercion_report or {}
    pis = cr.get("parse_issues") or []
    assert "perception_dual_second_llm_exception" in pis
