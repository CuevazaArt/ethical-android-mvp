"""
RLHF Reward Modeling for controlled fine-tuning (Phase 3+, ADR planning).

Extracts features from MalAbs evaluation artifacts and trains a small reward
classifier to model human preferences. Enables LoRA fine-tuning behind feature
flags with spacetime constraints (max steps, frozen prefix, regression gates).

**Pipeline:**
1. Collect human labels (operator feedback, red-team results)
2. Extract features (embedding sims, lexical flags, perception aggregates)
3. Train reward model (logistic regression, lightweight NN)
4. Optional LoRA fine-tune with hard constraint preservation

**Safety constraints:**
- Hard constraints (lexical MalAbs, constitution L0) frozen in weight prefix
- Optimizer can only adjust advisory thresholds within bounded bands
- Full pytest + red-team validation before merge
- Rollback on regression

Env:
- ``KERNEL_RLHF_REWARD_MODEL_ENABLED`` — master switch (default off)
- ``KERNEL_RLHF_MODULATE_BAYESIAN`` — when ``1``, after each MalAbs chat evaluation,
  run the reward model on ``rlhf_features`` and call
  :meth:`~src.modules.bayesian_engine.BayesianInferenceEngine.apply_rlhf_modulation`
  (default **off**; loads ``reward_model.json`` from artifacts when present).
- ``KERNEL_RLHF_FEATURE_EXTRACTOR_TYPE`` — "embedding" | "lexical" | "hybrid"
- ``KERNEL_RLHF_MODEL_TYPE`` — "logistic" | "lightweight_nn"
- ``KERNEL_RLHF_ARTIFACTS_PATH`` — storage path (default ``artifacts/rlhf/``)
- ``KERNEL_RLHF_MAX_STEPS`` — gradient steps (default 1000)
- ``KERNEL_RLHF_LEARNING_RATE`` — step size (default 0.001)
# IP: cuevaza | arq.jvof
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Literal

import numpy as np


@dataclass
class FeatureVector:
    """Extracted features from MalAbs evaluation."""

    embedding_sim: float = 0.0  # Cosine sim to nearest anchor
    lexical_score: float = 0.0  # Lexical layer confidence [0, 1]
    perception_confidence: float = 0.5  # Perception stage confidence
    is_ambiguous: bool = False  # In semantic ambiguous band
    category_id: int = 0  # MalAbs category encoding
    timestamp: float = field(default_factory=time.time)

    def to_vector(self) -> np.ndarray:
        """Convert to feature vector for model input."""
        return np.array([
            self.embedding_sim,
            self.lexical_score,
            self.perception_confidence,
            float(self.is_ambiguous),
            float(self.category_id),
        ], dtype=np.float32)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> FeatureVector:
        """Deserialize from dict."""
        return cls(**d)


@dataclass
class LabeledExample:
    """Human-labeled training example for reward model."""

    id: str
    features: FeatureVector
    human_label: Literal["benign", "blocked", "ambiguous"]  # True label
    confidence: float = 0.5  # Labeler confidence [0, 1]
    source: str = "unknown"  # Where label came from
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON."""
        d = asdict(self)
        d["features"] = self.features.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LabeledExample:
        """Deserialize from JSON."""
        d["features"] = FeatureVector.from_dict(d["features"])
        return cls(**d)


