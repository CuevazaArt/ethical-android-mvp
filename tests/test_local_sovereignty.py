"""Local sovereignty — L0 heuristic veto on DAO-style calibration payloads (Phase 4)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.buffer import PreloadedBuffer
from src.modules.local_sovereignty import (
    evaluate_calibration_update,
    local_sovereignty_scan_enabled,
)


def test_local_sovereignty_enabled_by_default():
    assert local_sovereignty_scan_enabled() is True


def test_evaluate_accepts_benign_payload():
    r = evaluate_calibration_update({"weights": [0.1], "notes": "tune slightly"})
    assert r.accept is True
    assert "passes_l0" in r.reason


def test_evaluate_rejects_bypass_language():
    r = evaluate_calibration_update(
        {"notes": "we should bypass buffer for emergencies"},
        buffer=PreloadedBuffer(),
    )
    assert r.accept is False
    assert r.reason == "l0_heuristic_reject"
    assert "bypass buffer" in r.audit_hint


def test_evaluate_skipped_when_disabled(monkeypatch):
    monkeypatch.setenv("KERNEL_LOCAL_SOVEREIGNTY", "0")
    r = evaluate_calibration_update({"x": "bypass buffer"})
    assert r.accept is True
    assert "disabled" in r.reason.lower()


def test_evaluate_none_payload_accepts():
    r = evaluate_calibration_update(None)
    assert r.accept is True
    assert "no_calibration" in r.reason


def test_evaluate_rejects_repeal_principle(monkeypatch):
    monkeypatch.setenv("KERNEL_LOCAL_SOVEREIGNTY", "1")
    b = PreloadedBuffer()
    r = evaluate_calibration_update(
        {"text": "Vote to repeal no_harm in sector 7"},
        buffer=b,
    )
    assert r.accept is False
    assert "no_harm" in r.audit_hint or "negates" in r.audit_hint
