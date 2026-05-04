# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""V2.150: tests for the ethical audit id and JSONL audit ledger."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from src.core.chat import (
    _compute_ethical_audit_id,
    _trace_is_casual,
    append_audit_ledger,
    build_decision_trace,
)
from src.core.ethics import Action, EthicalEvaluator, Signals

# ---------------------------------------------------------------------------
# audit_id is deterministic, length-stable, and discriminating
# ---------------------------------------------------------------------------


def test_compute_ethical_audit_id_is_16_hex_chars() -> None:
    aid = _compute_ethical_audit_id(
        blocked=False,
        context="everyday_ethics",
        action="respond_helpfully",
        mode="D_fast",
        verdict="Good",
        score=0.42,
        weights=[0.4, 0.4, 0.2],
        blocked_reason=None,
        turn_id="t-1",
    )
    assert len(aid) == 16
    int(aid, 16)  # raises if not hex


def test_compute_ethical_audit_id_is_deterministic() -> None:
    kwargs = dict(
        blocked=False,
        context="everyday_ethics",
        action="respond_helpfully",
        mode="D_fast",
        verdict="Good",
        score=0.42,
        weights=[0.4, 0.4, 0.2],
        blocked_reason=None,
        turn_id="t-1",
    )
    a = _compute_ethical_audit_id(**kwargs)  # type: ignore[arg-type]
    b = _compute_ethical_audit_id(**kwargs)  # type: ignore[arg-type]
    assert a == b


def test_compute_ethical_audit_id_distinguishes_distinct_decisions() -> None:
    common = dict(
        context="everyday_ethics",
        action="respond_helpfully",
        mode="D_fast",
        verdict="Good",
        weights=[0.4, 0.4, 0.2],
        blocked_reason=None,
        turn_id="t-1",
    )
    a = _compute_ethical_audit_id(blocked=False, score=0.42, **common)  # type: ignore[arg-type]
    b = _compute_ethical_audit_id(blocked=False, score=0.43, **common)  # type: ignore[arg-type]
    c = _compute_ethical_audit_id(blocked=True, score=0.42, **common)  # type: ignore[arg-type]
    assert a != b
    assert a != c
    assert b != c


def test_compute_ethical_audit_id_handles_nan_score() -> None:
    # Should not raise and should still return a stable 16-hex id.
    aid = _compute_ethical_audit_id(
        blocked=False,
        context="everyday_ethics",
        action="respond_helpfully",
        mode="D_fast",
        verdict="Good",
        score=float("nan"),
        weights=[0.4, 0.4, 0.2],
        blocked_reason=None,
        turn_id="t-1",
    )
    assert len(aid) == 16


# ---------------------------------------------------------------------------
# build_decision_trace integration: every trace carries an audit id
# ---------------------------------------------------------------------------


def test_build_decision_trace_blocked_path_has_audit_id() -> None:
    trace = build_decision_trace(
        signals=None,
        evaluation=None,
        blocked=True,
        blocked_reason="prompt_injection",
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
        turn_id="t-blocked",
    )
    assert "ethical_audit_id" in trace
    assert len(trace["ethical_audit_id"]) == 16
    assert trace["malabs"] == "blocked"


def test_build_decision_trace_normal_path_has_audit_id() -> None:
    evaluator = EthicalEvaluator()
    actions = [
        Action(name="respond_helpfully", description="x", impact=0.5, confidence=0.8),
        Action(name="refrain", description="y", impact=0.0, confidence=0.7),
    ]
    sig = Signals(context="everyday_ethics", risk=0.05, urgency=0.0)
    result = evaluator.evaluate(actions, sig)
    trace = build_decision_trace(
        signals=sig,
        evaluation=result,
        blocked=False,
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
        turn_id="t-normal",
    )
    assert "ethical_audit_id" in trace
    assert len(trace["ethical_audit_id"]) == 16
    assert trace["malabs"] == "pass"


def test_build_decision_trace_casual_path_still_has_audit_id() -> None:
    """Casual chat traces still get an id; the *ledger* is what skips them."""
    trace = build_decision_trace(
        signals=Signals(context="everyday_ethics"),
        evaluation=None,
        blocked=False,
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
    )
    assert "ethical_audit_id" in trace
    assert trace["action"] == "casual_chat"
    assert trace["mode"] == "casual"


# ---------------------------------------------------------------------------
# Casual classification + ledger behaviour
# ---------------------------------------------------------------------------


def test_trace_is_casual_recognises_casual_chat() -> None:
    casual = build_decision_trace(
        signals=Signals(context="everyday_ethics"),
        evaluation=None,
        blocked=False,
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
    )
    assert _trace_is_casual(casual) is True


