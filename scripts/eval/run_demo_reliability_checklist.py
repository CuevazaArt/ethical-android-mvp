from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class DemoCheck:
    id: str
    name: str
    command: list[str]


def _default_checks(python_exec: str) -> list[DemoCheck]:
    pytest = [python_exec, "-m", "pytest", "-q", "--tb=short"]
    return [
        DemoCheck("A1", "Audio perception success envelope", [*pytest, "tests/server/test_app_integration.py::test_audio_perception_happy_path_returns_transcript_and_latency"]),
        DemoCheck("A2", "Audio perception fallback envelope", [*pytest, "tests/server/test_app_integration.py::test_audio_perception_stt_fallback_when_transcription_unavailable"]),
        DemoCheck("A3", "Audio endpoint malformed payload tolerance", [*pytest, "tests/server/test_app_integration.py::test_audio_perception_invalid_sample_rate_returns_contract_error"]),
        DemoCheck("V1", "Video frame ws path with valid dimensions", [*pytest, "tests/server/test_app_integration.py::test_ws_chat_video_frame_updates_vision_state"]),
        DemoCheck("V2", "Video frame malformed dimensions no crash", [*pytest, "tests/server/test_app_integration.py::test_ws_chat_video_frame_with_malformed_dimensions_does_not_crash"]),
        DemoCheck("V3", "Video low-light/face_present strict token handling", [*pytest, "tests/server/test_desktop_video_adapter.py::test_sanitize_vision_context_rejects_invalid_boolean_tokens"]),
        DemoCheck("T1", "Voice turn state transitions to transcribing/responding", [*pytest, "tests/server/test_app_integration.py::test_audio_perception_success_updates_voice_turn_state"]),
        DemoCheck("T2", "Voice turn fallback resets to mic_off", [*pytest, "tests/server/test_app_integration.py::test_audio_perception_fallback_resets_voice_turn_state"]),
        DemoCheck("T3", "Video adapter rejects non-finite metrics", [*pytest, "tests/server/test_desktop_video_adapter.py::test_process_video_frame_rejects_non_finite_metrics"]),
        DemoCheck("T4", "Video adapter tolerates non-numeric dimensions", [*pytest, "tests/server/test_desktop_video_adapter.py::test_process_video_frame_tolerates_non_numeric_dimensions"]),
    ]


def run_check(check: DemoCheck, *, timeout_s: int) -> dict[str, object]:
    completed = subprocess.run(check.command, check=False, capture_output=True, text=True, timeout=timeout_s)
    passed = completed.returncode == 0
    snippet = (completed.stdout + "\n" + completed.stderr).strip()
    if len(snippet) > 600:
        snippet = snippet[:600] + "..."
    return {
        "id": check.id,
        "name": check.name,
        "passed": passed,
        "command": check.command,
        "return_code": completed.returncode,
        "log_excerpt": snippet,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run executable 10/10 demo reliability checklist.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/collaboration/evidence/DEMO_RELIABILITY_CHECKLIST.json"),
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--timeout-s", type=int, default=120)
    args = parser.parse_args()

    checks = _default_checks(args.python)
    results = [run_check(check, timeout_s=max(10, args.timeout_s)) for check in checks]
    payload = {
        "run_id": f"demo-reliability-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
        "operator": "automation-runner",
        "items": [{"id": row["id"], "name": row["name"], "passed": row["passed"]} for row in results],
        "details": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    passed = all(bool(item["passed"]) for item in payload["items"])
    print(json.dumps({"checks": len(results), "passed": sum(bool(item["passed"]) for item in payload["items"])}, ensure_ascii=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
