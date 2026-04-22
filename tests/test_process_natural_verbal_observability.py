"""process_natural exposes verbal LLM degradation like chat (G-03)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.cognition.llm_layer import LLMModule


class _RaisingCompletion:
    def complete(self, system: str, user: str) -> str:
        raise RuntimeError("simulated transport failure")


def test_process_natural_sets_last_natural_verbal_degradation_events(monkeypatch):
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    k = EthicalKernel(variability=False, seed=1, llm=LLMModule(text_backend=_RaisingCompletion()))
    decision, response, _narr = k.process_natural(
        "An elderly person collapsed in the supermarket while I was shopping."
    )
    assert decision is not None
    assert response.message
    ev = k.last_natural_verbal_llm_degradation_events
    assert ev is not None
    assert any(e.get("touchpoint") == "communicate" for e in ev)
