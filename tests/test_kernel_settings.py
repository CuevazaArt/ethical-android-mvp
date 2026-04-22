"""
KernelSettings consolidation tests.

Tests that the unified KernelSettings model correctly:
- Loads environment variables with proper type coercion
- Validates threshold ordering (θ_allow < θ_block)
- Provides startup inventory
- Exposes operator-safe public dictionary
"""

import pytest
from src.settings.kernel_settings import KernelSettings


class TestKernelSettingsDefaults:
    """Verify default values match engineering priors."""

    def test_default_values(self):
        """Settings should have sensible defaults when env is empty."""
        # Create with no env vars (relies on Field defaults)
        # Note: from_env() reads os.environ, so we use direct instantiation
        settings = KernelSettings()

        assert settings.chat_host == "127.0.0.1"
        assert settings.chat_port == 8765
        assert settings.kernel_variability is True
        assert settings.kernel_seed is None
        assert settings.kernel_semantic_chat_sim_block_threshold == 0.82
        assert settings.kernel_semantic_chat_sim_allow_threshold == 0.45
        assert settings.kernel_chat_async_llm_http is False
        assert settings.llm_provider == "anthropic"
        assert settings.llm_model == "claude-opus"

    def test_semantic_thresholds_default(self):
        """Semantic thresholds should match documented engineering priors."""
        settings = KernelSettings()
        assert settings.kernel_semantic_chat_sim_block_threshold == 0.82
        assert settings.kernel_semantic_chat_sim_allow_threshold == 0.45


class TestKernelSettingsEnvLoading:
    """Verify environment variable loading and type coercion."""

    def test_load_from_env_string_values(self, monkeypatch):
        """String env vars should be coerced to correct types."""
        monkeypatch.setenv("CHAT_HOST", "0.0.0.0")
        monkeypatch.setenv("CHAT_PORT", "9999")
        monkeypatch.setenv("KERNEL_VARIABILITY", "0")
        monkeypatch.setenv("KERNEL_METRICS", "1")

        settings = KernelSettings.from_env()

        assert settings.chat_host == "0.0.0.0"
        assert settings.chat_port == 9999
        assert settings.kernel_variability is False
        assert settings.kernel_metrics is True

    def test_load_float_values(self, monkeypatch):
        """Float env vars should parse correctly."""
        monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD", "0.90")
        monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD", "0.50")
        monkeypatch.setenv("LLM_TEMPERATURE", "0.3")

        settings = KernelSettings.from_env()

        assert settings.kernel_semantic_chat_sim_block_threshold == 0.90
        assert settings.kernel_semantic_chat_sim_allow_threshold == 0.50
        assert settings.llm_temperature == 0.3

    def test_load_int_values(self, monkeypatch):
        """Integer env vars should parse correctly."""
        monkeypatch.setenv("KERNEL_BAYESIAN_N_SAMPLES", "10000")
        monkeypatch.setenv("KERNEL_CHAT_THREADPOOL_WORKERS", "8")
        monkeypatch.setenv("KERNEL_NARRATIVE_MAX_EPISODES", "50")

        settings = KernelSettings.from_env()

        assert settings.kernel_bayesian_n_samples == 10000
        assert settings.kernel_chat_threadpool_workers == 8
        assert settings.kernel_narrative_max_episodes == 50

    def test_load_timeout_as_float(self, monkeypatch):
        """Turn timeout should parse as float (seconds)."""
        monkeypatch.setenv("KERNEL_CHAT_TURN_TIMEOUT", "30.5")

        settings = KernelSettings.from_env()

        assert settings.kernel_chat_turn_timeout_seconds == 30.5
        assert isinstance(settings.kernel_chat_turn_timeout_seconds, float)

    def test_unset_optional_fields(self, monkeypatch):
        """Unset optional fields should be None."""
        monkeypatch.delenv("KERNEL_SEED", raising=False)
        monkeypatch.delenv("LLM_MODE", raising=False)
        monkeypatch.delenv("KERNEL_LIGHTHOUSE_KB_PATH", raising=False)

        settings = KernelSettings.from_env()

        assert settings.kernel_seed is None
        assert settings.llm_mode is None
        assert settings.kernel_lighthouse_kb_path is None

    def test_truthy_false_values(self, monkeypatch):
        """Various false representations should work."""
        monkeypatch.setenv("KERNEL_VARIABILITY", "false")
        monkeypatch.setenv("KERNEL_GOVERNANCE_ENABLED", "no")
        monkeypatch.setenv("KERNEL_NARRATIVE_ENABLED", "off")

        settings = KernelSettings.from_env()

        assert settings.kernel_variability is False
        assert settings.kernel_governance_enabled is False
        assert settings.kernel_narrative_enabled is False

    def test_truthy_true_values(self, monkeypatch):
        """Various true representations should work."""
        monkeypatch.setenv("KERNEL_METRICS", "yes")
        monkeypatch.setenv("KERNEL_CHAT_JSON_OFFLOAD", "on")
        monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_ENABLED", "true")

        settings = KernelSettings.from_env()

        assert settings.kernel_metrics is True
        assert settings.kernel_chat_json_offload is True
        assert settings.kernel_semantic_chat_enabled is True


