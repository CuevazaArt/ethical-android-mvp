"""
Unified kernel + chat configuration model.

Single source of truth for all KERNEL_* and CHAT_* environment variables.
Consolidates fragmented settings from:
  - chat_settings.py (chat server config)
  - validators/kernel_public_env.py (kernel policy)
  - validators/env_policy.py (combo validation rules)
  - validators/kernel_env_operator.py (operator wrapper)
  - modules/env_coherence_check.py (runtime validation)

See: docs/PYDANTIC_SETTINGS_CONSOLIDATION_PLAN.md
"""

from __future__ import annotations

import logging
import os
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


def _env_str(name: str, default: str) -> str:
    v = os.environ.get(name, "").strip()
    return v if v else default


def _env_optional_str(name: str) -> str | None:
    v = os.environ.get(name, "").strip()
    return v if v else None


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_optional_positive_float(name: str) -> float | None:
    """Unset/empty or non-positive → no limit; otherwise as float."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        v = float(raw)
    except ValueError:
        return None
    return v if v > 0.0 else None


def _env_truthy(name: str, *, default_true: bool = True) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default_true
    if default_true:
        return raw not in ("0", "false", "no", "off")
    return raw in ("1", "true", "yes", "on")


class KernelSettings(BaseModel):
    """
    Unified kernel + chat configuration (Phase 1 implementation).

    Environment variables are parsed at startup and validated for consistency.
    All KERNEL_* and CHAT_* settings in one model with auto-documentation.
    """

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    # ════ CHAT SERVER ════
    chat_host: str = Field(
        default="0.0.0.0",
        description="CHAT_HOST — WebSocket/ASGI bind address.",
    )
    chat_port: int = Field(
        default=8765,
        ge=1,
        le=65535,
        description="CHAT_PORT — WebSocket/ASGI port.",
    )

    # ════ KERNEL CORE ════
    kernel_mode: str = Field(
        default="default",
        description="KERNEL_MODE — execution mode (default, demo, research).",
    )
    kernel_variability: bool = Field(
        default=True,
        description="KERNEL_VARIABILITY — enable Monte Carlo sampling (default on).",
    )
    kernel_seed: int | None = Field(
        default=None,
        description="KERNEL_SEED — random seed for reproducibility (None = random).",
    )
    kernel_api_docs: bool = Field(
        default=False,
        description="KERNEL_API_DOCS — expose OpenAPI /docs, /redoc when true.",
    )

    # ════ BAYESIAN INFERENCE ════
    kernel_bayesian_n_samples: int = Field(
        default=5000,
        description="KERNEL_BAYESIAN_N_SAMPLES — BMA Monte Carlo sample count.",
    )
    kernel_bayesian_prior_alpha: float = Field(
        default=1.0,
        description="KERNEL_BAYESIAN_PRIOR_ALPHA — Dirichlet prior concentration.",
    )

    # ════ SEMANTIC GATE ════
    kernel_semantic_chat_enabled: bool = Field(
        default=True,
        description="KERNEL_SEMANTIC_CHAT_ENABLED — enable semantic MalAbs layer.",
    )
    kernel_semantic_chat_sim_block_threshold: float = Field(
        default=0.82,
        description="KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD — cosine similarity block threshold (θ_block).",
    )
    kernel_semantic_chat_sim_allow_threshold: float = Field(
        default=0.45,
        description="KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD — cosine similarity allow threshold (θ_allow).",
    )

    # ════ ASYNC / CHAT ORCHESTRATION ════
    kernel_nomad_chat_timeout_seconds: float = Field(
        default=5.0,
        description=(
            "KERNEL_NOMAD_CHAT_TIMEOUT — max seconds to wait for a Nomad chat_text turn; "
            "default 5 s. Keeps the Nomad bridge zero-friction by bounding limbic latency."
        ),
    )
    kernel_chat_turn_timeout_seconds: float | None = Field(
        default=30.0,
        description=(
            "KERNEL_CHAT_TURN_TIMEOUT — max seconds for one WebSocket chat turn (async wait); "
            "default 30 s. Set to 0 or a negative value to disable. "
            "For Nomad LAN use-cases keep ≤30 s to prevent limbic-latency stalls."
        ),
    )
    kernel_chat_threadpool_workers: int = Field(
        default=0,
        ge=0,
        description="KERNEL_CHAT_THREADPOOL_WORKERS — dedicated thread pool size (0 = use anyio default).",
    )
    kernel_chat_async_llm_http: bool = Field(
        default=False,
        description=(
            "KERNEL_CHAT_ASYNC_LLM_HTTP — use async HTTP for LLM calls (ADR 0002). "
            "Default off; enables asyncio.wait_for cancellation."
        ),
    )
    kernel_chat_json_offload: bool = Field(
        default=True,
        description=(
            "KERNEL_CHAT_JSON_OFFLOAD — build WebSocket JSON in worker thread (default on). "
            "Set to 0 for debugging only."
        ),
    )
    kernel_chat_include_malabs_trace: bool = Field(
        default=True,
        description="KERNEL_CHAT_INCLUDE_MALABS_TRACE — include malabs_trace in WebSocket JSON.",
    )

    # ════ LLM LAYER ════
    llm_mode: str | None = Field(
        default=None,
        description="LLM_MODE — optional override for resolve_llm_mode().",
    )
    llm_provider: str = Field(
        default="anthropic",
        description="LLM_PROVIDER — LLM provider (anthropic, ollama, etc).",
    )
    llm_model: str = Field(
        default="claude-opus",
        description="LLM_MODEL — LLM model name.",
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="LLM_TEMPERATURE — LLM temperature (0.0-1.0).",
    )
    llm_max_tokens: int = Field(
        default=2000,
        ge=1,
        description="LLM_MAX_TOKENS — max tokens in LLM response.",
    )

    # ════ GOVERNANCE ════
    kernel_governance_enabled: bool = Field(
        default=True,
        description="KERNEL_GOVERNANCE_ENABLED — enable governance features (DAO, audit).",
    )
    kernel_l0_strict_mode: bool = Field(
        default=False,
        description="KERNEL_L0_STRICT_MODE — L0 supremacy governance strict enforcement.",
    )
    kernel_judicial_escalation: bool = Field(
        default=False,
        description="KERNEL_JUDICIAL_ESCALATION — enable judicial escalation mechanism.",
    )
    kernel_judicial_mock_court: bool = Field(
        default=False,
        description="KERNEL_JUDICIAL_MOCK_COURT — use mock court for testing.",
    )
    kernel_moral_hub_dao_vote: bool = Field(
        default=False,
        description="KERNEL_MORAL_HUB_DAO_VOTE — enable DAO voting on moral issues.",
    )

    # ════ NARRATIVE ════
    kernel_narrative_enabled: bool = Field(
        default=True,
        description="KERNEL_NARRATIVE_ENABLED — enable narrative memory system.",
    )
    kernel_narrative_max_episodes: int = Field(
        default=100,
        description="KERNEL_NARRATIVE_MAX_EPISODES — maximum episodes to retain.",
    )

    # ════ PERCEPTION ════
    kernel_perception_backend: str = Field(
        default="local",
        description="KERNEL_PERCEPTION_BACKEND — perception backend (local, ollama, remote).",
    )
    kernel_perception_uncertainty_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="KERNEL_PERCEPTION_UNCERTAINTY_THRESHOLD — confidence threshold for escalation.",
    )

    # ════ ENVIRONMENT VALIDATION ════
    kernel_env_validation: Literal["off", "warn", "strict"] = Field(
        default="strict",
        description="KERNEL_ENV_VALIDATION — validation mode (strict, warn, off).",
    )

    # ════ OPTIONAL FEATURES ════
    kernel_semantic_chat_gate_disabled: bool = Field(
        default=False,
        description="KERNEL_SEMANTIC_CHAT_GATE_DISABLED — explicitly disable semantic gate.",
    )
    kernel_chat_include_reality_verification: bool = Field(
        default=False,
        description="KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION — enable reality check layer.",
    )
    kernel_lighthouse_kb_path: str | None = Field(
        default=None,
        description="KERNEL_LIGHTHOUSE_KB_PATH — optional path for lighthouse knowledge base.",
    )
    ethos_runtime_profile: str | None = Field(
        default=None,
        description="ETHOS_RUNTIME_PROFILE — nominal runtime profile bundle name.",
    )

    # ════ METRICS ════
    kernel_metrics: bool = Field(
        default=False,
        description="KERNEL_METRICS — enable Prometheus metrics export.",
    )

    # ════ AUDIO OUROBOROS ════
    kernel_audio_ouroboros_enabled: bool = Field(
        default=False,
        description="KERNEL_AUDIO_OUROBOROS_ENABLED — enable STT->Reasoning->TTS loop.",
    )
    kernel_whisper_model: str = Field(
        default="base",
        description="KERNEL_WHISPER_MODEL — Whisper model size.",
    )

    @classmethod
    def from_env(cls) -> KernelSettings:
        """Load settings from environment variables."""
        return cls(
            # Chat server
            chat_host=_env_str("CHAT_HOST", "0.0.0.0"),
            chat_port=_env_int("CHAT_PORT", 8765),
            # Kernel core
            kernel_mode=_env_str("KERNEL_MODE", "default"),
            kernel_variability=_env_truthy("KERNEL_VARIABILITY", default_true=True),
            kernel_seed=_env_int("KERNEL_SEED", -1) if _env_int("KERNEL_SEED", -1) >= 0 else None,
            kernel_api_docs=_env_truthy("KERNEL_API_DOCS", default_true=False),
            # Bayesian
            kernel_bayesian_n_samples=_env_int("KERNEL_BAYESIAN_N_SAMPLES", 5000),
            kernel_bayesian_prior_alpha=_env_float("KERNEL_BAYESIAN_PRIOR_ALPHA", 1.0),
            # Semantic gate
            kernel_semantic_chat_enabled=_env_truthy("KERNEL_SEMANTIC_CHAT_ENABLED", default_true=True),
            kernel_semantic_chat_sim_block_threshold=_env_float(
                "KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD", 0.82
            ),
            kernel_semantic_chat_sim_allow_threshold=_env_float(
                "KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD", 0.45
            ),
            # Async/chat
            kernel_nomad_chat_timeout_seconds=max(0.1, _env_float("KERNEL_NOMAD_CHAT_TIMEOUT", 5.0)),
            kernel_chat_turn_timeout_seconds=_env_optional_positive_float("KERNEL_CHAT_TURN_TIMEOUT") or 30.0,
            kernel_chat_threadpool_workers=max(0, _env_int("KERNEL_CHAT_THREADPOOL_WORKERS", 0)),
            kernel_chat_async_llm_http=_env_truthy("KERNEL_CHAT_ASYNC_LLM_HTTP", default_true=False),
            kernel_chat_json_offload=_env_truthy("KERNEL_CHAT_JSON_OFFLOAD", default_true=True),
            kernel_chat_include_malabs_trace=_env_truthy("KERNEL_CHAT_INCLUDE_MALABS_TRACE", default_true=True),
            # LLM
            llm_mode=_env_optional_str("LLM_MODE"),
            llm_provider=_env_str("LLM_PROVIDER", "anthropic"),
            llm_model=_env_str("LLM_MODEL", "claude-opus"),
            llm_temperature=_env_float("LLM_TEMPERATURE", 0.7),
            llm_max_tokens=_env_int("LLM_MAX_TOKENS", 2000),
            # Governance
            kernel_governance_enabled=_env_truthy("KERNEL_GOVERNANCE_ENABLED", default_true=True),
            kernel_l0_strict_mode=_env_truthy("KERNEL_L0_STRICT_MODE", default_true=False),
            kernel_judicial_escalation=_env_truthy("KERNEL_JUDICIAL_ESCALATION", default_true=False),
            kernel_judicial_mock_court=_env_truthy("KERNEL_JUDICIAL_MOCK_COURT", default_true=False),
            kernel_moral_hub_dao_vote=_env_truthy("KERNEL_MORAL_HUB_DAO_VOTE", default_true=False),
            # Narrative
            kernel_narrative_enabled=_env_truthy("KERNEL_NARRATIVE_ENABLED", default_true=True),
            kernel_narrative_max_episodes=_env_int("KERNEL_NARRATIVE_MAX_EPISODES", 100),
            # Perception
            kernel_perception_backend=_env_str("KERNEL_PERCEPTION_BACKEND", "local"),
            kernel_perception_uncertainty_threshold=_env_float(
                "KERNEL_PERCEPTION_UNCERTAINTY_THRESHOLD", 0.6
            ),
            # Validation
            kernel_env_validation=_parse_env_validation_mode(),
            # Optional features
            kernel_semantic_chat_gate_disabled=_env_truthy("KERNEL_SEMANTIC_CHAT_GATE_DISABLED", default_true=False),
            kernel_chat_include_reality_verification=_env_truthy(
                "KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION", default_true=False
            ),
            kernel_lighthouse_kb_path=_env_optional_str("KERNEL_LIGHTHOUSE_KB_PATH"),
            ethos_runtime_profile=_env_optional_str("ETHOS_RUNTIME_PROFILE"),
            # Metrics
            kernel_metrics=_env_truthy("KERNEL_METRICS", default_true=False),
            # Audio Ouroboros
            kernel_audio_ouroboros_enabled=_env_truthy("KERNEL_AUDIO_OUROBOROS_ENABLED", default_true=False),
            kernel_whisper_model=_env_str("KERNEL_WHISPER_MODEL", "base"),
        )

    @field_validator("kernel_semantic_chat_sim_allow_threshold")
    @classmethod
    def validate_allow_threshold_ordering(cls, v: float, info) -> float:
        """θ_allow must be < θ_block (mandatory invariant)."""
        data = info.data
        if "kernel_semantic_chat_sim_block_threshold" in data:
            block = data["kernel_semantic_chat_sim_block_threshold"]
            if v >= block:
                raise ValueError(
                    f"allow_threshold ({v}) must be < block_threshold ({block})"
                )
        return v

    def startup_report(self) -> str:
        """Generate human-readable startup configuration inventory."""
        return f"""
