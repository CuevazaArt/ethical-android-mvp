"""Feedback ledger and Psi Sleep mixture application (proposal B1)."""

from __future__ import annotations

import numpy as np
import pytest
from src.kernel import EthicalKernel
from src.modules.feedback_calibration_ledger import (
    FeedbackCalibrationLedger,
    apply_psi_sleep_feedback_to_engine,
    compute_target_weights,
    normalize_feedback_label,
)


def test_normalize_feedback_label_aliases():
    assert normalize_feedback_label("approve") == "approve"
    assert normalize_feedback_label("HARM") == "harm_report"
    assert normalize_feedback_label("nope") is None


def test_compute_target_weights_none_when_empty():
    assert compute_target_weights(FeedbackCalibrationLedger().copy_counts()) is None


def test_apply_psi_sleep_skips_without_flag(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_PSI_SLEEP_UPDATE_MIXTURE", raising=False)
    k = EthicalKernel(variability=False)
    k.feedback_ledger.record("D_fast", "approve")
    k.feedback_ledger.record("D_fast", "harm_report")
    line = apply_psi_sleep_feedback_to_engine(
        k.bayesian,
        k.feedback_ledger,
        genome_weights=k._bayesian_genome_weights,
        max_drift=0.15,
    )
    assert line == ""
    assert k.feedback_ledger.total() == 2


def test_apply_psi_sleep_updates_and_clears(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PSI_SLEEP_UPDATE_MIXTURE", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_CALIBRATION_MIN_SAMPLES", "2")
    monkeypatch.setenv("KERNEL_PSI_SLEEP_FEEDBACK_BLEND", "0.25")
    k = EthicalKernel(variability=False)
    before = k.bayesian.hypothesis_weights.copy()
    k.feedback_ledger.record("D_fast", "approve")
    k.feedback_ledger.record("D_fast", "approve")
    line = apply_psi_sleep_feedback_to_engine(
        k.bayesian,
        k.feedback_ledger,
        genome_weights=k._bayesian_genome_weights,
        max_drift=0.15,
    )
    assert "applied" in line.lower()
    assert k.feedback_ledger.total() == 0
    assert not np.allclose(k.bayesian.hypothesis_weights, before)


def test_execute_sleep_appends_feedback_line(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_FEEDBACK_CALIBRATION", "1")
    monkeypatch.setenv("KERNEL_PSI_SLEEP_UPDATE_MIXTURE", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_CALIBRATION_MIN_SAMPLES", "1")
    monkeypatch.setenv("KERNEL_PSI_SLEEP_FEEDBACK_BLEND", "0.2")
    k = EthicalKernel(variability=False)
    k._snapshot_feedback_anchor("D_fast")
    assert k.record_operator_feedback("harm_report")
    out = k.execute_sleep()
    assert "Feedback mixture" in out


def test_record_operator_feedback_requires_flag(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_FEEDBACK_CALIBRATION", raising=False)
    k = EthicalKernel(variability=False)
    k._snapshot_feedback_anchor("D_fast")
    assert not k.record_operator_feedback("approve")


def test_genome_cap_skips_apply(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PSI_SLEEP_UPDATE_MIXTURE", "1")
    monkeypatch.setenv("KERNEL_FEEDBACK_CALIBRATION_MIN_SAMPLES", "1")
    monkeypatch.setenv("KERNEL_PSI_SLEEP_FEEDBACK_BLEND", "1.0")
    k = EthicalKernel(variability=False)
    k.feedback_ledger.record("D_fast", "harm_report")
    line = apply_psi_sleep_feedback_to_engine(
        k.bayesian,
        k.feedback_ledger,
        genome_weights=(0.4, 0.35, 0.25),
        max_drift=0.01,
    )
    assert "skipped" in line.lower()
    assert k.feedback_ledger.total() == 1
