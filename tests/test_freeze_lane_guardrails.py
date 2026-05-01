from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "freeze_lane" / "smoke_payloads.json"
MATRIX_DOC = ROOT / "docs" / "collaboration" / "FREEZE_LANE_MAINTENANCE_MATRIX.md"

DESKTOP_ENVELOPE_SCHEMA = {
    "type": "object",
    "required": ["version", "contract", "request", "response", "error", "latency_ms"],
    "properties": {
        "version": {"const": "1.0"},
        "contract": {"enum": ["audio_perception", "video_perception", "voice_turn"]},
        "request": {"type": "object"},
        "response": {"type": "object"},
        "error": {"anyOf": [{"type": "null"}, {"type": "object"}]},
        "latency_ms": {"type": "number", "minimum": 0},
    },
}


def _load_payloads() -> dict:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def test_freeze_lane_valid_smokes_match_desktop_contract_envelope() -> None:
    validator = Draft202012Validator(DESKTOP_ENVELOPE_SCHEMA)
    payloads = _load_payloads()

    for case in payloads["valid"]:
        errors = sorted(validator.iter_errors(case["payload"]), key=lambda e: e.path)
        assert not errors, (
            f"Unexpected drift in lane={case['lane']}: {[e.message for e in errors]}"
        )
        print(
            f"[freeze-valid] lane={case['lane']} contract={case['payload']['contract']} -> PASS"
        )


def test_freeze_lane_invalid_smokes_are_detected() -> None:
    validator = Draft202012Validator(DESKTOP_ENVELOPE_SCHEMA)
    payloads = _load_payloads()

    for case in payloads["invalid"]:
        errors = sorted(validator.iter_errors(case["payload"]), key=lambda e: e.path)
        assert errors, (
            f"Expected drift detection for lane={case['lane']} reason={case['reason']}"
        )
        print(
            f"[freeze-invalid] lane={case['lane']} reason={case['reason']} -> {errors[0].message}"
        )


def test_freeze_matrix_defines_healthy_criterion_and_feature_freeze_rule() -> None:
    text = MATRIX_DOC.read_text(encoding="utf-8")
    must_have = [
        "Freeze Healthy Criterion",
        "No net-new feature merged in frozen lane paths",
        "Desktop contract no-drift check: PASS",
        "If any check fails, status is **DEGRADED**",
    ]
    for marker in must_have:
        assert marker in text, f"Missing freeze guardrail marker: {marker}"
