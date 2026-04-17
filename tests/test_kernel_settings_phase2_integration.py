"""
KernelSettings Phase 2 integration tests.

Tests that EthicalKernel correctly:
- Uses KernelSettings for initialization
- Applies settings defaults to constructor parameters
- Maintains backward compatibility
- Logs startup configuration
"""

import pytest
import logging
from src.kernel import EthicalKernel
from src.settings.kernel_settings import KernelSettings


class TestKernelSettingsIntegration:
    """Verify EthicalKernel uses KernelSettings (Phase 2)."""

    def test_kernel_initializes_with_default_settings(self):
        """Kernel should initialize with default KernelSettings."""
        kernel = EthicalKernel()
        assert kernel.settings is not None
        assert isinstance(kernel.settings, KernelSettings)

    def test_kernel_accepts_settings_parameter(self):
        """Kernel should accept optional settings parameter."""
        custom_settings = KernelSettings(
            kernel_variability=False,
            llm_model="claude-sonnet"
        )
        kernel = EthicalKernel(settings=custom_settings)
        assert kernel.settings is custom_settings
        assert kernel.settings.kernel_variability is False
        assert kernel.settings.llm_model == "claude-sonnet"

    def test_kernel_settings_from_env(self, monkeypatch):
        """Kernel should load settings from environment variables."""
        monkeypatch.setenv("KERNEL_VARIABILITY", "0")
        monkeypatch.setenv("LLM_TEMPERATURE", "0.3")

        kernel = EthicalKernel()

        # Settings should have loaded from environment
        assert kernel.settings.kernel_variability is False
        assert kernel.settings.llm_temperature == 0.3

    def test_backward_compatibility_variability_param(self):
        """Old variability parameter should still work."""
        kernel = EthicalKernel(variability=False)
        # Internal variability state should be disabled
        assert kernel.var_engine._active is False

    def test_backward_compatibility_seed_param(self):
        """Old seed parameter should still work."""
        kernel = EthicalKernel(seed=42)
        # Seed should be applied to variability engine config
        assert kernel.var_engine.config.seed == 42

    def test_parameter_override_settings(self):
        """Constructor parameters should override settings."""
        kernel = EthicalKernel(
            variability=False,
            seed=123
        )
        # Parameters should take precedence
        assert kernel.var_engine._active is False
        assert kernel.var_engine.config.seed == 123

    def test_settings_applied_to_variability_engine(self):
        """Settings variability value should be applied to var_engine."""
        settings = KernelSettings(kernel_variability=False)
        kernel = EthicalKernel(settings=settings)
        assert kernel.var_engine._active is False

    def test_settings_applied_to_bayesian_engine(self):
        """Settings LLM mode should affect Bayesian engine."""
        kernel = EthicalKernel()
        assert kernel.bayesian is not None

    def test_startup_log_includes_configuration(self, caplog):
        """Startup log should include settings configuration."""
        with caplog.at_level(logging.INFO):
            kernel = EthicalKernel()

        # Check for startup configuration in logs
        assert any("KERNEL STARTUP CONFIGURATION" in record.message for record in caplog.records)

    def test_multiple_kernels_independent_settings(self):
        """Multiple kernel instances should have independent settings."""
        settings1 = KernelSettings(kernel_variability=True)
        settings2 = KernelSettings(kernel_variability=False)

        kernel1 = EthicalKernel(settings=settings1)
        kernel2 = EthicalKernel(settings=settings2)

        assert kernel1.settings.kernel_variability is True
        assert kernel2.settings.kernel_variability is False

    def test_settings_accessible_for_operations(self):
        """Kernel should provide easy access to settings during operations."""
        settings = KernelSettings(
            kernel_semantic_chat_sim_block_threshold=0.85,
            kernel_semantic_chat_sim_allow_threshold=0.50
        )
        kernel = EthicalKernel(settings=settings)

        # Settings should be accessible for decision-making
        assert kernel.settings.kernel_semantic_chat_sim_block_threshold == 0.85
        assert kernel.settings.kernel_semantic_chat_sim_allow_threshold == 0.50

    def test_semantic_threshold_validation_through_kernel(self):
        """Semantic thresholds in kernel settings should be validated."""
        # Invalid threshold ordering should fail
        with pytest.raises(ValueError):
            settings = KernelSettings(
                kernel_semantic_chat_sim_allow_threshold=0.80,
                kernel_semantic_chat_sim_block_threshold=0.70
            )
            EthicalKernel(settings=settings)


class TestKernelSettingsBackwardCompatibility:
    """Verify old env var reading still works (deprecation grace period)."""

    def test_kernel_accepts_llm_mode_override(self):
        """LLM mode parameter should override settings."""
        kernel = EthicalKernel(llm_mode="offline")
        assert kernel.llm is not None

    def test_kernel_accepts_component_overrides(self):
        """KernelComponentOverrides should still work."""
        from src.kernel import KernelComponentOverrides
        from src.modules.absolute_evil import AbsoluteEvilDetector

        overrides = KernelComponentOverrides(
            absolute_evil=AbsoluteEvilDetector()
        )
        kernel = EthicalKernel(components=overrides)
        assert kernel.absolute_evil is not None

    def test_kernel_accepts_checkpoint_persistence(self):
        """Checkpoint persistence parameter should still work."""
        kernel = EthicalKernel(checkpoint_persistence=None)
        assert kernel.checkpoint_persistence is None

    def test_kernel_settings_coexist_with_legacy_params(self):
        """Settings and legacy parameters should coexist peacefully."""
        settings = KernelSettings(kernel_variability=True)
        kernel = EthicalKernel(
            settings=settings,
            variability=False,  # This should override settings
            seed=42
        )
        # Legacy parameter should win
        assert kernel.var_engine._active is False


class TestKernelSettingsPublicAPI:
    """Verify kernel exposes settings for downstream code."""

    def test_kernel_settings_attribute_accessible(self):
        """kernel.settings should be publicly accessible."""
        kernel = EthicalKernel()
        assert hasattr(kernel, "settings")
        assert isinstance(kernel.settings, KernelSettings)

    def test_can_access_configuration_via_kernel(self):
        """Code should be able to read config from kernel.settings."""
        kernel = EthicalKernel()

        # Downstream code patterns
        llm_provider = kernel.settings.llm_provider
        turn_timeout = kernel.settings.kernel_chat_turn_timeout_seconds
        governance_enabled = kernel.settings.kernel_governance_enabled

        assert llm_provider is not None
        assert isinstance(turn_timeout, (float, type(None)))
        assert isinstance(governance_enabled, bool)

    def test_settings_dump_public_accessible(self):
        """kernel.settings.model_dump_public() should work."""
        kernel = EthicalKernel()
        public_config = kernel.settings.model_dump_public()

        assert isinstance(public_config, dict)
        assert "llm_provider" in public_config
        assert "kernel_variability" in public_config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
