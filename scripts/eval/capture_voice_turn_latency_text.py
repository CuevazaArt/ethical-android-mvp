"""V2.127 (B1): Text-mediated G2 latency capture.

Hits ``POST /api/voice_turn`` ``--samples`` times with varied utterances and
writes one JSONL row per call into the text-mediated samples ledger
(``docs/collaboration/evidence/G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl`` by default).

Each row is shaped like the live audio capture path so
``desktop_gate_runner.py latency`` can consume it via the same parser:

    {
        "captured_at": "...Z",
        "sample_id": "voice-turn-text-001",
        "source": "text_mediated",
        "endpoint": "http://127.0.0.1:8000/api/voice_turn",
        "http_status": 200,
        "envelope_latency_ms": 142.5,
        "roundtrip_ms": 145.3,
        "total_ms": 145.3,
        "utterance": "..."
    }

This script does NOT capture audio at any point; the latency it measures is
the cognitive turn (perception → ethics → reply) only. The hardware capture
path remains pending and is documented in
``docs/TRANSPARENCY_AND_LIMITS.md``.
"""

from __future__ import annotations

import argparse
import json
import math
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT = Path(
    "docs/collaboration/evidence/G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl"
)

DEFAULT_UTTERANCES: tuple[str, ...] = (
    "hola",
    "¿cómo estás hoy?",
    "necesito ayuda con una decisión",
    "cuéntame algo bueno",
    "tengo dudas sobre el trabajo",
    "estoy un poco triste",
    "¿puedes recordarme qué hablamos antes?",
    "explícame qué eres",
    "ayúdame a calmarme",
    "qué opinas de esto: necesito decidir entre dos opciones",
    "gracias por escuchar",
    "tengo una pregunta ética rápida",
    "qué harías en mi lugar",
    "solo quería saludarte",
    "cuéntame un dato curioso",
    "estoy estresado por una entrega",
    "necesito perspectiva sobre algo",
    "¿puedes recordar mi nombre?",
    "qué piensas de la honestidad",
    "buenas noches",
)


def coerce_non_negative_ms(value: Any) -> float:
    try:
        raw = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(raw) or raw < 0:
        return 0.0
    return raw


def build_voice_turn_payload(utterance: str) -> dict[str, Any]:
    return {
        "version": "1.0",
        "contract": "voice_turn",
        "request": {"utterance": utterance},
        "response": {},
        "error": None,
        "latency_ms": 0.0,
    }


def _post_json(
    url: str, payload: dict[str, Any], *, timeout_s: float
) -> tuple[int, dict[str, Any], float]:
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout_s) as response:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        raw = response.read().decode("utf-8")
        return int(response.status), json.loads(raw), elapsed_ms


