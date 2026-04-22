"""KERNEL_VERBAL_LLM_BACKEND_POLICY and verbal degradation event log."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.chat_server import _chat_turn_to_jsonable
from src.kernel import ChatTurnResult, EthicalKernel
from src.modules.cognition.llm_layer import LLMModule, VerbalResponse
from src.modules.cognition.llm_verbal_backend_policy import (
    DEFAULT_KERNEL_VERBAL_LLM_BACKEND_POLICY,
    resolve_verbal_llm_backend_policy,
)


class StaticCompletion:
    def __init__(self, text: str):
        self._text = text

    def complete(self, system: str, user: str) -> str:
        return self._text


class RaisingCompletion:
    def complete(self, system: str, user: str) -> str:
        raise RuntimeError("simulated transport failure")


def test_resolve_verbal_policy_default():
    assert resolve_verbal_llm_backend_policy() == DEFAULT_KERNEL_VERBAL_LLM_BACKEND_POLICY


def test_communicate_exception_canned_safe(monkeypatch):
    monkeypatch.setenv("KERNEL_VERBAL_LLM_BACKEND_POLICY", "canned_safe")
    llm = LLMModule(text_backend=RaisingCompletion())
    llm.reset_verbal_degradation_log()
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
    assert "language model path was unavailable" in vr.message.lower()
    ev = llm.verbal_degradation_events_snapshot()
    assert len(ev) == 1
    assert ev[0]["touchpoint"] == "communicate"
    assert ev[0]["failure_reason"] == "llm_completion_exception"
    assert ev[0]["recovery_policy"] == "canned_safe"


def test_communicate_empty_json_records_and_templates(monkeypatch):
    monkeypatch.setenv("KERNEL_VERBAL_LLM_BACKEND_POLICY", "template_local")
    llm = LLMModule(text_backend=StaticCompletion("{}"))
    llm.reset_verbal_degradation_log()
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
    assert vr.tone == "urgent"
    ev = llm.verbal_degradation_events_snapshot()
    assert len(ev) == 1
    assert ev[0]["failure_reason"] == "verbal_json_missing_or_empty"


def test_narrate_empty_json_canned_safe(monkeypatch):
    monkeypatch.setenv("KERNEL_VERBAL_LLM_BACKEND_POLICY", "canned_safe")
    llm = LLMModule(text_backend=StaticCompletion("not json"))
    llm.reset_verbal_degradation_log()
    rn = llm.narrate(
        "assist_emergency",
        "collapse",
        "Good",
        0.9,
        "c",
        "c",
        "o",
    )
    assert "unavailable" in rn.compassionate.lower()
    ev = llm.verbal_degradation_events_snapshot()
    assert len(ev) == 1
    assert ev[0]["touchpoint"] == "narrate"
    assert ev[0]["failure_reason"] == "verbal_json_missing_or_empty"
    assert ev[0]["recovery_policy"] == "canned_safe"


def test_monologue_annotate_degraded_on_failure(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_MONOLOGUE", "1")
    monkeypatch.setenv("KERNEL_LLM_TP_MONOLOGUE_POLICY", "annotate_degraded")

    llm = LLMModule(text_backend=RaisingCompletion())
    llm.reset_verbal_degradation_log()
    out = llm.optional_monologue_embellishment("base mono line")
    assert "monologue_llm_degraded" in out
    ev = llm.verbal_degradation_events_snapshot()
    assert len(ev) == 1 and ev[0]["touchpoint"] == "monologue"
    assert ev[0]["failure_reason"] == "llm_completion_exception"
    assert ev[0]["recovery_policy"] == "annotate_degraded"


def test_chat_json_includes_verbal_llm_observability():
    kernel = EthicalKernel(llm_mode="local")
    r = ChatTurnResult(
        response=VerbalResponse(message="ok", tone="calm", hax_mode="", inner_voice=""),
        path="light",
        verbal_llm_degradation_events=[
            {
                "touchpoint": "communicate",
                "failure_reason": "llm_completion_exception",
                "recovery_policy": "template_local",
            }
        ],
    )
    out = _chat_turn_to_jsonable(r, kernel)
    assert out.get("verbal_llm_observability", {}).get("degraded") is True
    assert len(out["verbal_llm_observability"]["events"]) == 1
