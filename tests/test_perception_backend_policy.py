"""KERNEL_PERCEPTION_BACKEND_POLICY — degraded perception recovery paths."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.llm_backends import LLMBackend
from src.modules.cognition.llm_layer import LLMModule
from src.modules.perception.perception_backend_policy import (
    DEFAULT_KERNEL_PERCEPTION_BACKEND_POLICY,
    resolve_perception_backend_policy,
)


class _BoomBackend(LLMBackend):
    def is_available(self) -> bool:
        return True

    def completion(self, system: str, user: str, **kwargs: object) -> str:
        raise RuntimeError("simulated transport failure")

    def embedding(self, text: str) -> list[float] | None:
        return None

    def info(self) -> dict:
        return {"name": "boom", "base_url": ""}


def test_default_backend_policy_constant():
    assert DEFAULT_KERNEL_PERCEPTION_BACKEND_POLICY == "template_local"


def test_resolve_policy_invalid_env_falls_back(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_BACKEND_POLICY", "not_a_real_mode")
    assert resolve_perception_backend_policy() == "template_local"


def test_transport_exception_template_local_marks_degradation(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_BACKEND_POLICY", "template_local")
    llm = LLMModule(llm_backend=_BoomBackend())
    p = llm.perceive("hello there")
    cr = p.coercion_report
    assert cr is not None
    assert cr["backend_degraded"] is True
    assert cr["backend_failure_reason"] == "llm_completion_exception"
    assert "llm_perception_backend_degraded" in cr["parse_issues"]


def test_transport_exception_fast_fail_avoids_keyword_escalation(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_BACKEND_POLICY", "fast_fail")
    llm = LLMModule(llm_backend=_BoomBackend())
    p = llm.perceive("someone has a gun and is shooting")
    assert p.suggested_context == "everyday_ethics"
    assert p.coercion_report is not None
    assert p.coercion_report["backend_degradation_mode"] == "fast_fail"
    assert p.hostility < 0.85


def test_session_banner_recommended_flag(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_BACKEND_POLICY", "session_banner")
    llm = LLMModule(llm_backend=_BoomBackend())
    p = llm.perceive("ping")
    assert p.coercion_report["session_banner_recommended"] is True


def test_chat_json_surfaces_perception_backend_banner():
    from src.chat_server import _chat_turn_to_jsonable
    from src.kernel import ChatTurnResult, EthicalKernel
    from src.modules.cognition.llm_layer import LLMPerception, VerbalResponse

    k = EthicalKernel(variability=False)
    p = LLMPerception(
        risk=0.5,
        urgency=0.5,
        hostility=0.0,
        calm=0.5,
        vulnerability=0.0,
        legality=1.0,
        manipulation=0.0,
        familiarity=0.0,
        social_tension=0.0,
        suggested_context="everyday_ethics",
        summary="x",
        coercion_report={
            "session_banner_recommended": True,
            "uncertainty": 0.9,
            "parse_issues": [],
            "fields_defaulted": [],
            "fields_clamped": [],
        },
    )
    r = ChatTurnResult(
        response=VerbalResponse(message="m", tone="calm", hax_mode="n", inner_voice=""),
        path="light",
        perception=p,
    )
    out = _chat_turn_to_jsonable(r, k)
    assert out.get("perception_backend_banner") is True
