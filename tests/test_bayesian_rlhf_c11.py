"""Plan C.1.1 — MalAbs rlhf_features → :class:`RewardModel` → Bayesian Dirichlet nudge."""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.bayesian_engine import (
    BayesianInferenceEngine,
    BayesianMode,
    reset_rlhf_trained_model_cache_for_tests,
)
from src.modules.rlhf_reward_model import (
    FeatureVector,
    LabeledExample,
    RewardModel,
    feature_vector_from_malabs_rlhf_dict,
    reward_predict_from_malabs_dict,
)


def test_feature_vector_from_malabs_sanitizes_nan_and_category():
    d = {
        "embedding_sim": float("nan"),
        "lexical_score": 0.4,
        "perception_confidence": float("inf"),
        "is_ambiguous": True,
        "category_id": "7",
    }
    fv = feature_vector_from_malabs_rlhf_dict(d)
    assert fv.embedding_sim == 0.0
    assert fv.lexical_score == 0.4
    assert fv.perception_confidence == 0.5
    assert fv.is_ambiguous is True
    assert fv.category_id == 7


def test_reward_predict_uses_trained_weights(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    m = RewardModel()
    ex = [
        LabeledExample(
            id="1",
            features=FeatureVector(
                embedding_sim=0.9,
                lexical_score=0.8,
                perception_confidence=0.7,
                is_ambiguous=False,
                category_id=1,
            ),
            human_label="blocked",
        ),
        LabeledExample(
            id="2",
            features=FeatureVector(
                embedding_sim=0.1,
                lexical_score=0.1,
                perception_confidence=0.5,
                is_ambiguous=False,
                category_id=0,
            ),
            human_label="benign",
        ),
    ]
    m.train(ex, max_steps=50, learning_rate=0.05)
    mp = tmp_path / "artifacts" / "rlhf"
    mp.mkdir(parents=True)
    m.save(mp / "reward_model.json")

    monkeypatch.setenv("KERNEL_RLHF_ARTIFACTS_PATH", str(mp))
    feats = {
        "embedding_sim": 0.95,
        "lexical_score": 0.9,
        "perception_confidence": 0.8,
        "is_ambiguous": False,
        "category_id": 1,
    }
    score, conf = reward_predict_from_malabs_dict(m, feats)
    assert 0.0 <= score <= 1.0
    assert 0.0 <= conf <= 1.0
    assert np.isfinite(score) and np.isfinite(conf)


def test_maybe_modulate_trained_model_nudges_alpha(tmp_path, monkeypatch):
    reset_rlhf_trained_model_cache_for_tests()
    m = RewardModel()
    ex = [
        LabeledExample(
            id="1",
            features=FeatureVector(0.95, 0.9, 0.8, False, 2),
            human_label="blocked",
        ),
        LabeledExample(
            id="2",
            features=FeatureVector(0.05, 0.05, 0.5, False, 0),
            human_label="benign",
        ),
    ]
    m.train(ex, max_steps=80, learning_rate=0.08)
    mp = tmp_path / "rlhf"
    mp.mkdir(parents=True)
    m.save(mp / "reward_model.json")

    monkeypatch.setenv("KERNEL_RLHF_ARTIFACTS_PATH", str(tmp_path / "rlhf"))
    monkeypatch.setenv("KERNEL_RLHF_MODULATE_BAYESIAN", "1")
    monkeypatch.setenv("KERNEL_RLHF_MODULATE_USE_TRAINED_MODEL", "1")
    eng = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
    alpha0 = eng.posterior_alpha.copy()
    eng.maybe_modulate_from_malabs_rlhf_features(
        {
            "embedding_sim": 0.99,
            "lexical_score": 0.95,
            "perception_confidence": 0.9,
            "is_ambiguous": False,
            "category_id": 2,
        }
    )
    assert np.all(eng.posterior_alpha >= 1.0)
    assert float(np.sum(eng.posterior_alpha)) > float(np.sum(alpha0))
    reset_rlhf_trained_model_cache_for_tests()


def test_apply_rlhf_modulation_ignores_non_finite_alpha(monkeypatch):
    eng = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
    eng.posterior_alpha = np.array([np.nan, 3.0, 3.0], dtype=np.float64)
    eng.apply_rlhf_modulation(0.5, 0.8)
    assert np.all(np.isfinite(eng.posterior_alpha))
