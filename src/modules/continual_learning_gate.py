"""
Continual learning with ethical constraints (Phase 3+, ADR 0015 draft).

Maintains replay buffers of labeled examples (benign, blocked, ambiguous) from
operator logs and evaluation sets. Enables online threshold updates **without
eroding hard constraints** (lexical MalAbs, constitution L0 hooks).

**Constraint hierarchy:**
1. **Hard (never relax):** Lexical MalAbs layer, constitution L0 (human life)
2. **Advisory (tunable):** Semantic thresholds (θ_block, θ_allow), Bayesian pruning
3. **Hyperparameters (optimizable):** Decay rates, confidence bands, penalty weights

**Replay buffer strategy:**
- Stratified batches: ~40% benign, ~40% blocked, ~20% ambiguous
- TTL-based aging: recent examples weighted more heavily
- Tagging: source (operator, evaluation, DAO), confidence, timestamp

**Safety gates:**
- All threshold changes pass full pytest suite
- Red-team JSONL validation before applying
- Rollback on regression (>10% loss increase)
- Audit trail: timestamp, who, what, why, metrics before/after

Env:
- ``KERNEL_CONTINUAL_LEARNING_ENABLED`` — master switch (default off)
- ``KERNEL_REPLAY_BUFFER_SIZE`` — max stored examples (default 10000)
- ``KERNEL_REPLAY_BUFFER_TTL_S`` — example age cutoff (default 2592000 = 30 days)
- ``KERNEL_REPLAY_BUFFER_PATH`` — storage path (default ``data/replay_buffer.jsonl``)
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np


@dataclass
class ReplayExample:
    """Single labeled example for continual learning."""

    id: str  # Unique identifier
    text: str  # Input text
    label: Literal["benign", "blocked", "ambiguous"]  # True label
    category: str = ""  # MalAbs category if blocked
    source: str = "unknown"  # Where it came from (operator, eval, DAO)
    confidence: float = 0.5  # Human confidence in label [0, 1]
    embedding: list[float] = field(default_factory=list)  # Optional embedding
    metadata: dict[str, Any] = field(default_factory=dict)  # Arbitrary metadata
    timestamp: float = field(default_factory=time.time)  # When added

    def age_seconds(self) -> float:
        """Age of example in seconds."""
        return time.time() - self.timestamp

    def is_expired(self, ttl_s: float) -> bool:
        """Check if example has exceeded TTL (0 = no expiry)."""
        if ttl_s <= 0:
            return False
        return self.age_seconds() > ttl_s

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        d = asdict(self)
        d["timestamp"] = self.timestamp  # Ensure float
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ReplayExample:
        """Deserialize from dict."""
        return cls(**d)


@dataclass
class StratifiedBatch:
    """Stratified batch for training/evaluation."""

    benign: list[ReplayExample] = field(default_factory=list)  # ~40%
    blocked: list[ReplayExample] = field(default_factory=list)  # ~40%
    ambiguous: list[ReplayExample] = field(default_factory=list)  # ~20%

    @property
    def all(self) -> list[ReplayExample]:
        """All examples in batch."""
        return self.benign + self.blocked + self.ambiguous

    def __len__(self) -> int:
        return len(self.all)


class ReplayBuffer:
    """Stratified replay buffer for continual learning."""

    def __init__(self, max_size: int = 10000, ttl_s: float = 2592000):
        """Initialize buffer."""
        self.max_size = max_size
        self.ttl_s = ttl_s
        self.examples: dict[str, ReplayExample] = {}

    def add(self, example: ReplayExample) -> None:
        """Add example to buffer (FIFO when full)."""
        if len(self.examples) >= self.max_size:
            # Remove oldest
            oldest_id = min(self.examples.keys(), key=lambda id: self.examples[id].timestamp)
            del self.examples[oldest_id]

        self.examples[example.id] = example

    def add_many(self, examples: list[ReplayExample]) -> None:
        """Add multiple examples."""
        for ex in examples:
            self.add(ex)

    def clean_expired(self) -> int:
        """Remove expired examples. Return count deleted."""
        expired_ids = [id for id, ex in self.examples.items() if ex.is_expired(self.ttl_s)]
        for id in expired_ids:
            del self.examples[id]
        return len(expired_ids)

    def get_stratified_batch(self, n_total: int = 100) -> StratifiedBatch:
        """Get stratified random batch (40% benign, 40% blocked, 20% ambiguous)."""
        self.clean_expired()

        # Group by label
        by_label = {"benign": [], "blocked": [], "ambiguous": []}
        for ex in self.examples.values():
            by_label[ex.label].append(ex)

        # Stratified sampling
        batch = StratifiedBatch()
        batch.benign = self._sample(by_label["benign"], int(0.40 * n_total))
        batch.blocked = self._sample(by_label["blocked"], int(0.40 * n_total))
        batch.ambiguous = self._sample(by_label["ambiguous"], int(0.20 * n_total))

        return batch

    @staticmethod
    def _sample(pool: list[ReplayExample], n: int) -> list[ReplayExample]:
        """Weighted sample (recent examples weighted higher)."""
        if not pool:
            return []
        if len(pool) <= n:
            return pool

        # Weight by recency: exp(-age/half_life)
        half_life_s = 86400 * 7  # 1 week
        now = time.time()
        weights = [np.exp(-(now - ex.timestamp) / half_life_s) for ex in pool]
        weights_norm = np.array(weights) / sum(weights)

        indices = np.random.choice(len(pool), size=min(n, len(pool)), replace=False, p=weights_norm)
        return [pool[i] for i in indices]

    def save(self, path: Path) -> None:
        """Save buffer to JSONL."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for ex in self.examples.values():
                f.write(json.dumps(ex.to_dict()) + "\n")

    def load(self, path: Path) -> None:
        """Load buffer from JSONL."""
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ex = ReplayExample.from_dict(json.loads(line))
                        self.add(ex)
                    except (json.JSONDecodeError, TypeError, KeyError):
                        continue

    def __len__(self) -> int:
        return len(self.examples)


