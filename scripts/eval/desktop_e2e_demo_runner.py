from __future__ import annotations

import argparse
import base64
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.server.app import app


def _audio_contract_payload(*, audio_b64: str, sample_rate_hz: int = 16000) -> dict[str, Any]:
    return {
        "version": "1.0",
        "contract": "audio_perception",
        "request": {
            "audio_b64": audio_b64,
            "sample_rate_hz": sample_rate_hz,
        },
        "response": {},
        "error": None,
        "latency_ms": 0.0,
    }


def _voice_turn_payload(*, utterance: str) -> dict[str, Any]:
    return {
        "version": "1.0",
        "contract": "voice_turn",
        "request": {"utterance": utterance},
        "response": {},
        "error": None,
        "latency_ms": 0.0,
    }


def _safe_latency_ms(start_t: float) -> float:
    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
    if not math.isfinite(elapsed_ms) or elapsed_ms < 0.0:
        return 0.0
    return elapsed_ms


def _run_step(name: str, fn: Any) -> dict[str, Any]:
    start_t = time.perf_counter()
    try:
        details = fn()
        return {
            "name": name,
            "passed": True,
            "latency_ms": _safe_latency_ms(start_t),
            "details": details,
        }
    except Exception as exc:  # pragma: no cover - surfaced as report evidence
        return {
            "name": name,
            "passed": False,
            "latency_ms": _safe_latency_ms(start_t),
            "details": {"error": str(exc)},
        }


def run_demo_session(
    *,
    transcript: str = "ethos demo turn acknowledged",
    voice_utterance: str = "Hola Ethos, este es un turno de demo.",
    voice_reply: str = "Entendido. Estoy aquí para ayudarte.",
) -> dict[str, Any]:
    fake_pcm = b"\x01\x00" * 2048
    audio_payload = _audio_contract_payload(
        audio_b64=base64.b64encode(fake_pcm).decode("utf-8"),
    )
    voice_payload = _voice_turn_payload(utterance=voice_utterance)
    steps: list[dict[str, Any]] = []

    class _StubVoiceResult:
        def __init__(self) -> None:
            self.message = voice_reply
            self.signals = None
            self.evaluation = None
            self.perception_raw = {"context": "demo", "blocked": False}
            self.latency_ms = {"total": 12.0}

    with (
        patch(
            "src.server.app.transcribe_pcm",
            new_callable=AsyncMock,
            return_value=transcript,
        ),
        patch(
            "src.server.app.ChatEngine.start",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "src.server.app.ChatEngine.turn",
            new_callable=AsyncMock,
            return_value=_StubVoiceResult(),
        ),
        patch(
            "src.server.app.ChatEngine.close",
            new_callable=AsyncMock,
            return_value=None,
        ),
        TestClient(app) as client,
    ):
        steps.append(_run_step("ping", lambda: _assert_ping(client)))
        steps.append(
            _run_step("status_before_turn", lambda: _assert_status(client))
        )
        steps.append(
            _run_step(
                "audio_turn", lambda: _assert_audio_turn(client, audio_payload)
            )
        )
        steps.append(
            _run_step(
                "status_after_turn", lambda: _assert_status_after_turn(client)
            )
        )
        steps.append(
            _run_step(
                "voice_turn",
                lambda: _assert_voice_turn(client, voice_payload, voice_reply),
            )
        )

    passed = all(bool(step["passed"]) for step in steps)
    return {
        "run_id": f"desktop-e2e-demo-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
        "mode": "local-testclient-stt-mocked",
        "evidence_posture": "G4_EXECUTABLE_LOCAL",
        "passed": passed,
        "steps": steps,
    }


def _assert_ping(client: TestClient) -> dict[str, Any]:
    response = client.get("/api/ping")
    if response.status_code != 200:
        raise ValueError(f"unexpected ping status: {response.status_code}")
    payload = response.json()
    if not bool(payload.get("pong")):
        raise ValueError("ping payload missing pong=true")
    return {
        "status_code": response.status_code,
        "pong": True,
        "uptime_s": int(payload.get("uptime_s", 0)),
    }


def _assert_status(client: TestClient) -> dict[str, Any]:
    response = client.get("/api/status")
    if response.status_code != 200:
        raise ValueError(f"unexpected status status_code: {response.status_code}")
    payload = response.json()
    required = ("status", "voice_turn_state", "reentry_gates")
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"status payload missing keys: {missing}")
    return {
        "status_code": response.status_code,
        "status": str(payload.get("status", "")),
        "voice_turn_state": str(payload.get("voice_turn_state", "")),
    }


def _assert_audio_turn(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/perception/audio", json=payload)
    if response.status_code != 200:
        raise ValueError(f"unexpected audio status_code: {response.status_code}")
    body = response.json()
    if str(body.get("contract", "")) != "audio_perception":
        raise ValueError("audio response contract drift")
    transcript = str(body.get("response", {}).get("transcript", ""))
    if not transcript.strip():
        raise ValueError("audio turn returned empty transcript")
    latency_ms = float(body.get("latency_ms", 0.0))
    if not math.isfinite(latency_ms) or latency_ms < 0.0:
        raise ValueError("audio turn latency is non-finite")
    return {
        "status_code": response.status_code,
        "contract": "audio_perception",
        "transcript_chars": len(transcript),
        "latency_ms": latency_ms,
    }


def _assert_status_after_turn(client: TestClient) -> dict[str, Any]:
    response = client.get("/api/status")
    if response.status_code != 200:
        raise ValueError(f"unexpected status-after-turn code: {response.status_code}")
    payload = response.json()
    state = str(payload.get("voice_turn_state", ""))
    if state != "responding":
        raise ValueError(f"voice_turn_state expected responding, got: {state}")
    return {
        "status_code": response.status_code,
        "voice_turn_state": state,
    }


def _assert_voice_turn(
    client: TestClient,
    payload: dict[str, Any],
    expected_reply: str,
) -> dict[str, Any]:
    response = client.post("/api/voice_turn", json=payload)
    if response.status_code != 200:
        raise ValueError(f"unexpected voice_turn status: {response.status_code}")
    body = response.json()
    if str(body.get("contract", "")) != "voice_turn":
        raise ValueError("voice_turn response contract drift")
    response_body = body.get("response", {})
    reply = str(response_body.get("reply_text", ""))
    if not reply.strip():
        raise ValueError("voice_turn returned empty reply_text")
    if reply.strip() != expected_reply.strip():
        raise ValueError(
            f"voice_turn reply mismatch: expected={expected_reply!r} got={reply!r}"
        )
    listen = response_body.get("should_listen")
    if not isinstance(listen, bool):
        raise ValueError("voice_turn should_listen must be bool")
    latency_ms = float(body.get("latency_ms", 0.0))
    if not math.isfinite(latency_ms) or latency_ms < 0.0:
        raise ValueError("voice_turn latency is non-finite")
    return {
        "status_code": response.status_code,
        "contract": "voice_turn",
        "reply_chars": len(reply),
        "should_listen": listen,
        "latency_ms": latency_ms,
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run reproducible local desktop E2E demo evidence for G4."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/collaboration/evidence/DESKTOP_E2E_DEMO_REPORT.json"),
    )
    args = parser.parse_args()

    payload = run_demo_session()
    write_report(args.output, payload)
    print(
        json.dumps(
            {
                "run_id": payload["run_id"],
                "passed": payload["passed"],
                "steps": len(payload["steps"]),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0 if bool(payload["passed"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
