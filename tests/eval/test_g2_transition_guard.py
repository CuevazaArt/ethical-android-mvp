from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.eval.g2_transition_guard import evaluate_transition


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    payload = "\n".join(json.dumps(row) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def test_transition_blocks_when_hardware_is_not_ready(tmp_path: Path) -> None:
    provisional = tmp_path / "provisional.json"
    preflight = tmp_path / "preflight.json"
    samples = tmp_path / "samples.jsonl"
    _write_json(
        provisional,
        {
            "generated_at": "2026-05-02T00:00:00Z",
            "provisional": True,
            "p95_ms": 2300.0,
            "target_p95_ms": 2500.0,
        },
    )
    _write_json(
        preflight,
        {
            "preflight_ready": False,
            "summary": {"camera_count": 0, "microphone_count": 0},
        },
    )
    _write_jsonl(samples, [])

    snapshot = evaluate_transition(
        provisional_report_path=provisional,
        preflight_report_path=preflight,
        live_samples_path=samples,
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
    )

    assert snapshot.status == "BLOCKED_HARDWARE"
    assert snapshot.provisional_valid is True
    assert snapshot.hardware_ready is False


def test_transition_ready_for_live_capture_when_hardware_ready(tmp_path: Path) -> None:
    provisional = tmp_path / "provisional.json"
    preflight = tmp_path / "preflight.json"
    samples = tmp_path / "samples.jsonl"
    _write_json(
        provisional,
        {
            "generated_at": "2026-05-02T00:00:00Z",
            "provisional": True,
            "p95_ms": 2300.0,
            "target_p95_ms": 2500.0,
        },
    )
    _write_json(
        preflight,
        {
            "preflight_ready": True,
            "summary": {"camera_count": 1, "microphone_count": 1},
        },
    )
    _write_jsonl(
        samples,
        [
            {"captured_at": "2026-05-02T10:00:00Z", "total_ms": 2000.0},
            {"captured_at": "2026-05-02T10:00:01Z", "total_ms": 2050.0},
        ],
    )

    snapshot = evaluate_transition(
        provisional_report_path=provisional,
        preflight_report_path=preflight,
        live_samples_path=samples,
        target_live_sample_count=5,
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
    )

    assert snapshot.status == "READY_FOR_LIVE_CAPTURE"
    assert snapshot.provisional_valid is True
    assert snapshot.hardware_ready is True
    assert snapshot.live_sample_count == 2


def test_transition_blocks_when_provisional_is_stale(tmp_path: Path) -> None:
    provisional = tmp_path / "provisional.json"
    preflight = tmp_path / "preflight.json"
    samples = tmp_path / "samples.jsonl"
    _write_json(
        provisional,
        {
            "generated_at": "2026-03-01T00:00:00Z",
            "provisional": True,
            "p95_ms": 2300.0,
            "target_p95_ms": 2500.0,
        },
    )
    _write_json(
        preflight,
        {
            "preflight_ready": True,
            "summary": {"camera_count": 1, "microphone_count": 1},
        },
    )
    _write_jsonl(samples, [])

    snapshot = evaluate_transition(
        provisional_report_path=provisional,
        preflight_report_path=preflight,
        live_samples_path=samples,
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
        max_provisional_age_days=14,
    )

    assert snapshot.status == "BLOCKED_PROVISIONAL_MISSING"
    assert snapshot.provisional_valid is False
    assert any("stale" in n.lower() for n in snapshot.notes)


def test_transition_blocks_when_provisional_flag_false(tmp_path: Path) -> None:
    provisional = tmp_path / "provisional.json"
    preflight = tmp_path / "preflight.json"
    samples = tmp_path / "samples.jsonl"
    _write_json(
        provisional,
        {
            "generated_at": "2026-05-02T00:00:00Z",
            "provisional": False,
            "p95_ms": 2300.0,
            "target_p95_ms": 2500.0,
        },
    )
    _write_json(preflight, {"preflight_ready": True, "summary": {}})
    _write_jsonl(samples, [])

    snapshot = evaluate_transition(
        provisional_report_path=provisional,
        preflight_report_path=preflight,
        live_samples_path=samples,
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
    )

    assert snapshot.status == "BLOCKED_PROVISIONAL_MISSING"
    assert snapshot.provisional_valid is False


def test_live_sample_count_ignores_invalid_rows(tmp_path: Path) -> None:
    provisional = tmp_path / "provisional.json"
    preflight = tmp_path / "preflight.json"
    samples = tmp_path / "samples.jsonl"
    _write_json(
        provisional,
        {
            "generated_at": "2026-05-02T00:00:00Z",
            "provisional": True,
            "p95_ms": 2300.0,
            "target_p95_ms": 2500.0,
        },
    )
    _write_json(
        preflight,
        {
            "preflight_ready": True,
            "summary": {"camera_count": 1, "microphone_count": 1},
        },
    )
    _write_jsonl(
        samples,
        [
            {"captured_at": "2026-05-02T10:00:00Z", "total_ms": float("nan")},
            {"captured_at": "not-a-date", "total_ms": 2000.0},
            {"captured_at": "2026-05-02T10:00:02Z", "total_ms": 2100.0},
        ],
    )

    snapshot = evaluate_transition(
        provisional_report_path=provisional,
        preflight_report_path=preflight,
        live_samples_path=samples,
        target_live_sample_count=5,
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
    )

    assert snapshot.live_sample_count == 1
    assert snapshot.status == "READY_FOR_LIVE_CAPTURE"
