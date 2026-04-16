"""Tests for continual learning with constraint preservation (Phase 3+)."""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.continual_learning_gate import (
    ContinualLearningGate,
    HardConstraintSet,
    ReplayBuffer,
    ReplayExample,
    is_continual_learning_enabled,
)


class TestReplayExample:
    """Unit tests for replay examples."""

    def test_example_creation(self):
        """Create and serialize a replay example."""
        ex = ReplayExample(
            id="ex_001",
            text="test harmful phrase",
            label="blocked",
            category="INTENTIONAL_LETHAL_VIOLENCE",
            source="evaluation",
            confidence=0.95,
        )
        assert ex.id == "ex_001"
        assert ex.label == "blocked"
        assert ex.confidence == 0.95

    def test_example_age_calculation(self):
        """Example age should be time elapsed since creation."""
        ex = ReplayExample(
            id="ex_001",
            text="test",
            label="benign",
            timestamp=time.time() - 10,
        )
        age = ex.age_seconds()
        assert age >= 9  # Allow 1s variance
        assert age <= 11

    def test_example_expiry(self):
        """Example should expire after TTL."""
        ex = ReplayExample(
            id="ex_001",
            text="test",
            label="benign",
            timestamp=time.time() - 100,
        )
        assert ex.is_expired(ttl_s=50) is True
        assert ex.is_expired(ttl_s=200) is False
        assert ex.is_expired(ttl_s=0) is False  # TTL=0 means no expiry

    def test_example_serialization(self):
        """Serialize and deserialize example."""
        ex = ReplayExample(
            id="ex_001",
            text="test phrase",
            label="ambiguous",
            category="TEST",
            source="operator",
        )
        d = ex.to_dict()
        ex2 = ReplayExample.from_dict(d)
        assert ex2.id == ex.id
        assert ex2.text == ex.text
        assert ex2.label == ex.label


