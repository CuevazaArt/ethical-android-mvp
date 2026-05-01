from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.eval.append_stability_ledger import append_stability_entry


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_append_stability_entry_rejects_duplicate_day(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    append_stability_entry(
        ledger,
        timestamp="2026-05-01T09:00:00Z",
        status="pass",
        cycle="desktop-smoke",
        note="ok",
    )

    with pytest.raises(ValueError, match="already exists"):
        append_stability_entry(
            ledger,
            timestamp="2026-05-01T12:00:00Z",
            status="pass",
            cycle="desktop-smoke",
            note="duplicate",
        )


def test_append_stability_entry_can_replace_day(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    append_stability_entry(
        ledger,
        timestamp="2026-05-01T09:00:00Z",
        status="pass",
        cycle="desktop-smoke",
        note="first",
    )
    append_stability_entry(
        ledger,
        timestamp="2026-05-01T10:00:00Z",
        status="fail",
        cycle="desktop-smoke",
        note="replaced",
        replace_existing_day=True,
    )

    rows = _read_jsonl(ledger)
    assert len(rows) == 1
    assert rows[0]["status"] == "fail"
    assert str(rows[0]["date"]).startswith("2026-05-01")
