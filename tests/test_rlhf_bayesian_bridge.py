"""Bridge tests: MalAbs rlhf_features → RewardModel → Bayesian prior modulation."""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.modules.absolute_evil import merge_layered_rlhf_features
from src.modules.bayesian_engine import BayesianInferenceEngine
from src.modules.rlhf_reward_model import (
    apply_rlhf_modulation_to_bayesian,
    apply_rlhf_modulation_to_bayesian_async,
    feature_vector_from_malabs_dict,
    reset_rlhf_reward_model_cache,
)
from src.modules.rlhf_reward_model import LabeledExample, RewardModel


class TestFeatureVectorFromMalabs:
    def test_parses_standard_keys(self):
        d = {
            "embedding_sim": 0.7,
            "lexical_score": 0.2,
            "perception_confidence": 0.9,
            "is_ambiguous": True,
            "category_id": 4,
        }
        fv = feature_vector_from_malabs_dict(d)
        assert fv is not None
        assert fv.embedding_sim == pytest.approx(0.7)
        assert fv.lexical_score == pytest.approx(0.2)
        assert fv.perception_confidence == pytest.approx(0.9)
        assert fv.is_ambiguous is True
        assert fv.category_id == 4

    def test_none_and_empty(self):
        assert feature_vector_from_malabs_dict(None) is None
        assert feature_vector_from_malabs_dict({}) is None


class TestMergeLayeredRlhf:
    def test_overlay_wins(self):
        a = {"embedding_sim": 0.1, "category_id": 1}
        b = {"embedding_sim": 0.9, "category_id": 2}
        assert merge_layered_rlhf_features(a, b) == b


class TestRlhfBayesianBridge:
    def teardown_method(self):
        reset_rlhf_reward_model_cache()

    def test_modulation_no_op_when_flag_off(self, monkeypatch):
        monkeypatch.delenv("KERNEL_RLHF_MODULATE_BAYESIAN", raising=False)
        eng = BayesianInferenceEngine()
        alpha_before = eng.posterior_alpha.copy()
        apply_rlhf_modulation_to_bayesian(
            eng,
            {"rlhf_features": {"embedding_sim": 1.0, "lexical_score": 1.0}},
        )
        np.testing.assert_array_equal(eng.posterior_alpha, alpha_before)

    def test_modulation_shifts_alpha_when_trained_model_loaded(
        self, monkeypatch, tmp_path: Path
    ):
        monkeypatch.setenv("KERNEL_RLHF_MODULATE_BAYESIAN", "1")
        monkeypatch.setenv("KERNEL_RLHF_ARTIFACTS_PATH", str(tmp_path))

        model = RewardModel()
        fv = LabeledExample(
            id="x",
            features=model.extract_features(0.9, 0.1, 0.5, False, 1),
            human_label="blocked",
        ).features
        examples = [
            LabeledExample(id="a", features=fv, human_label="blocked"),
            LabeledExample(
                id="b",
                features=model.extract_features(0.1, 0.9, 0.5, False, 0),
                human_label="benign",
            ),
        ]
        model.train(examples, max_steps=80, learning_rate=0.05)
        artifact = tmp_path / "reward_model.json"
        model.save(artifact)
        assert artifact.is_file()

        reset_rlhf_reward_model_cache()

        eng = BayesianInferenceEngine()
        alpha0 = eng.posterior_alpha.copy()
        apply_rlhf_modulation_to_bayesian(
            eng,
            {"rlhf_features": {"embedding_sim": 0.95, "lexical_score": 0.05}},
        )
        assert not np.allclose(eng.posterior_alpha, alpha0)

    @pytest.mark.asyncio
    async def test_async_bridge_offloads_sync_path(self, monkeypatch, tmp_path: Path):
        monkeypatch.setenv("KERNEL_RLHF_MODULATE_BAYESIAN", "1")
        monkeypatch.setenv("KERNEL_RLHF_ARTIFACTS_PATH", str(tmp_path))

        model = RewardModel()
        ex = LabeledExample(
            id="a",
            features=model.extract_features(0.5, 0.5, 0.5, False, 0),
            human_label="benign",
        )
        model.train([ex], max_steps=5, learning_rate=0.01)
        model.save(tmp_path / "reward_model.json")
        reset_rlhf_reward_model_cache()

        eng = BayesianInferenceEngine()
        before = eng.posterior_alpha.copy()
        assert asyncio.iscoroutinefunction(apply_rlhf_modulation_to_bayesian_async)
        await apply_rlhf_modulation_to_bayesian_async(
            eng,
            {"rlhf_features": {"embedding_sim": 0.8, "lexical_score": 0.2}},
        )
        assert asyncio.iscoroutinefunction(RewardModel.apredict)
        assert not np.allclose(eng.posterior_alpha, before) or np.any(
            before != eng.posterior_alpha
        )


def test_json_schema_reward_model_loads_via_bridge(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("KERNEL_RLHF_MODULATE_BAYESIAN", "1")
    monkeypatch.setenv("KERNEL_RLHF_ARTIFACTS_PATH", str(tmp_path))
    payload = {
        "model_type": "logistic",
        "is_trained": True,
        "weights": [0.1, -0.2, 0.3, 0.0, 0.05],
        "bias": -0.01,
        "training_history": [],
    }
    (tmp_path / "reward_model.json").write_text(json.dumps(payload), encoding="utf-8")
    reset_rlhf_reward_model_cache()

    eng = BayesianInferenceEngine()
    a0 = eng.posterior_alpha.copy()
    apply_rlhf_modulation_to_bayesian(
        eng,
        {
            "rlhf_features": {
                "embedding_sim": 0.6,
                "lexical_score": 0.4,
                "perception_confidence": 0.8,
                "is_ambiguous": False,
                "category_id": 0,
            }
        },
    )
    assert eng.posterior_alpha.shape == (3,)
    assert not np.array_equal(eng.posterior_alpha, a0)