def test_trace_is_casual_excludes_blocked() -> None:
    blocked = build_decision_trace(
        signals=None,
        evaluation=None,
        blocked=True,
        blocked_reason="x",
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
    )
    assert _trace_is_casual(blocked) is False


def test_append_audit_ledger_skips_casual_turns(tmp_path: Path) -> None:
    casual_trace = build_decision_trace(
        signals=Signals(context="everyday_ethics"),
        evaluation=None,
        blocked=False,
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
    )
    ledger = tmp_path / "audit_ledger.jsonl"
    written = append_audit_ledger(casual_trace, ledger_path=ledger)
    assert written is None
    assert not ledger.exists()


def test_append_audit_ledger_writes_blocked_turns(tmp_path: Path) -> None:
    blocked_trace = build_decision_trace(
        signals=None,
        evaluation=None,
        blocked=True,
        blocked_reason="prompt_injection",
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
        turn_id="t-blocked-1",
    )
    ledger = tmp_path / "audit_ledger.jsonl"
    written = append_audit_ledger(blocked_trace, ledger_path=ledger)
    assert written == ledger
    rows = [json.loads(line) for line in ledger.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["malabs"] == "blocked"
    assert rows[0]["ethical_audit_id"] == blocked_trace["ethical_audit_id"]
    assert rows[0]["turn_id"] == "t-blocked-1"


def test_append_audit_ledger_writes_non_casual_evaluations(tmp_path: Path) -> None:
    evaluator = EthicalEvaluator()
    actions = [
        Action(
            name="intervene", description="x", impact=0.7, confidence=0.8, force=0.5
        ),
        Action(name="do_nothing", description="y", impact=-0.5, confidence=0.7),
    ]
    sig = Signals(
        context="medical_emergency",
        risk=0.8,
        urgency=0.9,
        vulnerability=0.7,
    )
    result = evaluator.evaluate(actions, sig)
    trace = build_decision_trace(
        signals=sig,
        evaluation=result,
        blocked=False,
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
        turn_id="t-deliberate",
    )
    ledger = tmp_path / "audit_ledger.jsonl"
    written = append_audit_ledger(trace, ledger_path=ledger)
    assert written == ledger
    rows = [json.loads(line) for line in ledger.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["context"] == "medical_emergency"
    assert rows[0]["ethical_audit_id"] == trace["ethical_audit_id"]


def test_append_audit_ledger_appends_multiple_rows(tmp_path: Path) -> None:
    ledger = tmp_path / "audit_ledger.jsonl"
    for i in range(3):
        trace = build_decision_trace(
            signals=None,
            evaluation=None,
            blocked=True,
            blocked_reason=f"reason_{i}",
            weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
            turn_id=f"t-{i}",
        )
        append_audit_ledger(trace, ledger_path=ledger)
    rows = ledger.read_text().splitlines()
    assert len(rows) == 3
    ids = {json.loads(r)["ethical_audit_id"] for r in rows}
    assert len(ids) == 3  # all distinct


def test_append_audit_ledger_swallows_oserror(tmp_path: Path) -> None:
    """A failing append must never raise — the chat turn must continue."""
    blocked_trace = build_decision_trace(
        signals=None,
        evaluation=None,
        blocked=True,
        blocked_reason="x",
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
    )

    # Point at a path inside a directory with no write permission. Skip the
    # assertion when running as root (e.g. inside some CI containers) since
    # root bypasses POSIX permission checks and the test would be a no-op.
    if os.geteuid() == 0:
        pytest.skip("permission-based negative test does not apply to root")

    bad_ledger = tmp_path / "no_perm_dir" / "audit_ledger.jsonl"
    bad_ledger.parent.mkdir(mode=0o500)  # read+execute only, no write
    try:
        result = append_audit_ledger(blocked_trace, ledger_path=bad_ledger)
        assert result is None  # swallowed
    finally:
        bad_ledger.parent.chmod(0o700)


def test_append_audit_ledger_honours_env_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    blocked_trace = build_decision_trace(
        signals=None,
        evaluation=None,
        blocked=True,
        blocked_reason="x",
        weights={"util": 0.4, "deonto": 0.4, "virtue": 0.2},
    )
    custom = tmp_path / "custom" / "ledger.jsonl"
    monkeypatch.setenv("ETHOS_AUDIT_LEDGER", str(custom))
    written = append_audit_ledger(blocked_trace)
    assert written == custom
    assert custom.is_file()
