"""
Semantic threshold validation tests — θ_block / θ_allow boundary checks.

Tests that the semantic chat gate correctly classifies inputs into allow/ambiguous/block zones
and that threshold values match documented engineering priors.

Reference: PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md
"""

import pytest
from src.modules.safety.semantic_chat_gate import (
    DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
    DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
    classify_semantic_zone,
)


class TestSemanticThresholdDefaults:
    """Verify documented threshold values are unchanged."""

    def test_block_threshold_is_documented_value(self):
        """θ_block should be 0.82 per engineering priors."""
        assert DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD == 0.82

    def test_allow_threshold_is_documented_value(self):
        """θ_allow should be 0.45 per engineering priors."""
        assert DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD == 0.45

    def test_thresholds_ordered_correctly(self):
        """θ_allow < θ_block (mandatory invariant)."""
        assert DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD < DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD


class TestSemanticZoneClassification:
    """Verify zone boundaries work as documented."""

    def test_allow_zone_below_theta_allow(self):
        """Similarity < θ_allow → 'allow' zone."""
        zone = classify_semantic_zone(
            best_sim=0.40,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "allow"

    def test_allow_zone_at_theta_allow_boundary(self):
        """Similarity == θ_allow → 'allow' zone (inclusive lower boundary)."""
        zone = classify_semantic_zone(
            best_sim=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "allow"

    def test_ambiguous_zone_between_thresholds(self):
        """θ_allow < similarity < θ_block → 'ambiguous' zone."""
        zone = classify_semantic_zone(
            best_sim=0.60,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "ambiguous"

    def test_block_zone_at_theta_block_boundary(self):
        """Similarity == θ_block → 'block' zone (inclusive upper boundary)."""
        zone = classify_semantic_zone(
            best_sim=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "block"

    def test_block_zone_above_theta_block(self):
        """Similarity > θ_block → 'block' zone."""
        zone = classify_semantic_zone(
            best_sim=0.95,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "block"

    def test_zone_classification_complete_spectrum(self):
        """Verify zone classification across full [0, 1] spectrum."""
        test_cases = [
            (0.00, "allow"),
            (0.20, "allow"),
            (0.45, "allow"),  # At boundary
            (0.46, "ambiguous"),
            (0.60, "ambiguous"),
            (0.81, "ambiguous"),
            (0.82, "block"),  # At boundary
            (0.90, "block"),
            (1.00, "block"),
        ]
        for similarity, expected_zone in test_cases:
            zone = classify_semantic_zone(
                best_sim=similarity,
                theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
                theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
            )
            assert zone == expected_zone, (
                f"similarity={similarity}: expected {expected_zone}, got {zone}"
            )


class TestSemanticZoneEdgeCases:
    """Edge cases and boundary behavior."""

    def test_perfect_match_is_blocked(self):
        """Similarity 1.0 should always be blocked (exact match to harmful anchor)."""
        zone = classify_semantic_zone(
            best_sim=1.0,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "block"

    def test_zero_similarity_is_allowed(self):
        """Similarity 0.0 should always be allowed (completely unrelated)."""
        zone = classify_semantic_zone(
            best_sim=0.0,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "allow"

    def test_custom_threshold_pair(self):
        """Verify classification works with custom (non-default) thresholds."""
        custom_block = 0.80
        custom_allow = 0.50
        zone = classify_semantic_zone(
            best_sim=0.65,
            theta_block=custom_block,
            theta_allow=custom_allow,
        )
        assert zone == "ambiguous"

    def test_custom_thresholds_respected(self):
        """Verify custom thresholds override defaults in classification."""
        zone_default = classify_semantic_zone(
            best_sim=0.85,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        zone_custom = classify_semantic_zone(
            best_sim=0.85,
            theta_block=0.90,
            theta_allow=0.40,
        )
        assert zone_default == "block"
        assert zone_custom == "ambiguous"


class TestSemanticZoneFail_SafeProperties:
    """Verify fail-safe behavior per engineering priors."""

    def test_ambiguous_band_exists(self):
        """Ambiguous band must exist between θ_allow and θ_block."""
        ambiguous_lower = DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD + 0.01
        ambiguous_upper = DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD - 0.01

        zone_lower = classify_semantic_zone(
            best_sim=ambiguous_lower,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        zone_upper = classify_semantic_zone(
            best_sim=ambiguous_upper,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone_lower == "ambiguous"
        assert zone_upper == "ambiguous"

    def test_narrow_ambiguous_band_forces_arbiter_calls(self):
        """Narrow band (0.82 - 0.45 = 0.37) forces routing to LLM arbiter when enabled."""
        band_width = DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD - DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD
        # Engineering prior: band should be wide enough to catch paraphrases
        # but narrow enough to force escalation on borderline cases
        assert 0.30 <= band_width <= 0.50, (
            f"Ambiguous band width {band_width} outside engineering prior range [0.30, 0.50]"
        )

    def test_block_threshold_conservative_on_false_negatives(self):
        """θ_block = 0.82 is conservative (blocks at high similarity, reduces FN risk)."""
        # Engineering prior: high threshold → prefer false positives over false negatives
        assert DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD >= 0.80

    def test_allow_threshold_conservative_on_false_positives(self):
        """θ_allow = 0.45 is conservative (requires clear dissimilarity to auto-allow)."""
        # Engineering prior: low threshold → prefer false negatives over false positives
        assert DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD <= 0.50


class TestSemanticZoneOperatorDocumentation:
    """Verify that zone behavior matches operator documentation."""

    def test_zone_names_documented(self):
        """Verify zone names match PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md."""
        documented_zones = {"allow", "ambiguous", "block"}
        test_similarities = [0.0, 0.50, 0.82, 1.0]
        for sim in test_similarities:
            zone = classify_semantic_zone(
                best_sim=sim,
                theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
                theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
            )
            assert zone in documented_zones, f"Undocumented zone: {zone}"

    def test_allow_zone_requires_clear_dissimilarity(self):
        """Allow zone (sim < 0.45) means input is clearly different from harmful anchors."""
        zone = classify_semantic_zone(
            best_sim=0.40,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "allow"
        # Rationale: 0.40 cosine sim is ~24° angle → quite different

    def test_block_zone_requires_high_similarity(self):
        """Block zone (sim >= 0.82) means input is very similar to harmful anchors."""
        zone = classify_semantic_zone(
            best_sim=0.82,
            theta_block=DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
            theta_allow=DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
        )
        assert zone == "block"
        # Rationale: 0.82 cosine sim is ~35° angle → very close match


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