class TestSemanticThresholdValidation:
    """Verify semantic threshold ordering constraint."""

    def test_threshold_ordering_valid(self):
        """Valid ordering: allow < block should pass."""
        settings = KernelSettings(
            kernel_semantic_chat_sim_allow_threshold=0.40,
            kernel_semantic_chat_sim_block_threshold=0.85,
        )
        assert settings.kernel_semantic_chat_sim_allow_threshold == 0.40
        assert settings.kernel_semantic_chat_sim_block_threshold == 0.85

    def test_threshold_ordering_invalid_equal(self):
        """Equal thresholds should fail."""
        with pytest.raises(ValueError, match="allow_threshold .* must be <"):
            KernelSettings(
                kernel_semantic_chat_sim_allow_threshold=0.50,
                kernel_semantic_chat_sim_block_threshold=0.50,
            )

    def test_threshold_ordering_invalid_allow_greater(self):
        """allow > block should fail."""
        with pytest.raises(ValueError, match="allow_threshold .* must be <"):
            KernelSettings(
                kernel_semantic_chat_sim_allow_threshold=0.90,
                kernel_semantic_chat_sim_block_threshold=0.80,
            )

    def test_threshold_ordering_default_valid(self):
        """Default thresholds should satisfy ordering constraint."""
        settings = KernelSettings()
        assert (
            settings.kernel_semantic_chat_sim_allow_threshold
            < settings.kernel_semantic_chat_sim_block_threshold
        )


class TestTemperatureValidation:
    """Verify LLM temperature bounds."""

    def test_temperature_valid_range(self):
        """Temperature in [0.0, 1.0] should be valid."""
        settings = KernelSettings(llm_temperature=0.5)
        assert settings.llm_temperature == 0.5

    def test_temperature_min_bound(self):
        """Temperature at 0.0 should be valid."""
        settings = KernelSettings(llm_temperature=0.0)
        assert settings.llm_temperature == 0.0

    def test_temperature_max_bound(self):
        """Temperature at 1.0 should be valid."""
        settings = KernelSettings(llm_temperature=1.0)
        assert settings.llm_temperature == 1.0

    def test_temperature_below_min(self):
        """Temperature below 0.0 should fail."""
        with pytest.raises(ValueError):
            KernelSettings(llm_temperature=-0.1)

    def test_temperature_above_max(self):
        """Temperature above 1.0 should fail."""
        with pytest.raises(ValueError):
            KernelSettings(llm_temperature=1.5)


class TestStartupReport:
    """Verify startup configuration inventory."""

    def test_startup_report_format(self):
        """Startup report should be human-readable and include all sections."""
        settings = KernelSettings()
        report = settings.startup_report()

        assert "KERNEL STARTUP CONFIGURATION" in report
        assert "Chat Server:" in report
        assert "Kernel Core:" in report
        assert "Bayesian Inference:" in report
        assert "Semantic Gate:" in report
        assert "Async / Chat Orchestration:" in report
        assert "LLM Configuration:" in report
        assert "Governance:" in report
        assert "Narrative System:" in report
        assert "Perception:" in report

    def test_startup_report_includes_values(self):
        """Startup report should include actual configuration values."""
        settings = KernelSettings(
            chat_host="0.0.0.0", chat_port=9999, kernel_variability=False, llm_model="claude-sonnet"
        )
        report = settings.startup_report()

        assert "0.0.0.0" in report
        assert "9999" in report
        assert "False" in report
        assert "claude-sonnet" in report

    def test_startup_report_not_empty(self):
        """Startup report should have substantial content."""
        settings = KernelSettings()
        report = settings.startup_report()

        assert len(report) > 500  # Rough content check


