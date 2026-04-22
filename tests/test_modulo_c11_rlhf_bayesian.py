"""
Integration test for Module C.1.1: Async RLHF Prior Injection into Bayesian Engine.

Tests that:
1. RLHF reward scores correctly map to ethical poles
2. Confidence-weighted blending preserves Dirichlet structure
3. Posterior-driven and posterior-assisted modes respond correctly
4. Pole decision propagation to ExecutiveLobe remains coherent
"""

import asyncio

import numpy as np
import pytest
from src.modules.cognition.bayesian_engine import BayesianInferenceEngine, BayesianMode


class TestRLHFBayesianFusion:
    """Module C.1.1: RLHF Prior Injection."""

    def test_rlhf_safe_input_boosts_social_utilitarian(self):
        """Safe RLHF input (reward_score ~0) should boost social and utilitarian poles."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        initial_alpha = engine.posterior_alpha.copy()

        # Simulate safe input (reward_score=0.1)
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.1, confidence=0.8))

        # Posterior should shift toward social+utilitarian
        new_alpha = engine.posterior_alpha
        assert new_alpha[1] > initial_alpha[1], "Social pole should increase"
        assert new_alpha[2] > initial_alpha[2], "Utilitarian pole should increase"
        assert np.sum(new_alpha) > 0, "Posterior mass preserved"

    def test_rlhf_harmful_input_boosts_deontological(self):
        """Harmful RLHF input (reward_score ~1) should boost deontological (duty to refuse)."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        initial_alpha = engine.posterior_alpha.copy()

        # Simulate harmful input (reward_score=0.9)
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.9, confidence=0.9))

        new_alpha = engine.posterior_alpha
        assert new_alpha[0] > initial_alpha[0], "Deontological pole should increase"
        # Social and utilitarian may decrease
        assert np.sum(new_alpha) > 0, "Posterior mass preserved"

    def test_rlhf_ambiguous_input_maintains_balance(self):
        """Ambiguous RLHF input (reward_score ~0.5) should maintain balanced poles."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        initial_weights = engine.scorer.hypothesis_weights.copy()

        # Simulate ambiguous input (reward_score=0.5, low confidence)
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.5, confidence=0.2))

        new_weights = engine.scorer.hypothesis_weights
        # With low confidence and ambiguous score, change should be minimal
        change = np.abs(new_weights - initial_weights).sum()
        assert change < 0.1, f"Ambiguous input should cause minimal shift, got {change}"

    def test_confidence_weighted_modulation(self):
        """Higher confidence should result in stronger posterior shift."""
        engine_low = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        engine_high = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        initial_alpha_low = engine_low.posterior_alpha.copy()
        initial_alpha_high = engine_high.posterior_alpha.copy()

        # Same reward score, different confidence
        asyncio.run(engine_low.inject_rlhf_prior_async(reward_score=0.9, confidence=0.3))
        asyncio.run(engine_high.inject_rlhf_prior_async(reward_score=0.9, confidence=0.9))

        change_low = np.abs(engine_low.posterior_alpha - initial_alpha_low).sum()
        change_high = np.abs(engine_high.posterior_alpha - initial_alpha_high).sum()

        assert change_high > change_low, "High confidence should cause larger shift"

    def test_boundary_preservation_no_degeneration(self):
        """Alpha values should never go below 0.5 to prevent degeneration."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        # Apply multiple extreme RLHF injections
        for _ in range(5):
            asyncio.run(
                engine.inject_rlhf_prior_async(
                    reward_score=0.99, confidence=0.99, modulation_strength=1.0
                )
            )

        # All alphas should remain >= 0.5
        assert np.all(engine.posterior_alpha >= 0.5), (
            f"Alpha values {engine.posterior_alpha} below boundary"
        )
        assert np.sum(engine.posterior_alpha) > 0, "Posterior mass must be positive"

    def test_posterior_driven_mode_weight_sync(self):
        """POSTERIOR_DRIVEN mode should immediately sync weights after RLHF injection."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.8, confidence=0.8))

        # Weights should equal normalized alpha
        expected_weights = engine.posterior_alpha / np.sum(engine.posterior_alpha)
        actual_weights = engine.scorer.hypothesis_weights

        np.testing.assert_array_almost_equal(actual_weights, expected_weights, decimal=6)

    def test_posterior_assisted_mode_bounded_nudge(self):
        """POSTERIOR_ASSISTED mode should apply bounded nudge via _apply_assisted_nudge."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_ASSISTED)
        initial_weights = engine.scorer.hypothesis_weights.copy()

        # Inject strong RLHF signal
        asyncio.run(
            engine.inject_rlhf_prior_async(
                reward_score=0.95, confidence=0.95, modulation_strength=0.5
            )
        )

        new_weights = engine.scorer.hypothesis_weights
        change = np.abs(new_weights - initial_weights).sum()

        # Change should be moderate (bounded by 40% blend default in assisted mode)
        assert change > 0, "Assisted mode should apply some shift"
        assert change < 0.3, f"Assisted mode should bound shift, got {change}"

    def test_invalid_inputs_rejected(self):
        """Invalid reward_score or confidence values should be rejected."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        initial_alpha = engine.posterior_alpha.copy()

        # Out-of-range values
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=1.5, confidence=0.5))  # reward > 1
        asyncio.run(
            engine.inject_rlhf_prior_async(reward_score=0.5, confidence=1.5)
        )  # confidence > 1

        # Alpha should not have changed
        np.testing.assert_array_equal(engine.posterior_alpha, initial_alpha)

    def test_zero_confidence_has_no_effect(self):
        """Zero confidence RLHF input should have minimal effect."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        initial_alpha = engine.posterior_alpha.copy()

        # High reward score but zero confidence
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.99, confidence=0.0))

        # Alpha should be unchanged (confidence=0 → effective_strength=0)
        np.testing.assert_array_almost_equal(engine.posterior_alpha, initial_alpha, decimal=6)

    def test_pole_consistency_after_rlhf_injection(self):
        """After RLHF injection, pole consistency metric should remain valid."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        # Inject multiple RLHF signals
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.7, confidence=0.8))
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.3, confidence=0.6))
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.5, confidence=0.5))

        # Verify weights are valid probability distribution
        weights = engine.scorer.hypothesis_weights
        assert np.all(weights >= 0), "Weights should be non-negative"
        assert np.isclose(np.sum(weights), 1.0, atol=1e-6), "Weights should sum to 1"

    @pytest.mark.asyncio
    async def test_concurrent_rlhf_injections(self):
        """Multiple concurrent RLHF injections should not cause race conditions."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        # Run 10 concurrent injections
        tasks = [
            engine.inject_rlhf_prior_async(reward_score=np.random.random(), confidence=0.7)
            for _ in range(10)
        ]
        await asyncio.gather(*tasks)

        # Final state should be valid
        assert np.all(engine.posterior_alpha >= 0.5), "Alpha should respect boundary"
        assert np.isclose(np.sum(engine.scorer.hypothesis_weights), 1.0, atol=1e-6)

    def test_modulation_strength_parameter_effect(self):
        """Higher modulation_strength should cause larger posterior shift."""
        engine_weak = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
        engine_strong = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        initial_weak = engine_weak.posterior_alpha.copy()
        initial_strong = engine_strong.posterior_alpha.copy()

        asyncio.run(
            engine_weak.inject_rlhf_prior_async(
                reward_score=0.8, confidence=0.8, modulation_strength=0.05
            )
        )
        asyncio.run(
            engine_strong.inject_rlhf_prior_async(
                reward_score=0.8, confidence=0.8, modulation_strength=0.3
            )
        )

        change_weak = np.abs(engine_weak.posterior_alpha - initial_weak).sum()
        change_strong = np.abs(engine_strong.posterior_alpha - initial_strong).sum()

        assert change_strong > change_weak, "Stronger modulation should cause larger shift"