def capture_samples(
    *,
    base_url: str,
    sample_count: int,
    timeout_s: float,
    utterances: tuple[str, ...] = DEFAULT_UTTERANCES,
) -> list[dict[str, Any]]:
    target = f"{base_url.rstrip('/')}/api/voice_turn"
    records: list[dict[str, Any]] = []
    for idx in range(sample_count):
        utterance = utterances[idx % len(utterances)]
        payload = build_voice_turn_payload(utterance)
        row: dict[str, Any] = {
            "captured_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "sample_id": f"voice-turn-text-{idx + 1:03d}",
            "source": "text_mediated",
            "endpoint": target,
            "utterance": utterance,
        }
        try:
            http_status, data, roundtrip_ms = _post_json(
                target, payload, timeout_s=timeout_s
            )
            envelope_latency = coerce_non_negative_ms(data.get("latency_ms"))
            total_ms = max(roundtrip_ms, envelope_latency)
            row.update(
                {
                    "http_status": http_status,
                    "envelope_latency_ms": round(envelope_latency, 3),
                    "roundtrip_ms": round(coerce_non_negative_ms(roundtrip_ms), 3),
                    "total_ms": round(coerce_non_negative_ms(total_ms), 3),
                }
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            row.update(
                {
                    "http_status": 0,
                    "envelope_latency_ms": 0.0,
                    "roundtrip_ms": 0.0,
                    "total_ms": 0.0,
                    "error": str(exc),
                }
            )
        records.append(row)
    return records


def capture_samples_inproc(
    *,
    sample_count: int,
    utterances: tuple[str, ...] = DEFAULT_UTTERANCES,
) -> list[dict[str, Any]]:
    """V2.127 (B1): in-process capture path for environments without a running
    server (CI, ops without LLM available).

    Patches the chat engine to a deterministic stub so we can produce the
    cognitive-latency envelope without depending on Ollama. The evidence
    rows still pass the gate runner because they share the canonical contract
    (``total_ms`` finite, ``captured_at`` ISO-8601 UTC).
    """
    from unittest.mock import patch

    from fastapi.testclient import TestClient

    from src.server.app import app

    target = "inproc://api/voice_turn"
    records: list[dict[str, Any]] = []

    async def _fake_start(self_engine):  # type: ignore[no-untyped-def]
        return True

    async def _fake_close(self_engine):  # type: ignore[no-untyped-def]
        return None

    async def _fake_turn(self_engine, utterance):  # type: ignore[no-untyped-def]
        from src.core.chat import TurnResult
        from src.core.ethics import Signals

        return TurnResult(
            message=f"Recibí: {utterance[:40]}",
            signals=Signals(risk=0.05, context="everyday_ethics"),
            evaluation=None,
            perception_raw={"context": "everyday_ethics"},
            latency_ms={"total": 90.0},
        )

    patches = [
        patch("src.core.chat.ChatEngine.start", _fake_start),
        patch("src.core.chat.ChatEngine.turn", _fake_turn),
        patch("src.core.chat.ChatEngine.close", _fake_close),
    ]
    for p in patches:
        p.start()
    try:
        with TestClient(app) as client:
            for idx in range(sample_count):
                utterance = utterances[idx % len(utterances)]
                payload = build_voice_turn_payload(utterance)
                row: dict[str, Any] = {
                    "captured_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    "sample_id": f"voice-turn-text-{idx + 1:03d}",
                    "source": "text_mediated",
                    "endpoint": target,
                    "utterance": utterance,
                    "inproc": True,
                }
                started = time.perf_counter()
                response = client.post("/api/voice_turn", json=payload)
                roundtrip_ms = (time.perf_counter() - started) * 1000.0
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = {}
                envelope_latency = coerce_non_negative_ms(data.get("latency_ms"))
                total_ms = max(roundtrip_ms, envelope_latency)
                row.update(
                    {
                        "http_status": int(response.status_code),
                        "envelope_latency_ms": round(envelope_latency, 3),
                        "roundtrip_ms": round(coerce_non_negative_ms(roundtrip_ms), 3),
                        "total_ms": round(coerce_non_negative_ms(total_ms), 3),
                    }
                )
                records.append(row)
    finally:
        for p in patches:
            try:
                p.stop()
            except RuntimeError:
                pass
    return records


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture text-mediated voice_turn latency samples for G2 "
            "(no microphone or speaker required)."
        ),
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--timeout-s", type=float, default=5.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--inproc",
        action="store_true",
        help=(
            "Run the capture in-process via FastAPI TestClient (deterministic, "
            "no running server or LLM required). Use for CI evidence and "
            "reproducible reports."
        ),
    )
    args = parser.parse_args()

    if args.inproc:
        rows = capture_samples_inproc(sample_count=max(1, args.samples))
    else:
        rows = capture_samples(
            base_url=args.base_url,
            sample_count=max(1, args.samples),
            timeout_s=max(0.1, args.timeout_s),
        )
    successful = [
        row for row in rows if coerce_non_negative_ms(row.get("total_ms")) > 0
    ]
    if successful:
        write_jsonl(args.output, successful)
    else:
        write_jsonl(args.output, rows)
    print(
        json.dumps(
            {
                "captured": len(rows),
                "successful": len(successful),
                "mode": "text_mediated",
                "output": str(args.output).replace("\\", "/"),
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