class TestPublicDictionary:
    """Verify operator-safe public dictionary."""

    def test_public_dict_includes_key_fields(self):
        """model_dump_public should include important operator-facing fields."""
        settings = KernelSettings()
        public = settings.model_dump_public()

        assert "chat_host" in public
        assert "chat_port" in public
        assert "kernel_variability" in public
        assert "kernel_semantic_chat_sim_block_threshold" in public
        assert "kernel_semantic_chat_sim_allow_threshold" in public
        assert "llm_provider" in public
        assert "llm_model" in public

    def test_public_dict_values_match_settings(self):
        """Public dict values should match actual settings."""
        settings = KernelSettings(
            chat_host="0.0.0.0", kernel_variability=False, kernel_metrics=True
        )
        public = settings.model_dump_public()

        assert public["chat_host"] == "0.0.0.0"
        assert public["kernel_variability"] is False
        assert public["kernel_metrics"] is True


class TestAsyncSettings:
    """Verify async/chat orchestration configuration."""

    def test_async_llm_http_disabled_by_default(self):
        """Async LLM HTTP should be opt-in (default off)."""
        settings = KernelSettings()
        assert settings.kernel_chat_async_llm_http is False

    def test_async_llm_http_can_be_enabled(self, monkeypatch):
        """Async LLM HTTP should be configurable."""
        monkeypatch.setenv("KERNEL_CHAT_ASYNC_LLM_HTTP", "1")
        settings = KernelSettings.from_env()
        assert settings.kernel_chat_async_llm_http is True

    def test_threadpool_workers_default_zero(self):
        """Threadpool workers default to 0 (use anyio default)."""
        settings = KernelSettings()
        assert settings.kernel_chat_threadpool_workers == 0

    def test_threadpool_workers_configurable(self, monkeypatch):
        """Threadpool workers should be configurable."""
        monkeypatch.setenv("KERNEL_CHAT_THREADPOOL_WORKERS", "8")
        settings = KernelSettings.from_env()
        assert settings.kernel_chat_threadpool_workers == 8

    def test_turn_timeout_optional(self):
        """Turn timeout should be optional (None = unlimited)."""
        settings = KernelSettings()
        assert settings.kernel_chat_turn_timeout_seconds is None

    def test_turn_timeout_configurable(self, monkeypatch):
        """Turn timeout should be configurable in seconds."""
        monkeypatch.setenv("KERNEL_CHAT_TURN_TIMEOUT", "60")
        settings = KernelSettings.from_env()
        assert settings.kernel_chat_turn_timeout_seconds == 60.0


class TestGovernanceSettings:
    """Verify governance configuration."""

    def test_governance_enabled_by_default(self):
        """Governance should be enabled by default."""
        settings = KernelSettings()
        assert settings.kernel_governance_enabled is True

    def test_l0_strict_mode_disabled_by_default(self):
        """L0 strict mode should be opt-in."""
        settings = KernelSettings()
        assert settings.kernel_l0_strict_mode is False

    def test_judicial_escalation_disabled_by_default(self):
        """Judicial escalation should be opt-in."""
        settings = KernelSettings()
        assert settings.kernel_judicial_escalation is False


class TestValidationMode:
    """Verify environment validation configuration."""

    def test_validation_mode_strict_by_default(self, monkeypatch):
        """Validation mode should default to strict."""
        monkeypatch.delenv("KERNEL_ENV_VALIDATION", raising=False)
        settings = KernelSettings.from_env()
        assert settings.kernel_env_validation == "strict"

    def test_validation_mode_warn(self, monkeypatch):
        """Validation mode warn should be configurable."""
        monkeypatch.setenv("KERNEL_ENV_VALIDATION", "warn")
        settings = KernelSettings.from_env()
        assert settings.kernel_env_validation == "warn"

    def test_validation_mode_off(self, monkeypatch):
        """Validation mode off should be configurable."""
        monkeypatch.setenv("KERNEL_ENV_VALIDATION", "off")
        settings = KernelSettings.from_env()
        assert settings.kernel_env_validation == "off"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
