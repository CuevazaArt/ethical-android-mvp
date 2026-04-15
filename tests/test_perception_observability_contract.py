"""WebSocket JSON contract for perception observability fields."""

from src.chat_server import _chat_turn_to_jsonable
from src.kernel import ChatTurnResult, EthicalKernel
from src.modules.llm_layer import LLMPerception, VerbalResponse


def _mk_perception(*, coercion_report):
    return LLMPerception(
        risk=0.4,
        urgency=0.4,
        hostility=0.1,
        calm=0.7,
        vulnerability=0.1,
        legality=1.0,
        manipulation=0.0,
        familiarity=0.0,
        suggested_context="everyday_ethics",
        summary="ok",
        coercion_report=coercion_report,
    )


def test_chat_json_always_includes_canonical_coercion_report():
    k = EthicalKernel(variability=False)
    p = _mk_perception(coercion_report=None)
    r = ChatTurnResult(
        response=VerbalResponse(message="m", tone="calm", hax_mode="n", inner_voice=""),
        path="light",
        perception=p,
    )
    out = _chat_turn_to_jsonable(r, k)

    cr = out["perception"]["coercion_report"]
    assert isinstance(cr, dict)
    assert "uncertainty" in cr
    assert "parse_issues" in cr
    assert "backend_degraded" in cr
    assert isinstance(out.get("perception_observability"), dict)
    assert out["perception_observability"]["uncertainty"] == cr["uncertainty"]


def test_chat_json_observability_flags_reflect_report_and_doubt():
    k = EthicalKernel(variability=False)
    p = _mk_perception(
        coercion_report={
            "backend_degraded": True,
            "session_banner_recommended": True,
            "perception_dual_high_discrepancy": True,
            "parse_issues": ["x"],
            "fields_defaulted": [],
            "fields_clamped": [],
            "uncertainty": 0.91,
        }
    )
    r = ChatTurnResult(
        response=VerbalResponse(message="m", tone="calm", hax_mode="n", inner_voice=""),
        path="light",
        perception=p,
        metacognitive_doubt=True,
    )
    out = _chat_turn_to_jsonable(r, k)

    assert out.get("perception_backend_banner") is True
    obs = out["perception_observability"]
    assert obs["backend_degraded"] is True
    assert obs["dual_high_discrepancy"] is True
    assert obs["metacognitive_doubt"] is True
