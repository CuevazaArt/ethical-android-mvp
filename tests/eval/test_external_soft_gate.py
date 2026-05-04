"""Tests for the V2.165 external-benchmark soft gate.

Covers:
- WARNING is emitted when accuracy_overall < 0.60.
- No warning when accuracy_overall >= 0.60.
- No warning when n_examples_total == 0.
- KERNEL_SEMANTIC_IMPACT=1 is noted in the warning message.
- The gate never raises or calls sys.exit.
"""

from __future__ import annotations

import pytest

# Import the gate helper directly from the runner module.
from scripts.eval.run_ethics_external import (
    _SOFT_GATE_THRESHOLD,
    _soft_gate_warning,
)


def _report(accuracy: float, n_total: int = 1000) -> dict:
    return {"accuracy_overall": accuracy, "n_examples_total": n_total}


# ---------------------------------------------------------------------------
# Threshold behaviour
# ---------------------------------------------------------------------------


def test_warning_emitted_below_threshold() -> None:
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert "WARNING" in msg


def test_warning_emitted_just_below_threshold() -> None:
    msg = _soft_gate_warning(_report(0.5999))
    assert msg is not None


def test_no_warning_at_threshold() -> None:
    msg = _soft_gate_warning(_report(_SOFT_GATE_THRESHOLD))
    assert msg is None


def test_no_warning_above_threshold() -> None:
    msg = _soft_gate_warning(_report(0.62))
    assert msg is None


def test_no_warning_when_no_examples() -> None:
    msg = _soft_gate_warning(_report(0.50, n_total=0))
    assert msg is None


# ---------------------------------------------------------------------------
# Warning content
# ---------------------------------------------------------------------------


def test_warning_contains_accuracy_value() -> None:
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert "0.5" in msg


def test_warning_is_non_blocking_note() -> None:
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert (
        "CI is not blocked" in msg
        or "non-blocking" in msg.lower()
        or "informational" in msg
    )


# ---------------------------------------------------------------------------
# KERNEL_SEMANTIC_IMPACT flag awareness
# ---------------------------------------------------------------------------


def test_flag_noted_in_warning_when_active(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    msg = _soft_gate_warning(_report(0.51))
    assert msg is not None
    assert "KERNEL_SEMANTIC_IMPACT" in msg


def test_flag_not_noted_when_inactive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_SEMANTIC_IMPACT", raising=False)
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert "KERNEL_SEMANTIC_IMPACT" not in msg


def test_flag_not_noted_when_wrong_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "0")
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert "KERNEL_SEMANTIC_IMPACT" not in msg


# ---------------------------------------------------------------------------
# Gate never raises
# ---------------------------------------------------------------------------


def test_gate_does_not_raise_on_empty_report() -> None:
    result = _soft_gate_warning({})
    # Should return None, not raise.
    assert result is None


def test_gate_does_not_raise_on_high_accuracy() -> None:
    result = _soft_gate_warning(_report(1.0))
    assert result is None


def test_soft_gate_threshold_value() -> None:
    assert pytest.approx(0.60) == _SOFT_GATE_THRESHOLD
