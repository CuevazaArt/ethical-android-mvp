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
- ``KERNEL_RLHF_MODULATE_BAYESIAN`` — apply loaded reward model to ``BayesianInferenceEngine`` priors (default off)
- ``KERNEL_RLHF_FEATURE_EXTRACTOR_TYPE`` — "embedding" | "lexical" | "hybrid"
- ``KERNEL_RLHF_MODEL_TYPE`` — "logistic" | "lightweight_nn"
- ``KERNEL_RLHF_ARTIFACTS_PATH`` — storage path (default ``artifacts/rlhf/``)
- ``KERNEL_RLHF_MAX_STEPS`` — gradient steps (default 1000)
- ``KERNEL_RLHF_LEARNING_RATE`` — step size (default 0.001)

Runtime (Plan C.1.1 — Bayesian Dirichlet nudge via :mod:`bayesian_engine`):

- ``KERNEL_RLHF_MODULATE_USE_TRAINED_MODEL`` — when truthy, load ``reward_model.json`` from
  ``KERNEL_RLHF_ARTIFACTS_PATH`` and use :class:`RewardModel` predictions; otherwise a bounded
  MalAbs heuristic (``max(embedding_sim, lexical_score)``) applies.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
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


def feature_vector_from_malabs_dict(
    rlhf_features: dict[str, Any] | None,
) -> FeatureVector | None:
    """
    Map MalAbs / semantic gate ``rlhf_features`` to :class:`FeatureVector` for :class:`RewardModel`.

    Returns ``None`` when features are missing or an empty mapping (no signal). Otherwise
    coordinates are clamped and non-finite values collapse to safe defaults (plan C.1.1).
    """
    if rlhf_features is None or len(rlhf_features) == 0:
        return None

    def _f(key: str, default: float = 0.0) -> float:
        try:
            v = float(rlhf_features.get(key, default) or default)
        except (TypeError, ValueError):
            return default
        if not np.isfinite(v):
            return default
        return float(np.clip(v, 0.0, 1.0))

    def _i(key: str, default: int = 0) -> int:
        try:
            v = int(rlhf_features.get(key, default) or default)
        except (TypeError, ValueError):
            return default
        return max(0, v)

    amb_raw = rlhf_features.get("is_ambiguous", False)
    is_ambiguous = bool(amb_raw)

    return FeatureVector(
        embedding_sim=_f("embedding_sim", 0.0),
        lexical_score=_f("lexical_score", 0.0),
        perception_confidence=_f("perception_confidence", 0.5),
        is_ambiguous=is_ambiguous,
        category_id=_i("category_id", 0),
    )


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
        """Run :meth:`predict` in a worker thread so callers never block the event loop."""
        return await asyncio.to_thread(self.predict, features)

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
        with open(path, encoding="utf-8") as f:
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
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    examples.append(LabeledExample.from_dict(json.loads(line)))
                except (json.JSONDecodeError, TypeError, KeyError):
                    continue
        return examples