class TestRLHFPoleDecisionPropagation:
    """Validate that RLHF updates propagate correctly to decision layer."""

    def test_rlhf_updates_decision_weights(self):
        """RLHF-modulated weights should affect downstream scoring."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        # Mock candidate action for evaluation
        from src.modules.ethics.weighted_ethics_scorer import CandidateAction

        action = CandidateAction(
            name="Test Action",
            description="A test action to verify scoring",
            estimated_impact=0.6,
            confidence=0.8,
        )

        # Get baseline score
        initial_result = engine.evaluate([action])
        initial_score = initial_result.expected_impact

        # Inject RLHF that boosts deontological
        asyncio.run(engine.inject_rlhf_prior_async(reward_score=0.95, confidence=0.9))

        # Rescore with updated weights
        new_result = engine.evaluate([action])
        new_score = new_result.expected_impact

        # Score should change due to weight shift (deontological increased)
        assert initial_score != new_score, "RLHF injection should affect downstream scoring"

    def test_rlhf_maintains_pole_triad_coherence(self):
        """Pole decision triad (d, s, u) should maintain logical coherence under RLHF."""
        engine = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)

        # Get initial pole weights
        initial_poles = engine.current_weights_meta
        assert sum(initial_poles) > 0, "Poles should have non-zero sum"

        # Apply extreme RLHF shifts in sequence
        for reward in [0.1, 0.5, 0.9, 0.3, 0.7]:
            asyncio.run(engine.inject_rlhf_prior_async(reward_score=reward, confidence=0.8))

        final_poles = engine.current_weights_meta
        # All poles should remain positive and sum to ~1
        assert all(p >= 0 for p in final_poles), "All poles should be non-negative"
        assert np.isclose(sum(final_poles), 1.0, atol=0.01), "Poles should sum to ~1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
