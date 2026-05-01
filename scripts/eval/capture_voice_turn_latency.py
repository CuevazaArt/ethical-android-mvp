from __future__ import annotations

import argparse
import base64
import json
import math
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build_audio_payload(*, sample_rate_hz: int = 16000, pcm_frames: int = 2048) -> dict[str, Any]:
    fake_pcm = b"\x01\x00" * pcm_frames
    return {
        "version": "1.0",
        "contract": "audio_perception",
        "request": {
            "audio_b64": base64.b64encode(fake_pcm).decode("ascii"),
            "sample_rate_hz": sample_rate_hz,
        },
        "response": {},
        "error": None,
        "latency_ms": 0.0,
    }


def coerce_non_negative_ms(value: Any) -> float:
    try:
        raw = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(raw) or raw < 0:
        return 0.0
    return raw


def _post_json(url: str, payload: dict[str, Any], *, timeout_s: float) -> tuple[int, dict[str, Any], float]:
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
) -> list[dict[str, Any]]:
    target = f"{base_url.rstrip('/')}/api/perception/audio"
    records: list[dict[str, Any]] = []
    for idx in range(sample_count):
        payload = build_audio_payload()
        row: dict[str, Any] = {
            "captured_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "sample_id": f"voice-turn-{idx + 1:03d}",
            "source": "live_capture",
            "endpoint": target,
        }
        try:
            http_status, data, roundtrip_ms = _post_json(target, payload, timeout_s=timeout_s)
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture live voice-turn latency samples.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--timeout-s", type=float, default=3.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl"),
    )
    args = parser.parse_args()

    rows = capture_samples(
        base_url=args.base_url,
        sample_count=max(1, args.samples),
        timeout_s=max(0.1, args.timeout_s),
    )
    successful = [row for row in rows if coerce_non_negative_ms(row.get("total_ms")) > 0]
    if successful:
        write_jsonl(args.output, successful)
    else:
        # Keep file deterministic even on failure.
        write_jsonl(args.output, rows)
    print(json.dumps({"captured": len(rows), "successful": len(successful)}, ensure_ascii=True, indent=2))
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