@dataclass
class HardConstraintSet:
    """Immutable hard constraints that optimizer must preserve."""

    name: str
    description: str
    constraints: dict[str, Any] = field(default_factory=dict)

    def validate(self, theta_allow: float, theta_block: float) -> bool:
        """Check if thresholds satisfy all hard constraints."""
        # Constraint 1: allow < block
        if theta_allow >= theta_block:
            return False

        # Constraint 2: Lexical MalAbs always blocks absolute evil
        # (enforced by AbsoluteEvilDetector.py, not parameterized)

        # Constraint 3: θ_block must be in sensible range
        if theta_block < 0.5 or theta_block > 0.95:
            return False

        # Constraint 4: θ_allow must be in sensible range
        if theta_allow < 0.0 or theta_allow >= 0.8:
            return False

        return True


class ContinualLearningGate:
    """Online threshold updates with constraint preservation."""

    def __init__(
        self,
        replay_buffer_size: int | None = None,
        ttl_s: float | None = None,
        buffer_path: Path | None = None,
    ):
        """Initialize continual learning gate."""
        self.replay_buffer = ReplayBuffer(
            max_size=replay_buffer_size
            or int(os.environ.get("KERNEL_REPLAY_BUFFER_SIZE", "10000")),
            ttl_s=ttl_s or float(os.environ.get("KERNEL_REPLAY_BUFFER_TTL_S", "2592000")),
        )
        self.buffer_path = buffer_path or Path(
            os.environ.get("KERNEL_REPLAY_BUFFER_PATH", "data/replay_buffer.jsonl")
        )

        # Hard constraints (never relax)
        self.hard_constraints = HardConstraintSet(
            name="MalAbs Hard Constraints",
            description="Lexical MalAbs, Constitution L0, advisory threshold bounds",
            constraints={
                "theta_allow_min": 0.0,
                "theta_allow_max": 0.8,
                "theta_block_min": 0.5,
                "theta_block_max": 0.95,
                "allow_less_than_block": True,
            },
        )

        # Load persisted buffer
        self.reload_buffer()

    def reload_buffer(self) -> None:
        """Reload buffer from disk."""
        self.replay_buffer.load(self.buffer_path)

    def add_example(
        self,
        text: str,
        label: Literal["benign", "blocked", "ambiguous"],
        category: str = "",
        source: str = "unknown",
        confidence: float = 0.5,
    ) -> None:
        """Add labeled example to replay buffer."""
        import uuid

        ex = ReplayExample(
            id=f"{source}_{uuid.uuid4().hex[:8]}",
            text=text,
            label=label,
            category=category,
            source=source,
            confidence=confidence,
        )
        self.replay_buffer.add(ex)

    def can_apply_threshold_update(
        self, theta_allow_new: float, theta_block_new: float
    ) -> tuple[bool, str]:
        """Check if threshold update is allowed (constraint validation)."""
        if not self.hard_constraints.validate(theta_allow_new, theta_block_new):
            reasons = []
            if theta_allow_new >= theta_block_new:
                reasons.append("θ_allow must be < θ_block")
            if theta_allow_new < 0.0 or theta_allow_new >= 0.8:
                reasons.append(f"θ_allow out of range [0.0, 0.8): got {theta_allow_new:.3f}")
            if theta_block_new < 0.5 or theta_block_new > 0.95:
                reasons.append(f"θ_block out of range [0.5, 0.95]: got {theta_block_new:.3f}")
            return False, "; ".join(reasons)

        return True, "All constraints satisfied"

    def get_stratified_batch(self, n: int = 100) -> StratifiedBatch:
        """Get stratified batch for evaluation/training."""
        self.replay_buffer.clean_expired()
        return self.replay_buffer.get_stratified_batch(n)

    def save_buffer(self) -> None:
        """Persist buffer to disk."""
        self.replay_buffer.save(self.buffer_path)

    def buffer_stats(self) -> dict[str, Any]:
        """Get buffer statistics."""
        by_label = {"benign": 0, "blocked": 0, "ambiguous": 0}
        for ex in self.replay_buffer.examples.values():
            by_label[ex.label] += 1

        return {
            "total_examples": len(self.replay_buffer),
            "by_label": by_label,
            "max_size": self.replay_buffer.max_size,
            "ttl_s": self.replay_buffer.ttl_s,
            "expired_cleaned": self.replay_buffer.clean_expired(),
        }


def is_continual_learning_enabled() -> bool:
    """Check if continual learning is enabled."""
    v = os.environ.get("KERNEL_CONTINUAL_LEARNING_ENABLED", "0").strip().lower()
    return v in ("1", "true", "yes", "on")
