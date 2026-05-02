from __future__ import annotations

import json
from pathlib import Path

from scripts.eval.desktop_e2e_demo_runner import run_demo_session, write_report


def test_run_demo_session_passes_and_keeps_step_order() -> None:
    report = run_demo_session(
        transcript="demo transcript",
        voice_utterance="hola demo",
        voice_reply="reply demo",
    )

    assert report["passed"] is True
    assert report["mode"] == "local-testclient-stt-mocked"
    assert report["evidence_posture"] == "G4_EXECUTABLE_LOCAL"
    step_names = [step["name"] for step in report["steps"]]
    assert step_names == [
        "ping",
        "status_before_turn",
        "audio_turn",
        "status_after_turn",
        "voice_turn",
    ]
    for step in report["steps"]:
        assert step["passed"] is True
        assert isinstance(step["latency_ms"], float)
        assert step["latency_ms"] >= 0.0

    voice_step = next(step for step in report["steps"] if step["name"] == "voice_turn")
    assert voice_step["details"]["contract"] == "voice_turn"
    assert voice_step["details"]["reply_chars"] >= 1
    assert voice_step["details"]["should_listen"] is True


def test_write_report_persists_json_payload(tmp_path: Path) -> None:
    path = tmp_path / "demo_report.json"
    payload = {"run_id": "demo-1", "passed": True, "steps": []}

    write_report(path, payload)

    assert path.exists()
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert parsed["run_id"] == "demo-1"
    assert parsed["passed"] is True
