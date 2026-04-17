"""Ollama mode for LLMModule (Fase 3) — no live server required."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_layer import LLMModule


def test_ollama_perceive_uses_json_from_completion(monkeypatch):
    llm = LLMModule(mode="ollama")

    def fake_completion(system: str, user: str, **kwargs: object) -> str:
        return (
            '{"risk":0.2,"urgency":0.3,"hostility":0,"calm":0.8,"vulnerability":0.1,'
            '"legality":1,"manipulation":0,"familiarity":0.2,'
            '"suggested_context":"everyday_ethics","summary":"unit test"}'
        )

    monkeypatch.setattr(llm, "_llm_completion", fake_completion)
    p = llm.perceive("hello world")
    assert p.risk == 0.2
    assert p.suggested_context == "everyday_ethics"


def test_ollama_info_contains_model(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "mistral-nemo")
    llm = LLMModule(mode="ollama")
    assert "mistral-nemo" in llm.info()
    assert llm.is_available() is True
