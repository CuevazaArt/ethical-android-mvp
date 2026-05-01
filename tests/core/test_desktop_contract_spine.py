import json
from pathlib import Path

from jsonschema import Draft202012Validator

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "contracts"

CONTRACT_SCHEMA = {
    "type": "object",
    "required": ["version", "contract", "request", "response", "error", "latency_ms"],
    "properties": {
        "version": {"const": "1.0"},
        "contract": {"enum": ["audio_perception", "video_perception", "voice_turn"]},
        "request": {"type": "object"},
        "response": {"type": "object"},
        "error": {
            "anyOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "required": ["code", "message", "retryable"],
                    "properties": {
                        "code": {"type": "string", "minLength": 1},
                        "message": {"type": "string", "minLength": 1},
                        "retryable": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            ]
        },
        "latency_ms": {"type": "number", "minimum": 0},
    },
    "allOf": [
        {
            "if": {"properties": {"contract": {"const": "audio_perception"}}},
            "then": {
                "properties": {
                    "request": {
                        "type": "object",
                        "required": ["audio_b64", "sample_rate_hz"],
                        "properties": {
                            "audio_b64": {"type": "string", "minLength": 1},
                            "sample_rate_hz": {
                                "type": "integer",
                                "minimum": 8000,
                                "maximum": 96000,
                            },
                        },
                    },
                    "response": {
                        "type": "object",
                        "required": ["transcript", "confidence"],
                        "properties": {
                            "transcript": {"type": "string"},
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                        },
                    },
                }
            },
        },
        {
            "if": {"properties": {"contract": {"const": "video_perception"}}},
            "then": {
                "properties": {
                    "request": {
                        "type": "object",
                        "required": ["frame_b64", "frame_format", "width", "height"],
                        "properties": {
                            "frame_b64": {"type": "string", "minLength": 1},
                            "frame_format": {"enum": ["jpeg", "png"]},
                            "width": {"type": "integer", "minimum": 1},
                            "height": {"type": "integer", "minimum": 1},
                        },
                    },
                    "response": {
                        "type": "object",
                        "required": ["labels", "motion", "faces_detected"],
                        "properties": {
                            "labels": {"type": "array", "items": {"type": "string"}},
                            "motion": {"type": "number", "minimum": 0, "maximum": 1},
                            "faces_detected": {"type": "integer", "minimum": 0},
                        },
                    },
                }
            },
        },
        {
            "if": {"properties": {"contract": {"const": "voice_turn"}}},
            "then": {
                "properties": {
                    "request": {
                        "type": "object",
                        "required": ["utterance"],
                        "properties": {"utterance": {"type": "string", "minLength": 1}},
                    },
                    "response": {
                        "type": "object",
                        "required": ["reply_text", "should_listen"],
                        "properties": {
                            "reply_text": {"type": "string"},
                            "should_listen": {"type": "boolean"},
                        },
                    },
                }
            },
        },
    ],
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_spine_accepts_valid_payloads():
    validator = Draft202012Validator(CONTRACT_SCHEMA)
    valid_payloads = _load_json(FIXTURES_DIR / "valid_payloads.json")

    for payload in valid_payloads:
        errors = sorted(validator.iter_errors(payload), key=lambda e: e.path)
        assert not errors, (
            f"Expected valid payload, got errors: {[e.message for e in errors]}"
        )
        print(f"[valid] {payload['contract']} -> PASS")


def test_contract_spine_rejects_invalid_payloads():
    validator = Draft202012Validator(CONTRACT_SCHEMA)
    invalid_cases = _load_json(FIXTURES_DIR / "invalid_payloads.json")

    for case in invalid_cases:
        errors = sorted(validator.iter_errors(case["payload"]), key=lambda e: e.path)
        assert errors, f"Expected invalid payload for case={case['name']}"
        print(f"[invalid] {case['name']} -> {errors[0].message}")
