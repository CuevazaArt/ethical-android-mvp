from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _run_powershell_json(command: str) -> Any:
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return {"error": completed.stderr.strip(), "stdout": completed.stdout.strip()}
    stdout = completed.stdout.strip()
    if not stdout:
        return []
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def _normalize_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    return []


def collect_preflight() -> dict[str, Any]:
    camera_payload = _run_powershell_json(
        "Get-PnpDevice | Where-Object { ($_.Class -in @('Camera','Image')) -or ($_.FriendlyName -match 'camera|webcam') } "
        "| Select-Object -Property Status,Class,FriendlyName | ConvertTo-Json"
    )
    audio_payload = _run_powershell_json(
        "Get-PnpDevice -Class AudioEndpoint | Select-Object -Property Status,Class,FriendlyName | ConvertTo-Json"
    )
    mic_payload = _run_powershell_json(
        "Get-PnpDevice -Class AudioEndpoint | "
        "Where-Object { $_.FriendlyName -match 'microphone|mic|input' } "
        "| Select-Object -Property Status,Class,FriendlyName | ConvertTo-Json"
    )

    cameras = _normalize_rows(camera_payload)
    audio_endpoints = _normalize_rows(audio_payload)
    microphones = _normalize_rows(mic_payload)

    ready = bool(cameras) and bool(audio_endpoints) and bool(microphones)
    return {
        "captured_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "camera_devices": cameras,
        "audio_endpoints": audio_endpoints,
        "microphone_devices": microphones,
        "preflight_ready": ready,
        "summary": {
            "camera_count": len(cameras),
            "audio_endpoint_count": len(audio_endpoints),
            "microphone_count": len(microphones),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect perception pilot hardware preflight report."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/collaboration/evidence/PERCEPTION_HARDWARE_PREFLIGHT.json"),
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Return non-zero when preflight_ready is false.",
    )
    args = parser.parse_args()

    report = collect_preflight()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))

    if args.require_ready and not bool(report.get("preflight_ready", False)):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
