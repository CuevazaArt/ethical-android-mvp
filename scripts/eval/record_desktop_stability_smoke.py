from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.server.app import app


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, ensure_ascii=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{payload}\n")


def run_stability_smoke() -> tuple[bool, str]:
    with (
        patch(
            "src.core.llm.OllamaClient.is_available",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "src.core.llm.OllamaClient.extract_json",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "src.core.llm.OllamaClient.chat",
            new_callable=AsyncMock,
            return_value="ok",
        ),
        TestClient(app) as client,
    ):
        ping = client.get("/api/ping")
        status = client.get("/api/status")
    if ping.status_code != 200:
        return False, f"ping status_code={ping.status_code}"
    if status.status_code != 200:
        return False, f"status status_code={status.status_code}"
    payload = status.json()
    if str(payload.get("status", "")) != "online":
        return False, "status payload is not online"
    if "voice_turn_state" not in payload:
        return False, "status payload missing voice_turn_state"
    return True, "No critical crash; ping/status smoke succeeded."


def main() -> int:
    parser = argparse.ArgumentParser(description="Record one G1 desktop stability smoke ledger row.")
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl"),
    )
    args = parser.parse_args()

    passed, note = run_stability_smoke()
    now = datetime.now(UTC).replace(microsecond=0)
    row = {
        "date": now.isoformat().replace("+00:00", "Z"),
        "status": "pass" if passed else "fail",
        "cycle": "desktop-smoke",
        "note": note,
    }
    _append_jsonl(args.ledger, row)
    print(json.dumps(row, ensure_ascii=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
