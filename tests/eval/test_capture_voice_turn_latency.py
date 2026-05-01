from __future__ import annotations

from scripts.eval.capture_voice_turn_latency import (
    build_audio_payload,
    coerce_non_negative_ms,
)


def test_build_audio_payload_uses_audio_contract_shape() -> None:
    payload = build_audio_payload(sample_rate_hz=16000, pcm_frames=64)
    assert payload["version"] == "1.0"
    assert payload["contract"] == "audio_perception"
    assert payload["request"]["sample_rate_hz"] == 16000
    assert isinstance(payload["request"]["audio_b64"], str)
    assert payload["latency_ms"] == 0.0


def test_coerce_non_negative_ms_blocks_non_finite_values() -> None:
    assert coerce_non_negative_ms("15.5") == 15.5
    assert coerce_non_negative_ms(-1) == 0.0
    assert coerce_non_negative_ms(float("inf")) == 0.0
    assert coerce_non_negative_ms("bad") == 0.0

