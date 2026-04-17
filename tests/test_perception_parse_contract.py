"""Structured perception JSON parse issues (LLM output contract, hardening)."""

import json

from src.modules.perception_schema import (
    merge_parse_issues_into_perception,
    parse_perception_llm_raw_response,
)


def test_parse_empty_and_invalid_json():
    r = parse_perception_llm_raw_response("")
    assert r.data == {}
    assert "empty_response" in r.issues

    r2 = parse_perception_llm_raw_response("{not json")
    assert r2.data == {}
    assert "json_decode_error" in r2.issues


def test_parse_non_object_and_empty_object():
    r = parse_perception_llm_raw_response(json.dumps([1, 2]))
    assert r.data == {}
    assert "non_object_payload" in r.issues

    r2 = parse_perception_llm_raw_response("{}")
    assert r2.data == {}
    assert "empty_object" in r2.issues


def test_parse_markdown_fence_and_valid():
    inner = '{"risk": 0.2, "suggested_context": "everyday_ethics"}'
    raw = f"```json\n{inner}\n```"
    r = parse_perception_llm_raw_response(raw)
    assert r.data.get("risk") == 0.2
    assert "empty_object" not in r.issues
    assert "json_decode_error" not in r.issues


def test_merge_parse_issues_into_perception_mutates():
    from src.modules.llm_layer import LLMPerception

    p = LLMPerception(
        risk=0.1,
        urgency=0.1,
        hostility=0.0,
        calm=0.7,
        vulnerability=0.0,
        legality=1.0,
        manipulation=0.0,
        familiarity=0.0,
        social_tension=0.0,
        suggested_context="everyday_ethics",
        summary="s",
        coercion_report=None,
    )
    merge_parse_issues_into_perception(p, ["json_decode_error"])
    assert p.coercion_report is not None
    assert "json_decode_error" in p.coercion_report["parse_issues"]
