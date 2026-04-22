"""Fuzz-style tests for perception JSON coercion and raw parse (NaN, odd types, bad JSON)."""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.perception.perception_schema import (
    parse_perception_llm_raw_response,
    validate_perception_dict,
)


def test_validate_perception_dict_nan_and_inf_default_to_field_defaults():
    r = validate_perception_dict(
        {"risk": float("nan"), "urgency": float("inf"), "hostility": float("-inf")},
        report=None,
    )
    assert r["risk"] == 0.5
    assert r["urgency"] == 0.5
    assert r["hostility"] == 0.0


def test_validate_perception_dict_nested_and_array_inputs_are_defaulted():
    r = validate_perception_dict(
        {
            "risk": [0.2],
            "urgency": {"x": 0.3},
            "hostility": [[0.1]],
        },
        report=None,
    )
    assert r["risk"] == 0.5
    assert r["urgency"] == 0.5
    assert r["hostility"] == 0.0


def test_validate_perception_dict_clamps_out_of_range():
    r = validate_perception_dict({"risk": 3.0, "calm": -2.0}, report=None)
    assert r["risk"] == 1.0
    assert r["calm"] == 0.0


def test_validate_perception_dict_non_dict_payload_becomes_defaults():
    r = validate_perception_dict(["not", "a", "dict"], report=None)
    assert r["suggested_context"] == "everyday_ethics"
    assert r["risk"] == 0.5


def test_validate_perception_dict_summary_non_string_coerced():
    r = validate_perception_dict({"summary": ["a", "b"]}, report=None)
    assert "a" in r["summary"]


def test_parse_perception_malformed_json_records_issue():
    p = parse_perception_llm_raw_response("not-json-at-all {")
    assert "json_decode_error" in p.issues
    assert p.data == {}


def test_parse_perception_non_object_payload():
    p = parse_perception_llm_raw_response("[1, 2, 3]")
    assert "non_object_payload" in p.issues


def test_parse_perception_fenced_garbage_inside():
    p = parse_perception_llm_raw_response("```json\noops not valid\n```")
    assert "json_decode_error" in p.issues


def test_validate_perception_report_counts_invalid_fields():
    from src.modules.perception.perception_schema import PerceptionCoercionReport

    rep = PerceptionCoercionReport()
    validate_perception_dict({"risk": math.nan, "urgency": object()}, report=rep)
    assert "risk" in rep.fields_defaulted
    assert "urgency" in rep.fields_defaulted
