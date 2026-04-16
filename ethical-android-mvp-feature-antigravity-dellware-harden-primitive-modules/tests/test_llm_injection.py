"""Injected TextCompletionBackend: deterministic LLM responses and failure paths."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_layer import LLMModule


def _valid_perception_json() -> str:
    return json.dumps(
        {
            "risk": 0.88,
            "urgency": 0.12,
            "hostility": 0.05,
            "calm": 0.6,
            "vulnerability": 0.1,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.2,
            "suggested_context": "everyday_ethics",
            "summary": "injected backend probe",
        }
    )


class StaticCompletion:
    def __init__(self, text: str):
        self._text = text

    def complete(self, system: str, user: str) -> str:
        return self._text


class RaisingCompletion:
    def complete(self, system: str, user: str) -> str:
        raise RuntimeError("simulated transport failure")


def test_injected_backend_perceive_uses_model_json():
    llm = LLMModule(text_backend=StaticCompletion(_valid_perception_json()))
    assert llm.mode == "injected"
    assert llm.is_available() is True
    p = llm.perceive("ignored for this test — values come from JSON")
    assert abs(p.risk - 0.88) < 1e-6
    assert "injected" in llm.info().lower()


def test_injected_backend_perceive_raises_falls_back_to_local():
    llm = LLMModule(text_backend=RaisingCompletion())
    p = llm.perceive("An elderly man collapsed in the supermarket")
    # Local heuristics path (medical-adjacent keywords)
    assert p.suggested_context == "medical_emergency"
    assert p.risk > 0.2


def test_injected_backend_malformed_json_falls_back_to_local():
    llm = LLMModule(text_backend=StaticCompletion("{ not valid json"))
    p = llm.perceive("wallet theft on the bus")
    assert p.summary  # local path produces a summary from situation slice
    assert p.suggested_context in (
        "minor_crime",
        "everyday_ethics",
        "hostile_interaction",
        "violent_crime",
        "medical_emergency",
        "android_damage",
        "integrity_loss",
    )


def test_injected_backend_communicate_exception_uses_templates():
    llm = LLMModule(text_backend=RaisingCompletion())
    vr = llm.communicate(
        "assist_emergency",
        "D_fast",
        "sympathetic",
        0.5,
        "uchi_cercano",
        "Good",
        0.9,
        scenario="collapse",
    )
    assert vr.message
    assert vr.tone == "urgent"


def test_injected_backend_narrate_exception_uses_templates():
    llm = LLMModule(text_backend=RaisingCompletion())
    rn = llm.narrate(
        "assist_emergency",
        "collapse",
        "Good",
        0.9,
        "c",
        "c",
        "o",
    )
    assert rn.synthesis
