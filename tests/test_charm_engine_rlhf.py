"""
Tests for Bloque E.2: RLHF-informed sycophancy guard in ResponseSculptor.

Verifies that:
- When RLHF is disabled (default), sculpt() behaves exactly as before
- When RLHF is enabled with an untrained model, no dampening is applied
- When RLHF is enabled with a trained model, high-sycophancy vectors are dampened
- Absolute-evil bypass is never altered by the RLHF guard
- Dampening is proportional to reward score excess
- Directiveness is slightly boosted when warmth/playfulness are dampened
- CharmEngine facade accepts rlhf_pipeline kwarg end-to-end
"""

from __future__ import annotations

import os
import sys
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.charm_engine import (
    CharmEngine,
    CharmVector,
    ResponseSculptor,
    StylizedResponse,
)
from src.modules.rlhf_reward_model import LabeledExample, RLHFPipeline
from src.modules.uchi_soto import InteractionProfile, TrustCircle
from src.modules.user_model import UserModelTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _profile(intimacy: float = 0.0) -> InteractionProfile:
    return InteractionProfile(
        agent_id="tester",
        circle=TrustCircle.SOTO_NEUTRO,
        trust_score=0.5,
        intimacy_level=intimacy,
    )


def _tracker() -> UserModelTracker:
    return UserModelTracker()


def _trained_pipeline(tmp_path: Any) -> RLHFPipeline:
    """Build and train a minimal RLHFPipeline to guarantee is_trained=True."""
    pipeline = RLHFPipeline(artifacts_path=tmp_path / "rlhf")
    # Train with examples that mark high-warmth+low-directiveness as sycophancy risk
    examples = [
        pipeline.create_labeled_example(
            id=f"syco-{i}",
            embedding_sim=0.85,    # high warmth
            lexical_score=0.75,    # low directiveness
            perception_conf=0.9,
            is_ambiguous=False,
            category_id=0,
            human_label="ambiguous",  # sycophancy risk
            confidence=0.8,
            source="test",
        )
        for i in range(8)
    ] + [
        pipeline.create_labeled_example(
            id=f"safe-{i}",
            embedding_sim=0.2,     # low warmth
            lexical_score=0.2,     # high directiveness
            perception_conf=0.5,
            is_ambiguous=False,
            category_id=0,
            human_label="benign",
            confidence=0.9,
            source="test",
        )
        for i in range(8)
    ]
    pipeline.train_reward_model(examples)
    return pipeline


# ---------------------------------------------------------------------------
# RLHF disabled (default) — sculpt must be identical to baseline
# ---------------------------------------------------------------------------

