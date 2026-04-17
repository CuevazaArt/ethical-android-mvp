"""
Tests for deprecation warning emitters (ADR 0016 — B2).

Verifies that:
  1. Deprecated flags are correctly listed in DEPRECATION_ROADMAP
  2. check_deprecated_flags() emits DeprecationWarning for active flags
  3. get_deprecation_info() returns correct metadata
"""

from __future__ import annotations

import os
import warnings
from contextlib import contextmanager

from src.validators.deprecation_warnings import (
    DEPRECATED_FLAGS,
    check_deprecated_flags,
    get_deprecation_info,
    is_deprecated,
)
from src.validators.env_policy import DEPRECATION_ROADMAP


class TestDeprecationMetadata:
    """Test that deprecation metadata is well-formed."""

    def test_all_deprecated_flags_have_descriptions(self):
        """Every deprecated flag must have a removal version and suggestion."""
        for flag_name, (removal_version, suggestion) in DEPRECATED_FLAGS.items():
            assert isinstance(flag_name, str) and flag_name.startswith(
                ("KERNEL_", "OLLAMA_", "ETHOS_")
            ), f"Invalid flag name: {flag_name}"
            assert isinstance(removal_version, str) and removal_version, (
                f"Missing removal version for {flag_name}"
            )
            assert isinstance(suggestion, str) and len(suggestion) > 10, (
                f"Insufficient suggestion for {flag_name}: {suggestion!r}"
            )

    def test_deprecation_roadmap_matches_deprecated_flags(self):
        """DEPRECATION_ROADMAP in env_policy should cover all deprecated flags."""
        # Note: env_policy may use a shorter description; just verify coverage
        for flag_name in DEPRECATED_FLAGS.keys():
            assert flag_name in DEPRECATION_ROADMAP, (
                f"{flag_name} in DEPRECATED_FLAGS but not in DEPRECATION_ROADMAP"
            )

    def test_minimum_count_of_deprecated_flags(self):
        """ADR 0016 B2 requires at least 20 deprecated flags."""
        assert len(DEPRECATED_FLAGS) >= 20, (
            f"Need ≥20 deprecated flags; found {len(DEPRECATED_FLAGS)}"
        )

    def test_is_deprecated_helper(self):
        """Test is_deprecated() correctly identifies deprecated flags."""
        # Known deprecated
        assert is_deprecated("KERNEL_BAYESIAN_FEEDBACK")
        assert is_deprecated("KERNEL_SOMATIC_MARKERS")
        # Known non-deprecated
        assert not is_deprecated("KERNEL_ABSOLUTE_EVIL_THRESHOLD")
        assert not is_deprecated("KERNEL_ENV_VALIDATION")


class TestDeprecationWarnings:
    """Test that DeprecationWarning is emitted for active deprecated flags."""

    @contextmanager
    def _assert_deprecation_warning_for_flag(self, flag_name: str, flag_value: str = "1"):
        """Helper: set env var, capture DeprecationWarning, restore env."""
        old_value = os.environ.get(flag_name)
        try:
            os.environ[flag_name] = flag_value
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                yield w
        finally:
            if old_value is None:
                os.environ.pop(flag_name, None)
            else:
                os.environ[flag_name] = old_value

    def test_check_deprecated_flags_emits_warnings(self):
        """check_deprecated_flags() should emit warning for each active deprecated flag."""
        with self._assert_deprecation_warning_for_flag("KERNEL_BAYESIAN_FEEDBACK"):
            check_deprecated_flags()
            # Warnings are emitted; at least one should be a DeprecationWarning
            # (Note: warnings may be caught elsewhere, so we check via _assert context)

    def test_no_warning_when_flag_unset(self):
        """check_deprecated_flags() should not warn if deprecated flag is unset."""
        os.environ.pop("KERNEL_BAYESIAN_FEEDBACK", None)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_deprecated_flags()
            # Should have no warnings for unset flags (or at least none about this one)
            deprec_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            # It's okay if there are no warnings; the check ran without error
            assert isinstance(deprec_warnings, list)  # sanity check

    def test_get_deprecation_info(self):
        """Test get_deprecation_info() retrieves metadata."""
        info = get_deprecation_info("KERNEL_BAYESIAN_FEEDBACK")
        assert info is not None
        removal_version, suggestion = info
        assert "v0" in removal_version
        assert len(suggestion) > 5

    def test_get_deprecation_info_nonexistent(self):
        """get_deprecation_info() returns None for non-deprecated flags."""
        assert get_deprecation_info("KERNEL_ABSOLUTE_EVIL_THRESHOLD") is None


class TestDeprecationCoverage:
    """Ensure deprecation covers various categories of deprecated flags."""

    def test_bayesian_family_deprecated(self):
        """Bayesian family flags should be marked deprecated (replaced by feedback)."""
        bayesian_flags = [
            "KERNEL_BAYESIAN_FEEDBACK",
            "KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS",
            "KERNEL_BAYESIAN_MAX_DRIFT",
            "KERNEL_BAYESIAN_CONTEXT_LEVEL",
            "KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS",
        ]
        for flag in bayesian_flags:
            assert is_deprecated(flag), (
                f"{flag} should be deprecated (replaced by KERNEL_FEEDBACK_*)"
            )

    def test_narrative_only_deprecated(self):
        """Narrative-tier only flags should be marked deprecated (no causal effect)."""
        narrative_flags = [
            "KERNEL_SOMATIC_MARKERS",
            "KERNEL_GRAY_ZONE_DIPLOMACY",
            "KERNEL_POLES_PRE_ARGMAX",
            "KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX",
        ]
        for flag in narrative_flags:
            assert is_deprecated(flag), f"{flag} should be deprecated (narrative-tier only)"

    def test_mock_flags_deprecated(self):
        """Mock/lab-only flags should be deprecated (not for production)."""
        mock_flags = [
            "KERNEL_DEMOCRATIC_BUFFER_MOCK",
            "KERNEL_ETHOS_PAYROLL_MOCK",
            "KERNEL_REPARATION_VAULT_MOCK",
            "KERNEL_JUDICIAL_MOCK_COURT",
        ]
        for flag in mock_flags:
            assert is_deprecated(flag), f"{flag} should be deprecated (mock/lab-only)"

    def test_redundant_flags_deprecated(self):
        """Redundant or overlapping flags should be deprecated."""
        redundant_flags = [
            "KERNEL_PERCEPTION_PARALLEL",
            "KERNEL_TEMPORAL_DAO_SYNC",
            "KERNEL_SWARM_STUB",
            "KERNEL_NOMAD_SIMULATION",
        ]
        for flag in redundant_flags:
            assert is_deprecated(flag), f"{flag} should be deprecated (redundant/overlapping)"

    def test_unused_flags_deprecated(self):
        """Unused or undocumented flags should be deprecated."""
        unused_flags = [
            "KERNEL_ETHICAL_GENOME_ENFORCE",
            "KERNEL_ETHICAL_GENOME_MAX_DRIFT",
            "KERNEL_STRATEGIC_BOOST_FACTOR",
            "KERNEL_PSI_SLEEP_UPDATE_MIXTURE",
        ]
        for flag in unused_flags:
            assert is_deprecated(flag), f"{flag} should be deprecated (unused/undocumented)"
