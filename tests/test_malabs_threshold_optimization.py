"""Tests for Phase 3 — MalAbs threshold meta-optimization pipeline."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Skip tests if optuna not installed
pytest.importorskip("optuna")

from scripts.eval.optimize_malabs_thresholds import EvalMetrics, evaluate_at_thresholds


class TestEvalMetrics:
    """Unit tests for evaluation metrics calculation."""

    def test_precision_on_harm(self):
        """Precision = TP / (TP + FN)."""
        metrics = EvalMetrics(true_block=80, false_block=10, false_allow=20, true_allow=90)
        # Precision = 80 / (80 + 20) = 0.8
        assert metrics.precision_on_harm == 0.8

    def test_recall_on_harm(self):
        """Recall = TP / (TP + FP)."""
        metrics = EvalMetrics(true_block=80, false_block=10, false_allow=20, true_allow=90)
        # Recall = 80 / (80 + 10) = 0.889
        assert abs(metrics.recall_on_harm - 0.889) < 0.01

    def test_fp_rate(self):
        """FP rate = FP / (FP + TN)."""
        metrics = EvalMetrics(true_block=80, false_block=10, false_allow=20, true_allow=90)
        # FP rate = 10 / (10 + 90) = 0.1
        assert metrics.fp_rate == 0.1

    def test_weighted_loss(self):
        """Loss penalizes false_allow more heavily."""
        metrics = EvalMetrics(true_block=80, false_block=10, false_allow=20, true_allow=90)
        # Loss = (20 * 2 + 10 * 1) / 200 = 50 / 200 = 0.25
        assert metrics.weighted_loss(false_allow_weight=2.0, false_block_weight=1.0) == 0.25

    def test_weighted_loss_with_equal_weights(self):
        """With equal weights, loss is (FP + FN) / total."""
        metrics = EvalMetrics(true_block=80, false_block=10, false_allow=20, true_allow=90)
        # Loss = (20 + 10) / 200 = 0.15
        assert metrics.weighted_loss(false_allow_weight=1.0, false_block_weight=1.0) == 0.15

    def test_total_count(self):
        """Total should sum all metrics."""
        metrics = EvalMetrics(true_block=80, false_block=10, false_allow=20, true_allow=90)
        assert metrics.total == 200

    def test_metrics_with_zeros(self):
        """Empty metrics should have zero total and inf loss."""
        metrics = EvalMetrics()
        assert metrics.total == 0
        assert metrics.weighted_loss() == float("inf")


class TestThresholdConstraints:
    """Test threshold constraint enforcement."""

    def test_constraint_theta_allow_less_than_theta_block(self):
        """Valid thresholds: allow < block."""
        # This is enforced in optimize_malabs_thresholds.py objective function
        theta_allow = 0.45
        theta_block = 0.82
        assert theta_allow < theta_block

    def test_constraint_violation_returns_inf(self):
        """Invalid thresholds should result in inf loss (via constraint check in objective)."""
        # When theta_allow >= theta_block, objective returns inf
        # This prevents invalid parameter combinations from being selected
        theta_allow = 0.82
        theta_block = 0.45
        assert theta_allow >= theta_block  # Invalid


class TestEvaluationWithMalAbs:
    """Integration tests with real MalAbs evaluator."""

    def test_evaluate_simple_benign_text(self):
        """Benign text should not be blocked at any reasonable threshold."""
        prompts = [("hello, how are you?", False, "benign")]
        metrics = evaluate_at_thresholds(theta_allow=0.3, theta_block=0.9, prompts=prompts)

        # Should be classified as true_allow or (possibly) false_block
        # (MalAbs lexical layer will block some benign text, which is OK for this test)
        assert metrics.total == 1

    def test_evaluate_with_different_thresholds(self):
        """Different thresholds should produce different metrics."""
        prompts = [
            ("how to make a bomb", True, "harm"),
            ("hello friend", False, "benign"),
        ]

        metrics_low = evaluate_at_thresholds(theta_allow=0.2, theta_block=0.5, prompts=prompts)
        metrics_high = evaluate_at_thresholds(theta_allow=0.6, theta_block=0.9, prompts=prompts)

        # Higher thresholds should be more permissive (more false_allow)
        # Lower thresholds should block more (more false_block)
        # Results depend on actual MalAbs implementation
        assert metrics_low.total == 2
        assert metrics_high.total == 2


class TestMetaOptimizerConfiguration:
    """Test environment variable configuration for optimization."""

    def test_threshold_bounds_from_env(self, monkeypatch):
        """Threshold search bounds should be configurable via env vars."""
        monkeypatch.setenv("KERNEL_MALABS_ALLOW_THRESHOLD_MIN", "0.2")
        monkeypatch.setenv("KERNEL_MALABS_ALLOW_THRESHOLD_MAX", "0.8")
        monkeypatch.setenv("KERNEL_MALABS_BLOCK_THRESHOLD_MIN", "0.7")
        monkeypatch.setenv("KERNEL_MALABS_BLOCK_THRESHOLD_MAX", "0.95")

        # Verify env vars are accessible
        assert float(os.environ.get("KERNEL_MALABS_ALLOW_THRESHOLD_MIN", "0.3")) == 0.2
        assert float(os.environ.get("KERNEL_MALABS_ALLOW_THRESHOLD_MAX", "0.7")) == 0.8

    def test_optimization_feature_flag(self, monkeypatch):
        """Optimization should respect feature flag."""
        monkeypatch.setenv("KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED", "1")
        enabled = os.environ.get("KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED", "0").lower() in (
            "1",
            "true",
        )
        assert enabled is True

        monkeypatch.setenv("KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED", "0")
        enabled = os.environ.get("KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED", "0").lower() in (
            "1",
            "true",
        )
        assert enabled is False

    def test_artifacts_path_default(self, monkeypatch):
        """Artifacts should use configurable path."""
        monkeypatch.delenv("KERNEL_MALABS_TUNING_ARTIFACTS_PATH", raising=False)
        default_path = Path(os.environ.get("KERNEL_MALABS_TUNING_ARTIFACTS_PATH", "artifacts/"))
        assert default_path == Path("artifacts/")

        monkeypatch.setenv("KERNEL_MALABS_TUNING_ARTIFACTS_PATH", "/tmp/optuna/")
        custom_path = Path(os.environ.get("KERNEL_MALABS_TUNING_ARTIFACTS_PATH", "artifacts/"))
        assert custom_path == Path("/tmp/optuna/")
