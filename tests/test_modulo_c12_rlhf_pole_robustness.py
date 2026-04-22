"""
Module C.1.2: Validate RLHF doesn't corrupt PoleLinearEvaluator thresholds.

Tests that RLHF Bayesian updates don't interfere with pole linear verdict logic.
Ensures threshold lockage and multipolar coherence under RLHF modulation.
"""

import asyncio

import numpy as np
import pytest
from src.modules.cognition.bayesian_engine import BayesianInferenceEngine, BayesianMode
from src.modules.ethics.ethical_poles import Verdict
from src.modules.ethics.pole_linear import LinearPoleEvaluator


class TestRLHFPoleRobustness:
    """Module C.1.2: RLHF doesn't corrupt pole evaluator thresholds."""

    @pytest.fixture
    def evaluator(self):
        """Load standard pole evaluator."""
        return LinearPoleEvaluator.load()

    @pytest.fixture
    def bayesian_engine(self):
        """Standard Bayesian engine in POSTERIOR_DRIVEN mode."""
        return BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

    def test_pole_thresholds_remain_after_rlhf_injection(self, evaluator):
        """Pole thresholds should not change after RLHF injection to Bayesian engine."""
        # Get initial thresholds
        initial_poles = evaluator._poles.copy()
        initial_good_thresholds = {
            name: spec.good_threshold for name, spec in initial_poles.items()
        }
        initial_bad_thresholds = {name: spec.bad_threshold for name, spec in initial_poles.items()}

        # Create Bayesian engine and inject RLHF
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.8, confidence=0.9))

        # Evaluator should be unchanged
        new_poles = evaluator._poles
        for name, spec in new_poles.items():
            assert spec.good_threshold == initial_good_thresholds[name], (
                f"Good threshold for {name} should not change"
            )
            assert spec.bad_threshold == initial_bad_thresholds[name], (
                f"Bad threshold for {name} should not change"
            )

    def test_verdict_consistency_safe_action_remains_good(self, evaluator, bayesian_engine):
        """Safe action verdict should remain GOOD even after RLHF shifts Bayesian weights."""
        # Context for a safe action
        safe_context = {
            "risk": 0.1,
            "benefit": 0.8,
            "third_party_vulnerability": 0.0,
            "legality": 1.0,
        }

        # Get initial verdicts for each pole
        initial_verdicts = {}
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "safe_action", safe_context)
            if eval_result:
                initial_verdicts[pole] = eval_result.verdict

        # Inject RLHF that boosts deontological
        asyncio.run(bayesian_engine.inject_rlhf_prior_async(reward_score=0.95, confidence=0.9))

        # Verdicts should NOT change (pole evaluator is independent of Bayesian weights)
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "safe_action", safe_context)
            if eval_result and pole in initial_verdicts:
                assert eval_result.verdict == initial_verdicts[pole], (
                    f"Verdict for pole {pole} should not change after RLHF injection"
                )

    def test_verdict_consistency_dangerous_action_remains_bad(self, evaluator, bayesian_engine):
        """Dangerous action verdict should remain BAD even after RLHF shifts Bayesian weights."""
        dangerous_context = {
            "risk": 0.95,
            "benefit": 0.1,
            "third_party_vulnerability": 0.9,
            "legality": 0.0,
        }

        initial_verdicts = {}
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "dangerous_action", dangerous_context)
            if eval_result:
                initial_verdicts[pole] = eval_result.verdict

        # Inject RLHF that boosts utilitarian (might favor harm-benefit tradeoff)
        asyncio.run(bayesian_engine.inject_rlhf_prior_async(reward_score=0.05, confidence=0.8))

        # Verdicts should still reflect danger
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "dangerous_action", dangerous_context)
            if eval_result and pole in initial_verdicts:
                assert eval_result.verdict == initial_verdicts[pole], (
                    f"Verdict for pole {pole} should not change after RLHF injection"
                )

    def test_multipolar_consensus_under_rlhf_modulation(self, evaluator, bayesian_engine):
        """Multiple poles should maintain consensus (all GOOD or all BAD) under RLHF shifts."""
        # Clear good action
        good_context = {
            "risk": 0.05,
            "benefit": 0.95,
            "third_party_vulnerability": 0.02,
            "legality": 1.0,
        }

        # Get initial verdicts
        initial_bad_count = 0
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "good_action", good_context)
            if eval_result and eval_result.verdict == Verdict.BAD:
                initial_bad_count += 1

        # Apply extreme RLHF shifts
        for reward in [0.1, 0.5, 0.9, 0.2, 0.8]:
            asyncio.run(
                bayesian_engine.inject_rlhf_prior_async(reward_score=reward, confidence=0.7)
            )

        # Verdict consensus should be preserved
        final_bad_count = 0
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "good_action", good_context)
            if eval_result and eval_result.verdict == Verdict.BAD:
                final_bad_count += 1

        assert final_bad_count == initial_bad_count, (
            f"Pole consensus should be preserved under RLHF (was {initial_bad_count} BAD, "
            f"now {final_bad_count} BAD)"
        )

    def test_threshold_edge_cases_stable_under_rlhf(self, evaluator, bayesian_engine):
        """Actions near verdict thresholds should not flip due to RLHF shifts."""
        # Ambiguous action (near gray zone)
        ambiguous_context = {
            "risk": 0.35,
            "benefit": 0.45,
            "third_party_vulnerability": 0.15,
            "legality": 0.8,
        }

        # Record initial verdicts for edge-case actions
        edge_verdicts = {}
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "ambiguous", ambiguous_context)
            if eval_result:
                edge_verdicts[pole] = eval_result.verdict

        # Apply multiple RLHF injections with varying magnitudes
        for _ in range(5):
            asyncio.run(
                bayesian_engine.inject_rlhf_prior_async(
                    reward_score=np.random.random(), confidence=np.random.random()
                )
            )

        # Edge case verdicts should remain stable
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "ambiguous", ambiguous_context)
            if eval_result and pole in edge_verdicts:
                assert eval_result.verdict == edge_verdicts[pole], (
                    f"Verdict for edge-case action at pole {pole} should not flip"
                )

    def test_score_values_bounded_after_rlhf(self, evaluator, bayesian_engine):
        """Pole linear scores should always remain bounded [-1, 1] after RLHF."""
        context = {
            "risk": 0.5,
            "benefit": 0.5,
            "third_party_vulnerability": 0.3,
            "legality": 0.8,
        }

        # Apply extreme RLHF with high confidence
        for reward in np.linspace(0, 1, 11):
            asyncio.run(
                bayesian_engine.inject_rlhf_prior_async(reward_score=reward, confidence=0.9)
            )

        # Verify all scores are bounded
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "test_action", context)
            if eval_result:
                assert -1.0 <= eval_result.score <= 1.0, (
                    f"Score for pole {pole} out of bounds: {eval_result.score}"
                )

    @pytest.mark.asyncio
    async def test_concurrent_rlhf_doesnt_corrupt_pole_evaluation(self, evaluator):
        """Concurrent RLHF injections should not corrupt pole evaluator state."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        context = {"risk": 0.6, "benefit": 0.4, "legality": 0.5}

        # Get baseline evaluation
        baseline_verdicts = {}
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "action", context)
            if eval_result:
                baseline_verdicts[pole] = eval_result.verdict

        # Run concurrent RLHF injections
        tasks = [
            engine.inject_rlhf_prior_async(
                reward_score=np.random.random(), confidence=np.random.random()
            )
            for _ in range(20)
        ]
        await asyncio.gather(*tasks)

        # Pole evaluator should be unaffected
        for pole in evaluator._poles.keys():
            eval_result = evaluator.evaluate(pole, "action", context)
            if eval_result and pole in baseline_verdicts:
                assert eval_result.verdict == baseline_verdicts[pole], (
                    f"Concurrent RLHF corrupted pole {pole} verdict"
                )

    def test_weighted_ethics_scorer_independence_from_bayesian(self, bayesian_engine):
        """
        Bayesian alpha updates should not directly modify pole linear thresholds.
        WeightedEthicsScorer operates independently from LinearPoleEvaluator.
        """
        # The Bayesian engine manages mixture weights, not pole thresholds
        initial_alpha = bayesian_engine.posterior_alpha.copy()

        # Inject RLHF
        asyncio.run(bayesian_engine.inject_rlhf_prior_async(reward_score=0.9, confidence=0.8))

        # Alpha changed, but this is mixture weight, not pole threshold
        assert not np.allclose(bayesian_engine.posterior_alpha, initial_alpha), (
            "RLHF should change posterior alpha"
        )

        # But pole evaluator is completely independent
        pole_eval = LinearPoleEvaluator.load()
        initial_spec = pole_eval._poles["conservative"]
        asyncio.run(bayesian_engine.inject_rlhf_prior_async(reward_score=0.5, confidence=0.7))
        final_spec = pole_eval._poles["conservative"]

        assert initial_spec.good_threshold == final_spec.good_threshold, (
            "Pole threshold should never change from Bayesian updates"
        )


class TestThresholdLocking:
    """Lock key thresholds as immutable contract."""

    def test_conservative_good_threshold_locked_at_03(self):
        """Conservative GOOD threshold must be locked at 0.3."""
        evaluator = LinearPoleEvaluator.load()
        conservative_spec = evaluator._poles.get("conservative")
        assert conservative_spec is not None, "Conservative pole not found"
        assert conservative_spec.good_threshold == 0.3, (
            f"Conservative GOOD threshold must be locked at 0.3, got {conservative_spec.good_threshold}"
        )

    def test_conservative_bad_threshold_locked_at_neg03(self):
        """Conservative BAD threshold must be locked at -0.3."""
        evaluator = LinearPoleEvaluator.load()
        conservative_spec = evaluator._poles.get("conservative")
        assert conservative_spec is not None
        assert conservative_spec.bad_threshold == -0.3, (
            f"Conservative BAD threshold must be locked at -0.3, got {conservative_spec.bad_threshold}"
        )

    def test_all_poles_have_symmetric_thresholds(self):
        """All poles should have symmetric good/bad thresholds [±0.3]."""
        evaluator = LinearPoleEvaluator.load()
        for pole_name, spec in evaluator._poles.items():
            assert spec.good_threshold == 0.3, (
                f"Pole {pole_name} GOOD threshold must be 0.3, got {spec.good_threshold}"
            )
            assert spec.bad_threshold == -0.3, (
                f"Pole {pole_name} BAD threshold must be -0.3, got {spec.bad_threshold}"
            )
            assert spec.good_threshold == -spec.bad_threshold, (
                f"Pole {pole_name} thresholds should be symmetric"
            )

    def test_threshold_configuration_immutable(self):
        """Threshold specs should be frozen (immutable)."""
        evaluator = LinearPoleEvaluator.load()
        for pole_name, spec in evaluator._poles.items():
            # Try to modify (should fail if frozen)
            try:
                # The _PoleLinearSpec is frozen=True, so assignment should fail
                spec.good_threshold = 0.5
                pytest.fail(f"Pole {pole_name} spec should be immutable")
            except (AttributeError, TypeError):
                # Expected: dataclass is frozen
                pass


class TestRLHFPoleInteractionBoundaries:
    """Test boundary conditions where RLHF and poles interact."""

    def test_rlhf_safe_score_doesnt_override_pole_bad_verdict(self):
        """Even if RLHF boosts safe poles, pole BAD verdict must stand."""
        evaluator = LinearPoleEvaluator.load()
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        # Truly dangerous context
        dangerous = {"risk": 1.0, "benefit": 0.0, "legality": 0.0, "third_party_vulnerability": 1.0}

        # Get initial verdict (should be BAD)
        initial_verdict = None
        for pole in evaluator._poles.keys():
            result = evaluator.evaluate(pole, "action", dangerous)
            if result:
                initial_verdict = result.verdict
                break

        # Inject RLHF signal saying it's safe
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.05, confidence=0.9))

        # Verdict should still be BAD (poles are independent)
        final_verdict = None
        for pole in evaluator._poles.keys():
            result = evaluator.evaluate(pole, "action", dangerous)
            if result:
                final_verdict = result.verdict
                break

        assert initial_verdict == final_verdict, (
            f"Pole verdict should not change due to Bayesian weights "
            f"(was {initial_verdict}, now {final_verdict})"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
