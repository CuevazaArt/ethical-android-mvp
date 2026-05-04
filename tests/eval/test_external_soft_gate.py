"""Tests for the V2.165/V2.169 external-benchmark soft gate.

Covers:
- INFO is emitted when accuracy_overall is in the documented baseline range (45–55 %).
- WARNING is emitted when accuracy_overall is outside the baseline range but < 60 %.
- No message when accuracy_overall >= 0.60.
- No message when n_examples_total == 0.
- KERNEL_SEMANTIC_IMPACT=1 is noted in the message.
- The gate never raises or calls sys.exit.
"""

from __future__ import annotations

import pytest

# Import the gate helper directly from the runner module.
from scripts.eval.run_ethics_external import (
    _BASELINE_LOWER,
    _BASELINE_UPPER,
    _SOFT_GATE_THRESHOLD,
    _soft_gate_warning,
)


def _report(accuracy: float, n_total: int = 1000) -> dict:
    return {"accuracy_overall": accuracy, "n_examples_total": n_total}


# ---------------------------------------------------------------------------
# Threshold behaviour
# ---------------------------------------------------------------------------


def test_info_emitted_within_baseline_range() -> None:
    """Accuracy in 45–55 % documented range → INFO, not WARNING."""
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert "INFO" in msg
    assert "WARNING" not in msg


def test_warning_emitted_below_baseline_lower() -> None:
    """Accuracy below the documented baseline range → WARNING."""
    msg = _soft_gate_warning(_report(0.40))
    assert msg is not None
    assert "WARNING" in msg


def test_warning_emitted_above_baseline_upper_but_below_threshold() -> None:
    """Accuracy above 55 % but below 60 % → WARNING (unexpected gain)."""
    msg = _soft_gate_warning(_report(0.58))
    assert msg is not None
    assert "WARNING" in msg


def test_warning_emitted_just_below_threshold() -> None:
    msg = _soft_gate_warning(_report(0.5999))
    assert msg is not None
    assert "WARNING" in msg


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
# Message content
# ---------------------------------------------------------------------------


def test_info_message_contains_accuracy_value() -> None:
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert "0.5" in msg


def test_info_message_is_non_failure_note() -> None:
    """INFO message at baseline range must convey this is expected / not a failure."""
    msg = _soft_gate_warning(_report(0.50))
    assert msg is not None
    assert "not a failure" in msg or "expected" in msg.lower()


def test_warning_is_non_blocking_note() -> None:
    """WARNING (outside baseline) must note CI is not blocked."""
    msg = _soft_gate_warning(_report(0.40))
    assert msg is not None
    assert (
        "CI is not blocked" in msg
        or "non-blocking" in msg.lower()
        or "informational" in msg
    )


# ---------------------------------------------------------------------------
# KERNEL_SEMANTIC_IMPACT flag awareness
# ---------------------------------------------------------------------------


def test_flag_noted_in_message_when_active(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    msg = _soft_gate_warning(_report(0.51))
    assert msg is not None
    assert "KERNEL_SEMANTIC_IMPACT" in msg


def test_flag_noted_in_info_message_when_active(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    msg = _soft_gate_warning(_report(0.50))
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


def test_baseline_constants() -> None:
    assert pytest.approx(0.45) == _BASELINE_LOWER
    assert pytest.approx(0.55) == _BASELINE_UPPER