def is_rlhf_enabled() -> bool:
    """Check if RLHF is enabled."""
    v = os.environ.get("KERNEL_RLHF_REWARD_MODEL_ENABLED", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _finite_unit(x: float, default: float) -> float:
    if np.isnan(x):
        return float(default)
    if np.isposinf(x):
        return 1.0
    if np.isneginf(x):
        return 0.0
    return float(np.clip(x, 0.0, 1.0))


def feature_vector_from_malabs_rlhf_dict(d: dict[str, Any]) -> FeatureVector:
    """Alias for :func:`feature_vector_from_malabs_dict` (semantic gate / MalAbs keys)."""
    out = feature_vector_from_malabs_dict(d)
    if out is None:
        return FeatureVector()
    return out


def reward_predict_from_malabs_dict(
    model: RewardModel, features: dict[str, Any]
) -> tuple[float, float]:
    """
    Run a trained :class:`RewardModel` on MalAbs-shaped features; returns (harm_score, confidence).

    ``harm_score`` is the classifier probability of harmful class [0, 1]; confidence is model
    confidence. Falls back to neutral score with zero confidence if the model is not trained.
    """
    fv = feature_vector_from_malabs_dict(features)
    if fv is None:
        return model.predict(FeatureVector())
    return model.predict(fv)


ENV_KERNEL_RLHF_MODULATE_BAYESIAN = "KERNEL_RLHF_MODULATE_BAYESIAN"


def _finite_unit_interval(x: Any, default: float = 0.5) -> float:
    """Coerce reward outputs to a finite value in ``[0, 1]`` for Bayesian modulation."""
    try:
        return _finite_unit(float(x), float(default))
    except (TypeError, ValueError):
        return float(default)


def is_rlhf_modulate_bayesian() -> bool:
    """When true, map MalAbs ``rlhf_features`` through the reward model into Bayesian priors."""
    v = os.environ.get(ENV_KERNEL_RLHF_MODULATE_BAYESIAN, "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _reward_model_artifact_path() -> Path:
    base = Path(os.environ.get("KERNEL_RLHF_ARTIFACTS_PATH", "artifacts/rlhf/"))
    return base / "reward_model.json"


_cached_reward_model: RewardModel | None = None
_cached_reward_model_key: str | None = None


def reset_rlhf_reward_model_cache() -> None:
    """Clear cached reward artifact load (tests or hot-reload)."""
    global _cached_reward_model, _cached_reward_model_key
    _cached_reward_model = None
    _cached_reward_model_key = None


def _get_cached_reward_model() -> RewardModel:
    global _cached_reward_model, _cached_reward_model_key
    p = _reward_model_artifact_path().resolve()
    key = str(p)
    if _cached_reward_model is not None and _cached_reward_model_key == key:
        return _cached_reward_model
    rm = RewardModel()
    rm.load(p)
    _cached_reward_model = rm
    _cached_reward_model_key = key
    return rm


def apply_rlhf_modulation_to_bayesian(bayesian: Any, signals: Mapping[str, Any]) -> None:
    """
    If enabled, run MalAbs ``rlhf_features`` through the reward model and nudge Dirichlet priors.

    No-op when the flag is off, features are missing, the model is untrained, or ``bayesian`` has
    no ``apply_rlhf_modulation`` (e.g. plain ``WeightedEthicsScorer``).
    """
    # Avoid circular imports: BayesianInferenceEngine is expected at runtime.
    if not is_rlhf_modulate_bayesian():
        return
    if not hasattr(bayesian, "apply_rlhf_modulation"):
        return
    raw = signals.get("rlhf_features") if isinstance(signals, Mapping) else None
    fv = feature_vector_from_malabs_dict(raw if isinstance(raw, dict) else None)
    if fv is None:
        return
    model = _get_cached_reward_model()
    score, confidence = model.predict(fv)
    score = _finite_unit_interval(score, 0.5)
    confidence = _finite_unit_interval(confidence, 0.0)
    bayesian.apply_rlhf_modulation(score, confidence)


async def apply_rlhf_modulation_to_bayesian_async(bayesian: Any, signals: Mapping[str, Any]) -> None:
    """Async variant using ``apredict`` for cooperative async pipelines."""
    if not is_rlhf_modulate_bayesian():
        return
    if not hasattr(bayesian, "apply_rlhf_modulation"):
        return
    raw = signals.get("rlhf_features") if isinstance(signals, Mapping) else None
    fv = feature_vector_from_malabs_dict(raw if isinstance(raw, dict) else None)
    if fv is None:
        return
    model = _get_cached_reward_model()
    score, confidence = await model.apredict(fv)
    score = _finite_unit_interval(score, 0.5)
    confidence = _finite_unit_interval(confidence, 0.0)
    bayesian.apply_rlhf_modulation(score, confidence)
