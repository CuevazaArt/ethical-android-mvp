"""V2.127 (B1): both G2 paths (live audio and text_mediated) must coexist.

The text_mediated path is the explicit, transparent way to declare G2 PASS
when audio capture hardware is unavailable. The hardware path remains the
ground truth and is preferred whenever it has data.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.eval.desktop_gate_runner import (
    build_gate_snapshot,
    evaluate_latency_gate,
)
from scripts.eval.g2_transition_guard import evaluate_transition


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    payload = "\n".join(json.dumps(row) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def _seed_g1(evidence_dir: Path, *, now: datetime, days: int = 14) -> None:
    rows: list[dict[str, object]] = []
    for offset in range(days):
        date = (
            now.replace(hour=0, minute=0, second=0, microsecond=0).toordinal() - offset
        )
        d = datetime.fromordinal(date)
        rows.append(
            {
                "date": f"{d.strftime('%Y-%m-%d')}T00:00:00Z",
                "status": "pass",
            }
        )
    _write_jsonl(evidence_dir / "DESKTOP_STABILITY_LEDGER.jsonl", rows)


def test_evaluate_latency_gate_text_mediated_requires_min_samples(
    tmp_path: Path,
) -> None:
    samples = tmp_path / "samples.jsonl"
    rows = [
        {"captured_at": f"2026-05-02T10:00:{i:02d}Z", "total_ms": 1000.0 + i}
        for i in range(15)
    ]
    _write_jsonl(samples, rows)

    result = evaluate_latency_gate(
        samples,
        target_p95_ms=2500.0,
        mode="text_mediated",
        min_sample_count=20,
    )
    assert result.passed is False, "fewer than min samples must not PASS"
    assert result.details["mode"] == "text_mediated"
    assert result.details["audio_capture_path"] == "WONTFIX_UNTIL_HARDWARE"


def test_evaluate_latency_gate_text_mediated_passes_with_enough_samples(
    tmp_path: Path,
) -> None:
    samples = tmp_path / "samples.jsonl"
    rows = [
        {"captured_at": f"2026-05-02T10:00:{i:02d}Z", "total_ms": 800.0 + i * 5}
        for i in range(25)
    ]
    _write_jsonl(samples, rows)

    result = evaluate_latency_gate(
        samples,
        target_p95_ms=2500.0,
        mode="text_mediated",
        min_sample_count=20,
    )
    assert result.passed is True
    assert result.details["sample_count"] == 25
    assert result.details["mode"] == "text_mediated"
    assert "[text_mediated]" in result.summary


def test_evaluate_latency_gate_live_mode_unchanged_summary(tmp_path: Path) -> None:
    samples = tmp_path / "samples.jsonl"
    _write_jsonl(
        samples,
        [
            {"captured_at": "2026-05-02T10:00:00Z", "total_ms": 1900.0},
            {"captured_at": "2026-05-02T10:00:01Z", "total_ms": 2100.0},
        ],
    )

    result = evaluate_latency_gate(samples, target_p95_ms=2500.0)
    assert result.passed is True
    assert result.details["mode"] == "live"
    assert "[text_mediated]" not in result.summary


def test_build_gate_snapshot_prefers_text_mediated_pass(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    now = datetime(2026, 5, 2, 12, 0, tzinfo=UTC)

    _seed_g1(evidence_dir, now=now)

    text_rows = [
        {
            "captured_at": f"2026-05-02T10:00:{i:02d}Z",
            "total_ms": 1200.0 + i,
            "source": "text_mediated",
        }
        for i in range(22)
    ]
    _write_jsonl(evidence_dir / "G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl", text_rows)

    _write_json(
        evidence_dir / "G2_PROVISIONAL_LATENCY_REPORT.json",
        {
            "generated_at": "2026-05-02T00:00:00Z",
            "provisional": True,
            "p95_ms": 2395.0,
            "target_p95_ms": 2500.0,
            "source": "synthetic_fixture",
            "sample_count": 50,
        },
    )

    snapshot = build_gate_snapshot(evidence_dir=evidence_dir, now=now)
    g2 = snapshot["gates"]["G2"]
    assert g2["status"] == "pass"
    assert g2["mode"] == "text_mediated"
    assert g2["audio_capture_path"] == "WONTFIX_UNTIL_HARDWARE"
    assert "[text_mediated]" in g2["summary"]


def test_evaluate_transition_recognizes_text_mediated_path(tmp_path: Path) -> None:
    provisional = tmp_path / "provisional.json"
    preflight = tmp_path / "preflight.json"
    live_samples = tmp_path / "samples.jsonl"
    text_samples = tmp_path / "text_samples.jsonl"

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
    _write_jsonl(live_samples, [])
    _write_jsonl(
        text_samples,
        [
            {"captured_at": f"2026-05-02T10:00:{i:02d}Z", "total_ms": 1000.0 + i}
            for i in range(20)
        ],
    )

    snapshot = evaluate_transition(
        provisional_report_path=provisional,
        preflight_report_path=preflight,
        live_samples_path=live_samples,
        text_mediated_samples_path=text_samples,
        target_live_sample_count=20,
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
    )

    assert snapshot.status == "READY_FOR_LIVE_EVALUATION"
    assert snapshot.mode == "text_mediated"
    assert snapshot.text_mediated_sample_count == 20
    assert any("text_mediated" in n for n in snapshot.notes)
