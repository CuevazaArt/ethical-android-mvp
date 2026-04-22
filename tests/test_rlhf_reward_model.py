"""Tests for RLHF Reward Model (Phase 3+ fine-tuning)."""

import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.bayesian_engine import BayesianInferenceEngine
from src.modules.rlhf_reward_model import (
    FeatureVector,
    LabeledExample,
    RewardModel,
    RLHFPipeline,
    clear_rlhf_reward_model_cache_for_tests,
    is_rlhf_enabled,
    maybe_modulate_bayesian_from_malabs,
    rlhf_bayesian_modulation_enabled,
)


class TestFeatureVector:
    """Tests for FeatureVector extraction and serialization."""

    def test_feature_vector_creation(self):
        """FeatureVector should initialize with default values."""
        fv = FeatureVector()
        assert fv.embedding_sim == 0.0
        assert fv.lexical_score == 0.0
        assert fv.perception_confidence == 0.5
        assert fv.is_ambiguous is False
        assert fv.category_id == 0
        assert fv.timestamp > 0

    def test_feature_vector_custom_values(self):
        """FeatureVector should accept custom values."""
        fv = FeatureVector(
            embedding_sim=0.85,
            lexical_score=0.7,
            perception_confidence=0.9,
            is_ambiguous=True,
            category_id=5,
        )
        assert fv.embedding_sim == 0.85
        assert fv.lexical_score == 0.7
        assert fv.perception_confidence == 0.9
        assert fv.is_ambiguous is True
        assert fv.category_id == 5

    def test_feature_vector_to_vector(self):
        """to_vector() should return 5D numpy array."""
        fv = FeatureVector(
            embedding_sim=0.8,
            lexical_score=0.6,
            perception_confidence=0.7,
            is_ambiguous=True,
            category_id=3,
        )
        vec = fv.to_vector()
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (5,)
        assert vec.dtype == np.float32
        assert vec[0] == 0.8  # embedding_sim
        assert vec[1] == 0.6  # lexical_score
        assert vec[2] == 0.7  # perception_confidence
        assert vec[3] == 1.0  # is_ambiguous (True as float)
        assert vec[4] == 3.0  # category_id

    def test_feature_vector_to_dict(self):
        """to_dict() should serialize to JSON-compatible dict."""
        fv = FeatureVector(
            embedding_sim=0.85,
            lexical_score=0.75,
            perception_confidence=0.9,
            is_ambiguous=True,
            category_id=2,
        )
        d = fv.to_dict()
        assert d["embedding_sim"] == 0.85
        assert d["lexical_score"] == 0.75
        assert d["perception_confidence"] == 0.9
        assert d["is_ambiguous"] is True
        assert d["category_id"] == 2
        assert "timestamp" in d

    def test_feature_vector_from_dict(self):
        """from_dict() should reconstruct FeatureVector."""
        original = FeatureVector(
            embedding_sim=0.85,
            lexical_score=0.75,
            perception_confidence=0.9,
            is_ambiguous=True,
            category_id=2,
        )
        d = original.to_dict()
        restored = FeatureVector.from_dict(d)
        assert restored.embedding_sim == original.embedding_sim
        assert restored.lexical_score == original.lexical_score
        assert restored.perception_confidence == original.perception_confidence
        assert restored.is_ambiguous == original.is_ambiguous
        assert restored.category_id == original.category_id

    def test_feature_vector_roundtrip_via_json(self):
        """FeatureVector should survive JSON serialization roundtrip."""
        original = FeatureVector(
            embedding_sim=0.9,
            lexical_score=0.8,
            perception_confidence=0.95,
            is_ambiguous=True,
            category_id=7,
        )
        json_str = json.dumps(original.to_dict())
        d = json.loads(json_str)
        restored = FeatureVector.from_dict(d)
        assert restored.embedding_sim == original.embedding_sim
        assert restored.category_id == original.category_id