════ KERNEL STARTUP CONFIGURATION ════
Chat Server:
  Host: {self.chat_host}
  Port: {self.chat_port}

Kernel Core:
  Mode: {self.kernel_mode}
  Variability: {self.kernel_variability}
  Seed: {self.kernel_seed}
  API Docs: {self.kernel_api_docs}

Bayesian Inference:
  N Samples: {self.kernel_bayesian_n_samples}
  Prior Alpha: {self.kernel_bayesian_prior_alpha}

Semantic Gate:
  Enabled: {self.kernel_semantic_chat_enabled}
  Block Threshold (θ_block): {self.kernel_semantic_chat_sim_block_threshold}
  Allow Threshold (θ_allow): {self.kernel_semantic_chat_sim_allow_threshold}
  Gate Disabled: {self.kernel_semantic_chat_gate_disabled}

Async / Chat Orchestration:
  Turn Timeout: {self.kernel_chat_turn_timeout_seconds}s
  Threadpool Workers: {self.kernel_chat_threadpool_workers}
  Async LLM HTTP: {self.kernel_chat_async_llm_http}
  JSON Offload: {self.kernel_chat_json_offload}
  Include MalAbs Trace: {self.kernel_chat_include_malabs_trace}

LLM Configuration:
  Provider: {self.llm_provider}
  Model: {self.llm_model}
  Temperature: {self.llm_temperature}
  Max Tokens: {self.llm_max_tokens}
  Mode Override: {self.llm_mode}