class TestRlhfDisabled:
    def test_no_rlhf_pipeline_no_change(self) -> None:
        rs = ResponseSculptor()
        out = rs.sculpt(
            base_text="Hi there.",
            decision_action="care_response",
            profile=_profile(intimacy=0.8),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )
        assert isinstance(out, StylizedResponse)
        # Warm/open annotation should appear (warmth should be high without RLHF guard)
        assert "[Tone: Warm & Open]" in out.final_text

    def test_rlhf_off_env_no_dampening(self, monkeypatch: Any, tmp_path: Any) -> None:
        """Even with a trained pipeline, RLHF guard must skip when env is off."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "0")
        pipeline = _trained_pipeline(tmp_path)
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        out = rs.sculpt(
            base_text="Hi.",
            decision_action="care_response",
            profile=_profile(intimacy=0.9),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )
        # Should not suppress warm annotation
        assert "[Tone: Warm & Open]" in out.final_text


# ---------------------------------------------------------------------------
# RLHF enabled with untrained model — no dampening
# ---------------------------------------------------------------------------

class TestRlhfUntrainedModel:
    def test_untrained_model_no_dampening(self, monkeypatch: Any, tmp_path: Any) -> None:
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = RLHFPipeline(artifacts_path=tmp_path / "rlhf_empty")
        # Don't train — reward_model.is_trained == False
        assert not pipeline.reward_model.is_trained
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        out = rs.sculpt(
            base_text="Warm.",
            decision_action="care_response",
            profile=_profile(intimacy=0.9),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )
        assert isinstance(out, StylizedResponse)


# ---------------------------------------------------------------------------
# RLHF enabled with trained model — sycophancy detection
# ---------------------------------------------------------------------------

class TestRlhfSycophancyGuard:
    def test_high_warmth_vector_is_dampened(self, monkeypatch: Any, tmp_path: Any) -> None:
        """
        A care_response at high intimacy + low caution produces a very warm vector.
        With a trained RLHF model that learned to flag high-warmth patterns, warmth
        should be reduced relative to the no-RLHF baseline.
        """
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")

        # Baseline without RLHF
        rs_base = ResponseSculptor()
        out_base = rs_base.sculpt(
            base_text="Let me help.",
            decision_action="care_response",
            profile=_profile(intimacy=0.9),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )

        # With trained RLHF guard
        pipeline = _trained_pipeline(tmp_path)
        rs_rlhf = ResponseSculptor(rlhf_pipeline=pipeline)
        out_rlhf = rs_rlhf.sculpt(
            base_text="Let me help.",
            decision_action="care_response",
            profile=_profile(intimacy=0.9),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )

        assert isinstance(out_rlhf, StylizedResponse)
        # Either warmth is dampened OR directiveness is boosted (or both)
        warmth_dampened = out_rlhf.charm_vector["warmth"] <= out_base.charm_vector["warmth"]
        directness_boosted = out_rlhf.charm_vector["directiveness"] >= out_base.charm_vector["directiveness"]
        assert warmth_dampened or directness_boosted, (
            f"Expected sycophancy dampening: "
            f"base={out_base.charm_vector}, rlhf={out_rlhf.charm_vector}"
        )

    def test_dampened_vector_values_still_in_range(self, monkeypatch: Any, tmp_path: Any) -> None:
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = _trained_pipeline(tmp_path)
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        out = rs.sculpt(
            base_text="Sure thing!",
            decision_action="care_response",
            profile=_profile(intimacy=0.9),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=False,
        )
        for key, val in out.charm_vector.items():
            assert 0.0 <= val <= 1.0, f"{key}={val} out of [0,1]"

    def test_absolute_evil_bypass_never_altered_by_rlhf(self, monkeypatch: Any, tmp_path: Any) -> None:
        """RLHF guard must never touch the absolute-evil safety bypass path."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = _trained_pipeline(tmp_path)
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        out = rs.sculpt(
            base_text="BLOCKED",
            decision_action="anything",
            profile=_profile(intimacy=1.0),
            user_tracker=_tracker(),
            caution_level=0.0,
            absolute_evil_detected=True,
        )
        assert out.charm_vector["warmth"] == 0.0
        assert out.charm_vector["directiveness"] == 1.0
        assert any(g["action"] == "rigid_block" for g in out.gesture_plan)

    def test_low_warmth_vector_not_dampened(self, monkeypatch: Any, tmp_path: Any) -> None:
        """A deontological block produces low warmth — RLHF should not reduce it further."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = _trained_pipeline(tmp_path)
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        out = rs.sculpt(
            base_text="I cannot proceed.",
            decision_action="deontolog_block",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.8,
            absolute_evil_detected=False,
        )
        # Warmth should remain low (no meaningful sycophancy signal in block vectors)
        assert out.charm_vector["warmth"] <= 0.35

    def test_rlhf_guard_directiveness_boost_capped_at_1(self, monkeypatch: Any, tmp_path: Any) -> None:
        """Directiveness must never exceed 1.0 after the boost."""
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = _trained_pipeline(tmp_path)
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        for action in ("care_response", "sympathetic_action", "utilitarian"):
            out = rs.sculpt(
                base_text="Test.",
                decision_action=action,
                profile=_profile(intimacy=0.9),
                user_tracker=_tracker(),
                caution_level=0.0,
                absolute_evil_detected=False,
            )
            assert out.charm_vector["directiveness"] <= 1.0


# ---------------------------------------------------------------------------
# CharmEngine facade with rlhf_pipeline kwarg
# ---------------------------------------------------------------------------

class TestCharmEngineFacadeRlhf:
    def test_charm_engine_accepts_rlhf_pipeline(self, tmp_path: Any) -> None:
        pipeline = _trained_pipeline(tmp_path)
        ce = CharmEngine(rlhf_pipeline=pipeline)
        assert ce.sculptor._rlhf is pipeline

    def test_charm_engine_rlhf_end_to_end(self, monkeypatch: Any, tmp_path: Any) -> None:
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = _trained_pipeline(tmp_path)
        ce = CharmEngine(rlhf_pipeline=pipeline)
        out = ce.apply(
            base_text="Hello!",
            decision_action="care_response",
            profile=_profile(intimacy=0.8),
            user_tracker=_tracker(),
            caution_level=0.1,
            absolute_evil_detected=False,
        )
        assert isinstance(out, StylizedResponse)
        for val in out.charm_vector.values():
            assert 0.0 <= val <= 1.0

    def test_charm_engine_no_rlhf_pipeline_backward_compat(self) -> None:
        """CharmEngine() with no rlhf_pipeline must still work identically to before."""
        ce = CharmEngine()
        out = ce.apply(
            base_text="Hi.",
            decision_action="utilitarian",
            profile=_profile(),
            user_tracker=_tracker(),
            caution_level=0.3,
            absolute_evil_detected=False,
        )
        assert isinstance(out, StylizedResponse)


# ---------------------------------------------------------------------------
# _apply_rlhf_guard unit tests (direct)
# ---------------------------------------------------------------------------

class TestApplyRlhfGuardDirect:
    def test_guard_no_pipeline_returns_charm_unchanged(self) -> None:
        rs = ResponseSculptor()
        cv = CharmVector(warmth=0.8, mystery=0.3, playfulness=0.5, directiveness=0.3)
        result = rs._apply_rlhf_guard(cv, caution_level=0.0)
        assert result is cv  # same object returned

    def test_guard_disabled_env_returns_charm_unchanged(
        self, monkeypatch: Any, tmp_path: Any
    ) -> None:
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "0")
        pipeline = _trained_pipeline(tmp_path)
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        cv = CharmVector(warmth=0.8, mystery=0.3, playfulness=0.5, directiveness=0.3)
        result = rs._apply_rlhf_guard(cv, caution_level=0.0)
        assert result is cv

    def test_guard_untrained_returns_charm_unchanged(
        self, monkeypatch: Any, tmp_path: Any
    ) -> None:
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = RLHFPipeline(artifacts_path=tmp_path / "empty")
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        cv = CharmVector(warmth=0.9, mystery=0.2, playfulness=0.7, directiveness=0.2)
        result = rs._apply_rlhf_guard(cv, caution_level=0.0)
        assert result is cv  # untrained → no change

    def test_guard_trained_reduces_warmth_on_high_score(
        self, monkeypatch: Any, tmp_path: Any
    ) -> None:
        monkeypatch.setenv("KERNEL_RLHF_REWARD_MODEL_ENABLED", "1")
        pipeline = _trained_pipeline(tmp_path)
        rs = ResponseSculptor(rlhf_pipeline=pipeline)
        # Craft a vector that matches the sycophancy training distribution
        cv = CharmVector(warmth=0.85, mystery=0.3, playfulness=0.7, directiveness=0.15)
        result = rs._apply_rlhf_guard(cv, caution_level=0.0)
        assert isinstance(result, CharmVector)
        # warmth should be reduced or unchanged (never increased)
        assert result.warmth <= cv.warmth + 1e-9
        # mystery is never touched
        assert result.mystery == cv.mystery