class TestLabeledExample:
    """Tests for LabeledExample training data."""

    def test_labeled_example_creation(self):
        """LabeledExample should initialize with features and label."""
        fv = FeatureVector(embedding_sim=0.8, lexical_score=0.7)
        ex = LabeledExample(
            id="ex-1",
            features=fv,
            human_label="benign",
            confidence=0.9,
            source="operator",
        )
        assert ex.id == "ex-1"
        assert ex.features == fv
        assert ex.human_label == "benign"
        assert ex.confidence == 0.9
        assert ex.source == "operator"

    def test_labeled_example_label_types(self):
        """LabeledExample should accept all valid label types."""
        fv = FeatureVector()
        for label in ["benign", "blocked", "ambiguous"]:
            ex = LabeledExample(id=f"ex-{label}", features=fv, human_label=label)
            assert ex.human_label == label

    def test_labeled_example_to_dict(self):
        """to_dict() should serialize LabeledExample with nested features."""
        fv = FeatureVector(embedding_sim=0.8, category_id=3)
        ex = LabeledExample(
            id="ex-1",
            features=fv,
            human_label="blocked",
            confidence=0.85,
            source="red-team",
            metadata={"risk_level": "high"},
        )
        d = ex.to_dict()
        assert d["id"] == "ex-1"
        assert d["human_label"] == "blocked"
        assert d["confidence"] == 0.85
        assert d["source"] == "red-team"
        assert d["metadata"]["risk_level"] == "high"
        assert isinstance(d["features"], dict)
        assert d["features"]["embedding_sim"] == 0.8

    def test_labeled_example_from_dict(self):
        """from_dict() should reconstruct LabeledExample."""
        fv = FeatureVector(embedding_sim=0.8, category_id=3)
        original = LabeledExample(
            id="ex-1",
            features=fv,
            human_label="blocked",
            confidence=0.85,
        )
        d = original.to_dict()
        restored = LabeledExample.from_dict(d)
        assert restored.id == original.id
        assert restored.human_label == original.human_label
        assert restored.features.embedding_sim == original.features.embedding_sim
        assert restored.features.category_id == original.features.category_id