Governance:
  Enabled: {self.kernel_governance_enabled}
  L0 Strict Mode: {self.kernel_l0_strict_mode}
  Judicial Escalation: {self.kernel_judicial_escalation}
  Moral Hub DAO Vote: {self.kernel_moral_hub_dao_vote}

Narrative System:
  Enabled: {self.kernel_narrative_enabled}
  Max Episodes: {self.kernel_narrative_max_episodes}

Perception:
  Backend: {self.kernel_perception_backend}
  Uncertainty Threshold: {self.kernel_perception_uncertainty_threshold}

Validation:
  Mode: {self.kernel_env_validation}

Optional Features:
  Reality Verification: {self.kernel_chat_include_reality_verification}
  Lighthouse KB: {self.kernel_lighthouse_kb_path}
  Runtime Profile: {self.ethos_runtime_profile}

Telemetry:
  Metrics Enabled: {self.kernel_metrics}

Audio Ouroboros:
  Enabled: {self.kernel_audio_ouroboros_enabled}
  Whisper Model: {self.kernel_whisper_model}
════════════════════════════════════════
"""

    def model_dump_public(self) -> dict[str, Any]:
        """Operator-safe dictionary (excludes sensitive values)."""
        return {
            "chat_host": self.chat_host,
            "chat_port": self.chat_port,
            "kernel_mode": self.kernel_mode,
            "kernel_variability": self.kernel_variability,
            "kernel_api_docs": self.kernel_api_docs,
            "kernel_bayesian_n_samples": self.kernel_bayesian_n_samples,
            "kernel_semantic_chat_enabled": self.kernel_semantic_chat_enabled,
            "kernel_semantic_chat_sim_block_threshold": self.kernel_semantic_chat_sim_block_threshold,
            "kernel_semantic_chat_sim_allow_threshold": self.kernel_semantic_chat_sim_allow_threshold,
            "kernel_chat_turn_timeout_seconds": self.kernel_chat_turn_timeout_seconds,
            "kernel_chat_threadpool_workers": self.kernel_chat_threadpool_workers,
            "kernel_chat_async_llm_http": self.kernel_chat_async_llm_http,
            "kernel_chat_json_offload": self.kernel_chat_json_offload,
            "kernel_governance_enabled": self.kernel_governance_enabled,
            "kernel_narrative_enabled": self.kernel_narrative_enabled,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "kernel_metrics": self.kernel_metrics,
        }

    def check_deprecated(self) -> None:
        """Verify if any environment variables are scheduled for removal."""
        # TODO: Implement ADR 0016 B2 logic
        pass

    def validate_startup(self) -> None:
        """Full cross-check of environment variables for contradictions (Issue #7)."""
        # TODO: Implement environment combo validation logic
        pass


def _parse_env_validation_mode() -> Literal["off", "warn", "strict"]:
    """Parse KERNEL_ENV_VALIDATION environment variable."""
    raw = os.environ.get("KERNEL_ENV_VALIDATION", "").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return "off"
    if raw in ("warn", "warning"):
        return "warn"
    if raw in ("1", "true", "yes", "on", "strict", ""):
        return "strict"
    logger.warning("unknown KERNEL_ENV_VALIDATION=%r; defaulting to strict", raw)
    return "strict"


def kernel_settings() -> KernelSettings:
    """Load from ``os.environ`` (no cross-request cache — tests may monkeypatch)."""
    return KernelSettings.from_env()
