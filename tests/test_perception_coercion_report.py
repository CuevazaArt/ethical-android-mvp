"""Perception JSON coercion diagnostics (production hardening surface)."""

from src.modules.llm_layer import perception_from_llm_json
from src.modules.perception_schema import PerceptionCoercionReport, validate_perception_dict


def test_validate_perception_clean_payload_low_uncertainty():
    r = PerceptionCoercionReport()
    validate_perception_dict(
        {
            "risk": 0.2,
            "urgency": 0.3,
            "hostility": 0.1,
            "calm": 0.6,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.0,
            "social_tension": 0.0,
            "suggested_context": "everyday_ethics",
            "summary": "ok",
        },
        report=r,
    )
    d = r.to_public_dict()
    assert d["uncertainty"] == 0.0
    assert not d["non_dict_payload"]
    assert not d["context_fallback"]
    assert d["fields_defaulted"] == []
    assert d["fields_clamped"] == []


def test_non_dict_and_bad_context_raise_uncertainty():
    r = PerceptionCoercionReport()
    validate_perception_dict(["not", "a", "dict"], report=r)
    assert r.non_dict_payload
    assert r.uncertainty() >= 0.4

    r2 = PerceptionCoercionReport()
    validate_perception_dict({"suggested_context": "nope"}, report=r2)
    assert r2.context_fallback


def test_clamped_and_defaulted_fields_tracked():
    r = PerceptionCoercionReport()
    validate_perception_dict(
        {"risk": 9.0, "urgency": "x", "suggested_context": "everyday_ethics"},
        report=r,
    )
    assert "risk" in r.fields_clamped
    assert "urgency" in r.fields_defaulted
    assert r.uncertainty() > 0.1


def test_perception_from_llm_json_includes_coercion_report():
    p = perception_from_llm_json({"risk": "bad"}, "scene")
    assert p.coercion_report is not None
    assert p.coercion_report["uncertainty"] > 0


def test_local_heuristic_path_omits_coercion_report():
    from src.modules.llm_layer import LLMModule

    m = LLMModule(mode="local")
    p = m._perceive_local("someone has a medical emergency here")
    assert p.coercion_report is None