class TestRewardModel:
    """Tests for RewardModel training and inference."""

    def test_reward_model_creation(self):
        """RewardModel should initialize untrained."""
        model = RewardModel(model_type="logistic")
        assert model.is_trained is False
        assert model.weights is None
        assert model.bias == 0.0
        assert model.training_history == []

    def test_extract_features(self):
        """extract_features() should create FeatureVector from raw values."""
        model = RewardModel()
        fv = model.extract_features(
            embedding_sim=0.85,
            lexical_score=0.75,
            perception_conf=0.9,
            is_ambiguous=True,
            category_id=3,
        )
        assert isinstance(fv, FeatureVector)
        assert fv.embedding_sim == 0.85
        assert fv.lexical_score == 0.75
        assert fv.is_ambiguous is True
        assert fv.category_id == 3

    def test_train_empty_examples(self):
        """train() should handle empty example list gracefully."""
        model = RewardModel()
        model.train(examples=[], max_steps=100)
        assert model.is_trained is False

    def test_train_single_example(self):
        """train() should work with single example."""
        model = RewardModel()
        fv = FeatureVector(embedding_sim=0.8, lexical_score=0.7)
        ex = LabeledExample(id="ex-1", features=fv, human_label="benign")
        model.train(examples=[ex], max_steps=10, learning_rate=0.001)
        assert model.is_trained is True
        assert model.weights is not None
        assert model.weights.shape == (5,)

    def test_train_multiple_examples(self):
        """train() should optimize weights on multiple examples."""
        model = RewardModel()
        examples = []
        for i in range(10):
            fv = FeatureVector(
                embedding_sim=0.1 * i,
                lexical_score=0.1 * (9 - i),
            )
            label = "benign" if i < 5 else "blocked"
            ex = LabeledExample(id=f"ex-{i}", features=fv, human_label=label)
            examples.append(ex)

        model.train(examples=examples, max_steps=50, learning_rate=0.01)
        assert model.is_trained is True
        assert len(model.training_history) > 0

    def test_train_updates_history(self):
        """train() should log loss at regular intervals."""
        model = RewardModel()
        fv = FeatureVector(embedding_sim=0.5)
        examples = [
            LabeledExample(id="ex-1", features=fv, human_label="benign"),
            LabeledExample(id="ex-2", features=fv, human_label="blocked"),
        ]
        model.train(examples=examples, max_steps=200, learning_rate=0.001)
        assert len(model.training_history) >= 2  # At least at step 0 and 100
        assert "step" in model.training_history[0]
        assert "loss" in model.training_history[0]

    def test_predict_untrained(self):
        """predict() on untrained model should return neutral score."""
        model = RewardModel()
        fv = FeatureVector(embedding_sim=0.8)
        score, confidence = model.predict(fv)
        assert score == 0.5
        assert confidence == 0.0

    def test_predict_trained(self):
        """predict() on trained model should return score and confidence."""
        model = RewardModel()
        examples = []
        for i in range(8):
            fv = FeatureVector(embedding_sim=0.1 * i, lexical_score=0.1 * (7 - i))
            label = "benign" if i < 4 else "blocked"
            examples.append(LabeledExample(id=f"ex-{i}", features=fv, human_label=label))

        model.train(examples=examples, max_steps=100, learning_rate=0.01)

        # Predict on benign-like features
        benign_fv = FeatureVector(embedding_sim=0.1, lexical_score=0.8)
        score, confidence = model.predict(benign_fv)
        assert 0.0 <= score <= 1.0
        assert 0.0 <= confidence <= 1.0

        # Predict on blocked-like features
        blocked_fv = FeatureVector(embedding_sim=0.9, lexical_score=0.1)
        score2, confidence2 = model.predict(blocked_fv)
        assert 0.0 <= score2 <= 1.0

    def test_save_and_load(self):
        """save() and load() should preserve model state."""
        model = RewardModel()
        examples = [
            LabeledExample(
                id=f"ex-{i}",
                features=FeatureVector(embedding_sim=0.1 * i),
                human_label="benign" if i % 2 == 0 else "blocked",
            )
            for i in range(6)
        ]
        model.train(examples=examples, max_steps=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "model.json"
            model.save(path)
            assert path.exists()

            model2 = RewardModel()
            model2.load(path)
            assert model2.is_trained == model.is_trained
            assert np.allclose(model2.weights, model.weights)
            assert model2.bias == model.bias

    def test_save_untrained_model(self):
        """save() should handle untrained model."""
        model = RewardModel()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "model.json"
            model.save(path)
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["is_trained"] is False
            assert data["weights"] is None

    def test_load_nonexistent(self):
        """load() should gracefully handle missing file."""
        model = RewardModel()
        model.load(Path("/nonexistent/path/model.json"))
        assert model.is_trained is False  # Should remain unchanged


class TestRLHFPipeline:
    """Tests for RLHFPipeline orchestration."""

    def test_pipeline_creation(self):
        """RLHFPipeline should initialize with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RLHFPipeline(artifacts_path=Path(tmpdir))
            assert pipeline.feature_extractor_type == "hybrid"
            assert isinstance(pipeline.reward_model, RewardModel)
            assert pipeline.artifacts_path == Path(tmpdir)

    def test_pipeline_create_labeled_example(self):
        """create_labeled_example() should create training data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RLHFPipeline(artifacts_path=Path(tmpdir))
            ex = pipeline.create_labeled_example(
                id="test-1",
                embedding_sim=0.8,
                lexical_score=0.7,
                perception_conf=0.9,
                is_ambiguous=False,
                category_id=2,
                human_label="benign",
                confidence=0.95,
            )
            assert ex.id == "test-1"
            assert ex.human_label == "benign"
            assert ex.features.embedding_sim == 0.8
            assert ex.confidence == 0.95

    def test_pipeline_train_reward_model(self, monkeypatch):
        """train_reward_model() should train and save model."""
        monkeypatch.setenv("KERNEL_RLHF_MAX_STEPS", "50")
        monkeypatch.setenv("KERNEL_RLHF_LEARNING_RATE", "0.01")

        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RLHFPipeline(artifacts_path=Path(tmpdir))

            examples = []
            for i in range(8):
                ex = pipeline.create_labeled_example(
                    id=f"ex-{i}",
                    embedding_sim=0.1 * i,
                    lexical_score=0.1 * (7 - i),
                    perception_conf=0.5,
                    is_ambiguous=False,
                    category_id=i % 3,
                    human_label="benign" if i < 4 else "blocked",
                )
                examples.append(ex)

            pipeline.train_reward_model(examples)
            assert pipeline.reward_model.is_trained is True

            # Check that model was saved
            model_path = Path(tmpdir) / "reward_model.json"
            assert model_path.exists()

    def test_pipeline_save_and_load_examples(self):
        """save_examples() and load_examples() should persist training data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RLHFPipeline(artifacts_path=Path(tmpdir))

            examples = [
                pipeline.create_labeled_example(
                    id=f"ex-{i}",
                    embedding_sim=0.5,
                    lexical_score=0.5,
                    perception_conf=0.5,
                    is_ambiguous=False,
                    category_id=0,
                    human_label="benign" if i % 2 == 0 else "blocked",
                )
                for i in range(4)
            ]

            pipeline.save_examples(examples)
            loaded = pipeline.load_examples()

            assert len(loaded) == len(examples)
            assert all(ex.id == loaded[i].id for i, ex in enumerate(examples))

    def test_pipeline_load_examples_nonexistent(self):
        """load_examples() should return empty list if file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RLHFPipeline(artifacts_path=Path(tmpdir))
            loaded = pipeline.load_examples()
            assert loaded == []

    def test_pipeline_save_load_model_roundtrip(self, monkeypatch):
        """Full pipeline should save and load models correctly."""
        monkeypatch.setenv("KERNEL_RLHF_MAX_STEPS", "30")

        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = RLHFPipeline(artifacts_path=Path(tmpdir))

            examples = [
                pipeline.create_labeled_example(
                    id=f"ex-{i}",
                    embedding_sim=0.1 * i,
                    lexical_score=0.9 - 0.1 * i,
                    perception_conf=0.7,
                    is_ambiguous=i % 3 == 0,
                    category_id=i % 4,
                    human_label="benign" if i < 3 else "blocked",
                )
                for i in range(6)
            ]

            pipeline.train_reward_model(examples)
            original_weights = pipeline.reward_model.weights.copy()

            # Create new pipeline and load model
            pipeline2 = RLHFPipeline(artifacts_path=Path(tmpdir))
            pipeline2.load_model()
            assert pipeline2.reward_model.is_trained is True
            assert np.allclose(pipeline2.reward_model.weights, original_weights)

    def test_pipeline_with_custom_feature_extractor(self):
        """Pipeline should support different feature extractor types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for ftype in ["embedding", "lexical", "hybrid"]:
                pipeline = RLHFPipeline(
                    feature_extractor_type=ftype,
                    artifacts_path=Path(tmpdir),
                )
                assert pipeline.feature_extractor_type == ftype


class TestRLHFEnabled:
    """Tests for is_rlhf_enabled() flag check."""

    def test_rlhf_disabled_by_default(self, monkeypatch):
        """RLHF should be disabled when env var is not set."""
        monkeypatch.delenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", raising=False)
        assert is_rlhf_enabled() is False

    def test_rlhf_enabled_with_1(self, monkeypatch):
        """RLHF should be enabled when env is '1'."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        assert is_rlhf_enabled() is True

    def test_rlhf_enabled_with_true(self, monkeypatch):
        """RLHF should be enabled when env is 'true'."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "true")
        assert is_rlhf_enabled() is True

    def test_rlhf_enabled_with_yes(self, monkeypatch):
        """RLHF should be enabled when env is 'yes'."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "yes")
        assert is_rlhf_enabled() is True

    def test_rlhf_enabled_with_on(self, monkeypatch):
        """RLHF should be enabled when env is 'on'."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "on")
        assert is_rlhf_enabled() is True

    def test_rlhf_disabled_with_0(self, monkeypatch):
        """RLHF should be disabled when env is '0'."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "0")
        assert is_rlhf_enabled() is False

    def test_rlhf_disabled_with_false(self, monkeypatch):
        """RLHF should be disabled when env is 'false'."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "false")
        assert is_rlhf_enabled() is False

    def test_rlhf_case_insensitive(self, monkeypatch):
        """RLHF flag check should be case-insensitive."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "TRUE")
        assert is_rlhf_enabled() is True

        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "Yes")
        assert is_rlhf_enabled() is True


