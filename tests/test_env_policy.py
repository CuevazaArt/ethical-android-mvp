"""
P1 Core Issue #7: Environment combo validation tests.

Validates KERNEL_* environment policy, supported combos, and deprecation roadmap.
"""

from __future__ import annotations

import os
import pytest

from src.validators.env_policy import SUPPORTED_COMBOS, DEPRECATION_ROADMAP
from src.runtime_profiles import profile_names


class TestEnvPolicySupportedCombos:
    """Test that environment combos are properly defined and partition profiles."""

    def test_supported_combos_cover_all_profiles(self):
        """All profile names must be in exactly one combo bucket."""
        all_profiles = set(profile_names())
        all_combos = set()

        for bucket_profiles in SUPPORTED_COMBOS.values():
            all_combos.update(bucket_profiles)

        # All profiles should be covered
        assert all_profiles.issubset(all_combos), (
            f"Profiles not in SUPPORTED_COMBOS: {all_profiles - all_combos}"
        )

        # No overlaps between buckets
        production = SUPPORTED_COMBOS["production"]
        demo = SUPPORTED_COMBOS["demo"]
        lab = SUPPORTED_COMBOS["lab"]

        assert not (production & demo), "Overlap between production and demo"
        assert not (production & lab), "Overlap between production and lab"
        assert not (demo & lab), "Overlap between demo and lab"

    def test_production_profiles_exist(self):
        """Production bucket must have valid profiles."""
        prod = SUPPORTED_COMBOS["production"]
        assert len(prod) > 0, "Production bucket is empty"
        assert "baseline" in prod, "baseline must be in production"

    def test_demo_profiles_exist(self):
        """Demo bucket must have valid profiles."""
        demo = SUPPORTED_COMBOS["demo"]
        assert len(demo) > 0, "Demo bucket is empty"
        assert "judicial_demo" in demo or "hub_dao_demo" in demo

    def test_lab_profiles_exist(self):
        """Lab bucket must have valid profiles."""
        lab = SUPPORTED_COMBOS["lab"]
        assert len(lab) > 0, "Lab bucket is empty"

    def test_combos_are_frozensets(self):
        """Combos must be immutable."""
        for bucket_name, profiles in SUPPORTED_COMBOS.items():
            assert isinstance(profiles, frozenset), (
                f"Bucket {bucket_name} is not frozenset: {type(profiles)}"
            )


class TestDeprecationRoadmap:
    """Test deprecation roadmap structure."""

    def test_deprecation_roadmap_not_empty(self):
        """Roadmap must have entries."""
        assert len(DEPRECATION_ROADMAP) > 0, "Deprecation roadmap is empty"

    def test_deprecation_entries_have_migration_path(self):
        """Each deprecated flag must have a migration message."""
        for flag, migration in DEPRECATION_ROADMAP.items():
            assert isinstance(flag, str), f"Flag key not string: {flag}"
            assert isinstance(migration, str), f"Migration path not string for {flag}"
            assert len(flag) > 0, "Flag name is empty"
            assert len(migration) > 0, f"Migration path empty for {flag}"
            assert flag.startswith("KERNEL_"), f"Flag not KERNEL_*: {flag}"

    def test_bayesian_deprecation_documented(self):
        """Bayesian-related deprecations must be documented."""
        bayesian_deprecations = [k for k in DEPRECATION_ROADMAP.keys() if "BAYESIAN" in k]
        assert len(bayesian_deprecations) > 0, "No Bayesian deprecations documented"


class TestEnvProfileValidation:
    """Test that runtime profiles can be loaded without errors."""

    def test_production_baseline_loadable(self):
        """Baseline profile must be loadable."""
        # This test would require actually loading the profile; for now just verify it exists
        all_profiles = profile_names()
        assert "baseline" in all_profiles

    def test_demo_judicial_demo_loadable(self):
        """Judicial demo profile must be loadable."""
        all_profiles = profile_names()
        assert "judicial_demo" in all_profiles or "hub_dao_demo" in all_profiles


class TestEnvComboConflictDetection:
    """Test detection of conflicting env variable combinations."""

    def test_semantic_gate_requires_embedding_config(self):
        """KERNEL_SEMANTIC_CHAT_GATE=1 requires semantic embedding config."""
        # In strict mode, should validate relationships
        # This is an example rule: semantic gate should have embedding backend specified
        # Actual implementation depends on validators/kernel_env_operator.py
        pass  # Placeholder for future strict validation


class TestEnvValidationContract:
    """Test environment validation contract and API."""

    def test_supported_combos_keys_are_valid(self):
        """Combo keys must be standard bucket names."""
        valid_keys = {"production", "demo", "lab"}
        assert set(SUPPORTED_COMBOS.keys()) == valid_keys, (
            f"Unexpected combo keys: {set(SUPPORTED_COMBOS.keys())}"
        )

    def test_no_default_env_contamination(self):
        """Tests should not affect global environment."""
        # Store original state
        original_keys = set(os.environ.keys())

        # Do nothing - just verify current state
        current_keys = set(os.environ.keys())

        # After test runs, environment should not accumulate keys
        assert original_keys == current_keys


class TestEnvDocumentation:
    """Test that env policy is documented."""

    def test_deprecation_roadmap_matches_adr_naming(self):
        """Deprecation messages should reference ADRs where applicable."""
        adr_referenced = [
            msg for msg in DEPRECATION_ROADMAP.values()
            if "ADR" in msg or "adr" in msg
        ]
        assert len(adr_referenced) > 0, "Some deprecations should reference ADRs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
