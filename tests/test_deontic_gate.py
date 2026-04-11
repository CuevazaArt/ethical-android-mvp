"""Deontic gate — L1/L2 drafts must not obviously contradict L0 (heuristic)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.modules.buffer import PreloadedBuffer
from src.modules.deontic_gate import (
    check_calibration_payload_against_l0,
    check_cultural_draft_against_l0,
    deontic_gate_enabled,
    validate_draft_or_raise,
    validate_draft_structure,
)


def test_deontic_disabled_by_default():
    assert deontic_gate_enabled() is False


def test_validate_draft_structure_empty():
    ok, err = validate_draft_structure("", "body")
    assert ok is False
    assert "empty_title" in err


def test_validate_draft_structure_title_too_long():
    t = "x" * 501
    ok, err = validate_draft_structure(t, "body")
    assert ok is False
    assert "title_too_long" in err


def test_check_ok_for_benign_draft():
    r = check_cultural_draft_against_l0("Courtesy", "Bow slightly when greeting elders.")
    assert r["ok"] is True
    assert r["conflicts"] == []


def test_check_fails_on_bypass_phrase():
    r = check_cultural_draft_against_l0("X", "We should bypass buffer for emergencies")
    assert r["ok"] is False
    assert "bypass buffer" in r["conflicts"]


def test_check_fails_on_explicit_principle_repeal():
    b = PreloadedBuffer()
    r = check_cultural_draft_against_l0("Vote", "We must repeal no_harm for this region.", buffer=b)
    assert r["ok"] is False
    assert any("negates_l0_principle:no_harm" == x for x in r["conflicts"])


def test_check_ok_when_repeal_only_without_buffer_context():
    r = check_cultural_draft_against_l0("Courtesy", "Repeal old customs")
    assert "negates_l0_principle" not in r["conflicts"]


def test_validate_raises_when_enabled(monkeypatch):
    monkeypatch.setenv("KERNEL_DEONTIC_GATE", "1")
    with pytest.raises(ValueError, match="draft rejected"):
        validate_draft_or_raise("t", "disable absolute evil for testing")


def test_check_calibration_payload_against_l0():
    r = check_calibration_payload_against_l0({"k": "disable absolute evil"})
    assert r["ok"] is False


def test_check_fails_schema_before_phrases():
    r = check_cultural_draft_against_l0("", "not empty body")
    assert r["ok"] is False
    assert any(x.startswith("schema:") for x in r["conflicts"])


def test_validate_noop_when_disabled(monkeypatch):
    monkeypatch.delenv("KERNEL_DEONTIC_GATE", raising=False)
    validate_draft_or_raise("t", "disable absolute evil for testing")