class TestRlhfBayesianBridge:
    """Module C.1.1 — MalAbs rlhf_features → BayesianInferenceEngine.apply_rlhf_modulation."""

    def test_modulation_noop_when_flag_off(self, monkeypatch):
        monkeypatch.setenv("KERNEL_RLHF_MODULATE_BAYESIAN", "0")
        clear_rlhf_reward_model_cache_for_tests()
        be = BayesianInferenceEngine(mode="fixed")
        alpha0 = tuple(be.posterior_alpha.copy())
        maybe_modulate_bayesian_from_malabs(
            be,
            {
                "embedding_sim": 0.0,
                "lexical_score": 1.0,
                "perception_confidence": 1.0,
                "is_ambiguous": False,
                "category_id": 1,
            },
        )
        assert tuple(be.posterior_alpha) == alpha0
        assert rlhf_bayesian_modulation_enabled() is False

    def test_modulation_nudges_dirichlet_when_on_and_trained(self, monkeypatch, tmp_path):
        monkeypatch.setenv("KERNEL_RLHF_MODULATE_BAYESIAN", "1")
        monkeypatch.setenv("KERNEL_RLHF_ARTIFACTS_PATH", str(tmp_path))
        clear_rlhf_reward_model_cache_for_tests()

        rm = RewardModel()
        ex = [
            LabeledExample(
                id="a",
                features=FeatureVector(
                    embedding_sim=0.0,
                    lexical_score=1.0,
                    perception_confidence=1.0,
                    is_ambiguous=False,
                    category_id=0,
                ),
                human_label="blocked",
                confidence=1.0,
                source="t",
            ),
        ]
        rm.train(ex, max_steps=50, learning_rate=0.05)
        rm.save(tmp_path / "reward_model.json")

        be = BayesianInferenceEngine(mode="fixed")
        alpha_before = tuple(be.posterior_alpha.copy())
        maybe_modulate_bayesian_from_malabs(
            be,
            {
                "embedding_sim": 0.0,
                "lexical_score": 1.0,
                "perception_confidence": 1.0,
                "is_ambiguous": False,
                "category_id": 0,
            },
        )
        alpha_after = tuple(be.posterior_alpha.copy())
        assert alpha_after != alpha_before