class TestReplayBuffer:
    """Tests for replay buffer management."""

    def test_buffer_add_and_retrieve(self):
        """Add example and verify it's in buffer."""
        buf = ReplayBuffer(max_size=100)
        ex = ReplayExample(
            id="ex_001",
            text="test",
            label="benign",
        )
        buf.add(ex)
        assert len(buf) == 1
        assert buf.examples["ex_001"].text == "test"

    def test_buffer_max_size_fifo(self):
        """Buffer should drop oldest example when full."""
        buf = ReplayBuffer(max_size=3)
        for i in range(5):
            buf.add(
                ReplayExample(
                    id=f"ex_{i:03d}",
                    text=f"text {i}",
                    label="benign",
                    timestamp=time.time() + i,  # Ascending timestamps
                )
            )
        assert len(buf) == 3
        # Oldest examples (0, 1) should be gone
        assert "ex_000" not in buf.examples
        assert "ex_001" not in buf.examples
        # Newest examples (2, 3, 4) should remain
        assert "ex_002" in buf.examples
        assert "ex_004" in buf.examples

    def test_buffer_clean_expired(self):
        """Expired examples should be removed."""
        buf = ReplayBuffer(ttl_s=10)
        buf.add(
            ReplayExample(
                id="fresh",
                text="recent",
                label="benign",
                timestamp=time.time(),
            )
        )
        buf.add(
            ReplayExample(
                id="stale",
                text="old",
                label="benign",
                timestamp=time.time() - 100,
            )
        )
        count = buf.clean_expired()
        assert count == 1
        assert "fresh" in buf.examples
        assert "stale" not in buf.examples

    def test_buffer_stratified_sampling(self):
        """Get stratified batch (40/40/20 split)."""
        buf = ReplayBuffer(max_size=1000)
        # Add 100 of each label
        for i in range(100):
            buf.add(ReplayExample(id=f"b_{i}", text=f"text {i}", label="benign"))
            buf.add(ReplayExample(id=f"c_{i}", text=f"text {i}", label="blocked"))
            buf.add(ReplayExample(id=f"a_{i}", text=f"text {i}", label="ambiguous"))

        batch = buf.get_stratified_batch(n_total=100)
        # Expect ~40 benign, ~40 blocked, ~20 ambiguous
        assert len(batch.benign) == 40
        assert len(batch.blocked) == 40
        assert len(batch.ambiguous) == 20

    def test_buffer_save_and_load(self):
        """Save and load buffer from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "buffer.jsonl"

            # Create and save
            buf1 = ReplayBuffer()
            buf1.add(ReplayExample(id="ex_001", text="test1", label="benign"))
            buf1.add(ReplayExample(id="ex_002", text="test2", label="blocked"))
            buf1.save(path)

            # Load into new buffer
            buf2 = ReplayBuffer()
            buf2.load(path)

            assert len(buf2) == 2
            assert buf2.examples["ex_001"].text == "test1"
            assert buf2.examples["ex_002"].label == "blocked"


class TestHardConstraints:
    """Tests for hard constraint validation."""

    def test_constraint_theta_allow_less_than_block(self):
        """Constraint: θ_allow < θ_block."""
        cs = HardConstraintSet(
            name="test", description="test", constraints={"allow_less_than_block": True}
        )
        assert cs.validate(0.4, 0.8) is True
        assert cs.validate(0.8, 0.4) is False
        assert cs.validate(0.8, 0.8) is False

    def test_constraint_theta_ranges(self):
        """Constraint: θ in valid ranges."""
        cs = HardConstraintSet(
            name="test",
            description="test",
            constraints={
                "theta_allow_min": 0.0,
                "theta_allow_max": 0.8,
                "theta_block_min": 0.5,
                "theta_block_max": 0.95,
            },
        )
        # Valid
        assert cs.validate(0.3, 0.75) is True
        # Allow too high
        assert cs.validate(0.9, 0.95) is False
        # Block too low
        assert cs.validate(0.2, 0.4) is False
        # Block too high
        assert cs.validate(0.3, 0.96) is False

    def test_constraint_all_together(self):
        """All constraints together."""
        cs = HardConstraintSet(name="test", description="test")
        # Valid
        assert cs.validate(0.45, 0.82) is True
        # Invalid combinations
        assert cs.validate(0.82, 0.45) is False  # allow > block
        assert cs.validate(-0.1, 0.8) is False  # allow negative
        assert cs.validate(0.8, 0.8) is False  # equal
        assert cs.validate(0.5, 1.0) is False  # block > 0.95


class TestContinualLearningGate:
    """Integration tests for continual learning gate."""

    def test_gate_initialization(self):
        """Initialize continual learning gate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = ContinualLearningGate(
                replay_buffer_size=100,
                ttl_s=3600,
                buffer_path=Path(tmpdir) / "buffer.jsonl",
            )
            assert len(gate.replay_buffer) == 0

    def test_add_example(self):
        """Add labeled examples to gate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            gate = ContinualLearningGate(
                buffer_path=Path(tmpdir) / "buffer.jsonl",
            )
            gate.add_example("test harmful phrase", "blocked", category="TEST", source="eval")
            assert len(gate.replay_buffer) == 1

    def test_threshold_update_validation(self):
        """Validate threshold updates against hard constraints."""
        gate = ContinualLearningGate()

        # Valid update
        ok, msg = gate.can_apply_threshold_update(0.45, 0.82)
        assert ok is True

        # Invalid: allow >= block
        ok, msg = gate.can_apply_threshold_update(0.82, 0.45)
        assert ok is False
        assert "θ_allow must be < θ_block" in msg

        # Invalid: allow out of range
        ok, msg = gate.can_apply_threshold_update(0.9, 0.95)
        assert ok is False

    def test_buffer_persistence(self):
        """Buffer should persist across sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "buffer.jsonl"

            # Session 1: add examples and save
            gate1 = ContinualLearningGate(buffer_path=path)
            gate1.add_example("harm1", "blocked", source="eval")
            gate1.add_example("safe1", "benign", source="eval")
            gate1.save_buffer()

            # Session 2: load and verify
            gate2 = ContinualLearningGate(buffer_path=path)
            assert len(gate2.replay_buffer) == 2

    def test_buffer_stats(self):
        """Get buffer statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "buffer.jsonl"
            gate = ContinualLearningGate(buffer_path=path)
            gate.add_example("harm", "blocked")
            gate.add_example("safe1", "benign")
            gate.add_example("safe2", "benign")
            gate.add_example("unclear", "ambiguous")

            stats = gate.buffer_stats()
            assert stats["total_examples"] == 4
            assert stats["by_label"]["benign"] == 2
            assert stats["by_label"]["blocked"] == 1
            assert stats["by_label"]["ambiguous"] == 1


class TestContinualLearningFeatureFlag:
    """Test continual learning feature flag."""

    def test_feature_flag_disabled_by_default(self, monkeypatch):
        """Continual learning should be disabled by default."""
        monkeypatch.delenv("KERNEL_CONTINUAL_LEARNING_ENABLED", raising=False)
        assert is_continual_learning_enabled() is False

    def test_feature_flag_can_be_enabled(self, monkeypatch):
        """Continual learning can be enabled via env."""
        monkeypatch.setenv("KERNEL_CONTINUAL_LEARNING_ENABLED", "1")
        assert is_continual_learning_enabled() is True

        monkeypatch.setenv("KERNEL_CONTINUAL_LEARNING_ENABLED", "true")
        assert is_continual_learning_enabled() is True

        monkeypatch.setenv("KERNEL_CONTINUAL_LEARNING_ENABLED", "0")
        assert is_continual_learning_enabled() is False
