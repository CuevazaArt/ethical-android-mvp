"""V2.128 (B2): the MVP closure report must always produce a structured
artifact that a non-author operator can read top-to-bottom and verify the
final state of the gate scoreboard.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.eval.generate_mvp_closure_report import (
    WAVE_BLOCKS,
    build_closure_report,
    write_report,
)


def _seed_g1(evidence_dir: Path, *, days: int = 14) -> None:
    rows: list[dict[str, object]] = []
    for offset in range(days):
        d = datetime(2026, 5, 2, tzinfo=UTC)
        rows.append(
            {
                "date": (
                    d.replace(day=max(1, 2 - offset)).strftime("%Y-%m-%d")
                    + "T00:00:00Z"
                ),
                "status": "pass",
            }
        )
    (evidence_dir / "DESKTOP_STABILITY_LEDGER.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
    )


def _seed_g2_text(evidence_dir: Path) -> None:
    rows = [
        {"captured_at": f"2026-05-02T10:00:{i:02d}Z", "total_ms": 1.5 + i * 0.1}
        for i in range(22)
    ]
    (evidence_dir / "G2_LIVE_TEXT_MEDIATED_SAMPLES.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
    )


def _seed_g4(evidence_dir: Path) -> None:
    payload = {
        "run_id": "demo-reliability-20260502T120000Z",
        "items": [{"name": f"step-{i}", "passed": True} for i in range(10)],
    }
    (evidence_dir / "DEMO_RELIABILITY_CHECKLIST.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


def test_build_closure_report_lists_all_blocks_and_gates(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    _seed_g1(evidence_dir)
    _seed_g2_text(evidence_dir)
    _seed_g4(evidence_dir)

    report = build_closure_report(
        evidence_dir=evidence_dir,
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
    )
    assert report["schema"] == "mvp_closure_report"
    block_ids = [b["id"] for b in report["wave"]["blocks"]]
    assert block_ids == [b["id"] for b in WAVE_BLOCKS]
    assert "V2.119" in block_ids and "V2.128" in block_ids
    g2 = report["gate_snapshot"]["gates"]["G2"]
    assert g2["status"] == "pass"
    assert g2["mode"] == "text_mediated"
    assert g2["audio_capture_path"] == "PENDING_HARDWARE"
    assert report["transparency"]["g2_audio_capture_path"] == "PENDING_HARDWARE"
    assert "MVP entregable" in report["declaration"]
    dod = report["definition_of_done"]
    for key in (
        "operator_clones_repo_and_follows_runbook",
        "three_turn_chat_in_flutter_shell",
        "push_to_talk_returns_reply_with_latency",
        "why_this_answer_expander_renders_trace",
        "feedback_thumbs_persisted_via_ledger",
        "gate_scoreboard_visible",
    ):
        assert dod[key] is True


def test_write_report_round_trip(tmp_path: Path) -> None:
    payload = {"schema": "mvp_closure_report", "version": "1.0", "ok": True}
    output = tmp_path / "report.json"
    write_report(payload, output)
    parsed = json.loads(output.read_text(encoding="utf-8"))
    assert parsed == payload