class RewardModel:
    """Lightweight reward classifier for human preference modeling."""

    def __init__(self, model_type: Literal["logistic", "lightweight_nn"] = "logistic"):
        """Initialize reward model."""
        self.model_type = model_type
        self.is_trained = False
        self.weights: np.ndarray | None = None
        self.bias: float = 0.0
        self.training_history: list[dict[str, float]] = []

    def extract_features(
        self, embedding_sim: float, lexical_score: float, perception_conf: float,
        is_ambiguous: bool, category_id: int
    ) -> FeatureVector:
        """Create feature vector from evaluation artifacts."""
        return FeatureVector(
            embedding_sim=embedding_sim,
            lexical_score=lexical_score,
            perception_confidence=perception_conf,
            is_ambiguous=is_ambiguous,
            category_id=category_id,
        )

    def train(
        self,
        examples: list[LabeledExample],
        max_steps: int = 1000,
        learning_rate: float = 0.001,
    ) -> None:
        """Train reward model on labeled examples."""
        if not examples:
            return

        # Prepare training data
        X = np.array([ex.features.to_vector() for ex in examples], dtype=np.float32)
        # Binary labels: 1 = blocked/ambiguous (harmful), 0 = benign (safe)
        y = np.array([1.0 if ex.human_label != "benign" else 0.0 for ex in examples], dtype=np.float32)

        # Simple logistic regression training
        self.weights = np.random.randn(X.shape[1]) * 0.01
        self.bias = 0.0

        for step in range(max_steps):
            # Forward pass
            logits = np.dot(X, self.weights) + self.bias
            probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -100, 100)))

            # Compute loss
            eps = 1e-7
            loss = -np.mean(y * np.log(probs + eps) + (1 - y) * np.log(1 - probs + eps))

            # Gradient descent
            grad_w = np.dot(X.T, (probs - y)) / len(examples)
            grad_b = np.mean(probs - y)

            self.weights -= learning_rate * grad_w
            self.bias -= learning_rate * grad_b

            if step % 100 == 0:
                self.training_history.append({"step": step, "loss": float(loss)})

        self.is_trained = True

    def predict(self, features: FeatureVector) -> tuple[float, float]:
        """
        Predict reward score for features.

        Returns (reward_score, confidence) where:
        - reward_score ∈ [0, 1]: predicted probability of harm (1 = harmful, 0 = safe)
        - confidence ∈ [0, 1]: model confidence in prediction
        """
        if not self.is_trained or self.weights is None:
            return 0.5, 0.0  # Neutral + no confidence

        X = features.to_vector()
        logit = float(np.dot(X, self.weights) + self.bias)
        score = 1.0 / (1.0 + np.exp(-np.clip(logit, -100, 100)))

        # Confidence = distance from 0.5
        confidence = abs(score - 0.5) * 2

        return float(score), confidence

    async def apredict(self, features: FeatureVector) -> tuple[float, float]:
        """Async wrapper for predict."""
        return self.predict(features)

    def save(self, path: Path) -> None:
        """Save model weights to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "model_type": self.model_type,
            "is_trained": self.is_trained,
            "weights": self.weights.tolist() if self.weights is not None else None,
            "bias": float(self.bias),
            "training_history": self.training_history,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: Path) -> None:
        """Load model weights from disk."""
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.model_type = data["model_type"]
        self.is_trained = data["is_trained"]
        self.weights = np.array(data["weights"], dtype=np.float32) if data["weights"] else None
        self.bias = float(data["bias"])
        self.training_history = data.get("training_history", [])


class RLHFPipeline:
    """RLHF pipeline orchestration with safety constraints."""

    def __init__(
        self,
        feature_extractor_type: Literal["embedding", "lexical", "hybrid"] = "hybrid",
        model_type: Literal["logistic", "lightweight_nn"] = "logistic",
        artifacts_path: Path | None = None,
    ):
        """Initialize RLHF pipeline."""
        self.feature_extractor_type = feature_extractor_type
        self.reward_model = RewardModel(model_type=model_type)
        self.artifacts_path = artifacts_path or Path(
            os.environ.get("KERNEL_RLHF_ARTIFACTS_PATH", "artifacts/rlhf/")
        )
        self.artifacts_path.mkdir(parents=True, exist_ok=True)

    def create_labeled_example(
        self,
        id: str,
        embedding_sim: float,
        lexical_score: float,
        perception_conf: float,
        is_ambiguous: bool,
        category_id: int,
        human_label: Literal["benign", "blocked", "ambiguous"],
        confidence: float = 0.5,
        source: str = "operator",
    ) -> LabeledExample:
        """Create a labeled training example."""
        features = self.reward_model.extract_features(
            embedding_sim, lexical_score, perception_conf, is_ambiguous, category_id
        )
        return LabeledExample(
            id=id,
            features=features,
            human_label=human_label,
            confidence=confidence,
            source=source,
        )

    def train_reward_model(self, examples: list[LabeledExample]) -> None:
        """Train reward model on labeled examples."""
        max_steps = int(os.environ.get("KERNEL_RLHF_MAX_STEPS", "1000"))
        learning_rate = float(os.environ.get("KERNEL_RLHF_LEARNING_RATE", "0.001"))
        self.reward_model.train(examples, max_steps=max_steps, learning_rate=learning_rate)
        self.save_model()

    def save_model(self) -> None:
        """Save trained model to disk."""
        model_path = self.artifacts_path / "reward_model.json"
        self.reward_model.save(model_path)

    def load_model(self) -> None:
        """Load trained model from disk."""
        model_path = self.artifacts_path / "reward_model.json"
        self.reward_model.load(model_path)

    def save_examples(self, examples: list[LabeledExample], path: Path | None = None) -> None:
        """Save training examples to JSONL."""
        path = path or self.artifacts_path / "training_examples.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for ex in examples:
                f.write(json.dumps(ex.to_dict()) + "\n")

    def load_examples(self, path: Path | None = None) -> list[LabeledExample]:
        """Load training examples from JSONL."""
        path = path or self.artifacts_path / "training_examples.jsonl"
        if not path.exists():
            return []
        examples = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    examples.append(LabeledExample.from_dict(json.loads(line)))
                except (json.JSONDecodeError, TypeError, KeyError):
                    continue
        return examples

    def subscribe_to_bus(self, bus: Any) -> None:
        """
        Wire RLHF pipeline into the kernel event bus (optional integration hook).

        Allows RLHF to receive decision and episode events for online learning.
        This is a no-op stub; the bus integration is advisory-only and does not
        change reward-model training or inference behaviour.
        """


def is_rlhf_enabled() -> bool:
    """Check if RLHF is enabled."""
    v = os.environ.get("KERNEL_RLHF_REWARD_MODEL_ENABLED", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def rlhf_bayesian_modulation_enabled() -> bool:
    """True when MalAbs ``rlhf_features`` should nudge Dirichlet priors via the reward model."""
    v = os.environ.get("KERNEL_RLHF_MODULATE_BAYESIAN", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


_RLHF_RM_CACHE: RewardModel | None = None
_RLHF_RM_LOAD_ATTEMPTED: bool = False


def clear_rlhf_reward_model_cache_for_tests() -> None:
    """Reset lazy-loaded reward model (tests only)."""
    global _RLHF_RM_CACHE, _RLHF_RM_LOAD_ATTEMPTED
    _RLHF_RM_CACHE = None
    _RLHF_RM_LOAD_ATTEMPTED = False


def _loaded_reward_model_for_inference() -> RewardModel:
    """Return cached :class:`RewardModel`, loading ``reward_model.json`` once if present."""
    global _RLHF_RM_CACHE, _RLHF_RM_LOAD_ATTEMPTED
    if _RLHF_RM_CACHE is not None:
        return _RLHF_RM_CACHE
    rm = RewardModel()
    if not _RLHF_RM_LOAD_ATTEMPTED:
        ap = Path(os.environ.get("KERNEL_RLHF_ARTIFACTS_PATH", "artifacts/rlhf/"))
        path = ap / "reward_model.json"
        if path.exists():
            rm.load(path)
        _RLHF_RM_LOAD_ATTEMPTED = True
    _RLHF_RM_CACHE = rm
    return _RLHF_RM_CACHE


def feature_vector_from_rlhf_dict(features: dict[str, Any]) -> FeatureVector:
    """Build :class:`FeatureVector` from MalAbs ``rlhf_features`` dict."""
    return FeatureVector(
        embedding_sim=float(features.get("embedding_sim", 0.0)),
        lexical_score=float(features.get("lexical_score", 0.0)),
        perception_confidence=float(features.get("perception_confidence", features.get("perception_conf", 0.5))),
        is_ambiguous=bool(features.get("is_ambiguous", False)),
        category_id=int(features.get("category_id", 0)),
    )


def maybe_modulate_bayesian_from_malabs(bayesian: Any, rlhf_features: dict[str, Any] | None) -> None:
    """
    If ``KERNEL_RLHF_MODULATE_BAYESIAN`` is on and features exist, predict harm probability
    and apply ``bayesian.apply_rlhf_modulation(score, confidence)``.

    When no trained weights are on disk, :meth:`RewardModel.predict` returns neutral
    ``(0.5, 0.0)`` so Dirichlet updates are negligible (confidence gate).
    """
    if not rlhf_bayesian_modulation_enabled() or not rlhf_features:
        return
    if not hasattr(bayesian, "apply_rlhf_modulation"):
        return
    fv = feature_vector_from_rlhf_dict(rlhf_features)
    rm = _loaded_reward_model_for_inference()
    score, confidence = rm.predict(fv)
    bayesian.apply_rlhf_modulation(float(score), float(confidence))
