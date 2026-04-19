"""
Central Pydantic model for **chat server** environment variables.

⚠️  DEPRECATED: This module is replaced by src.settings.KernelSettings (Phase 3).
Use `from src.settings import KernelSettings` instead.

This module remains for backward compatibility through v1.1.
Operators should migrate to KernelSettings for unified configuration.

``chat_server.py`` reads booleans and bind addresses here so operators have a single schema
and field descriptions. Other modules may still read ``os.environ`` directly; migrating them
is incremental.

See also: ``README.md`` (Chat server environment), ``docs/proposals/README.md``.
Migration guide: docs/PYDANTIC_SETTINGS_CONSOLIDATION_PLAN.md
"""

from __future__ import annotations

import os
import warnings
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Emit deprecation warning on module import
warnings.warn(
    "chat_settings.ChatServerSettings is deprecated as of v1.0 and will be removed in v1.2. "
    "Use src.settings.KernelSettings instead. "
    "See docs/PYDANTIC_SETTINGS_CONSOLIDATION_PLAN.md for migration guide.",
    DeprecationWarning,
    stacklevel=2,
)


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


def _env_optional_positive_float(name: str) -> float | None:
    """Unset/empty or non-positive → no limit; otherwise seconds as float."""
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        v = float(raw)
    except ValueError:
        return None
    return v if v > 0.0 else None


# WebSocket: reject inbound text frames larger than this (UTF-8 byte length) before json.loads.
_DEFAULT_CHAT_WS_MAX_MESSAGE_BYTES = 2 * 1024 * 1024
_CAP_CHAT_WS_MAX_MESSAGE_BYTES = 32 * 1024 * 1024
# Allow operators (and tests) to set a strict cap; absurdly small values still fall back to default.
_MIN_CHAT_WS_MAX_MESSAGE_BYTES = 64


def _env_chat_ws_max_message_bytes() -> int:
    raw = os.environ.get("KERNEL_CHAT_WS_MAX_MESSAGE_BYTES", "").strip()
    if not raw:
        return _DEFAULT_CHAT_WS_MAX_MESSAGE_BYTES
    try:
        n = int(raw)
    except ValueError:
        return _DEFAULT_CHAT_WS_MAX_MESSAGE_BYTES
    if n < _MIN_CHAT_WS_MAX_MESSAGE_BYTES:
        return _DEFAULT_CHAT_WS_MAX_MESSAGE_BYTES
    return min(n, _CAP_CHAT_WS_MAX_MESSAGE_BYTES)


# Keep in sync with ``CHAT_THREADPOOL_MAX_WORKERS`` in ``real_time_bridge`` (no import — avoid cycles).
_CHAT_THREADPOOL_ENV_CAP = 64


def _env_truthy(name: str, *, default_true: bool = True) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default_true
    if default_true:
        return raw not in ("0", "false", "no", "off")
    return raw in ("1", "true", "yes", "on")


class ChatServerSettings(BaseModel):
    """Subset of env vars consumed by ``src.chat_server`` (extend as needed)."""

    model_config = ConfigDict(extra="ignore")

    chat_host: str = Field(
        default="127.0.0.1",
        description="CHAT_HOST — WebSocket / ASGI bind address.",
    )
    chat_port: int = Field(
        default=8765,
        ge=1,
        le=65535,
        description="CHAT_PORT — WebSocket / ASGI port.",
    )
    kernel_api_docs: bool = Field(
        description="KERNEL_API_DOCS — expose OpenAPI ``/docs``, ``/redoc`` when true.",
    )
    kernel_variability: bool = Field(
        description="KERNEL_VARIABILITY — enable variability engine (default on).",
    )
    llm_mode: str | None = Field(
        description="LLM_MODE — optional override for ``resolve_llm_mode``.",
    )
    kernel_chat_include_malabs_trace: bool = Field(
        description="KERNEL_CHAT_INCLUDE_MALABS_TRACE — include malabs_trace in WebSocket JSON.",
    )
    kernel_chat_turn_timeout_seconds: float | None = Field(
        description=(
            "KERNEL_CHAT_TURN_TIMEOUT — max seconds for one WebSocket chat turn (async wait); "
            "unset = unlimited. With sync worker offload, in-flight httpx may continue until read "
            "timeout unless KERNEL_CHAT_ASYNC_LLM_HTTP is enabled."
        ),
    )
    kernel_chat_async_llm_http: bool = Field(
        description=(
            "KERNEL_CHAT_ASYNC_LLM_HTTP — when true, chat turns use async LLM HTTP on the "
            "event loop (process_chat_turn_async) so asyncio can cancel in-flight requests "
            "(Ollama/HTTP JSON). Default off; see ADR 0002."
        ),
    )
    kernel_chat_threadpool_workers: int = Field(
        ge=0,
        le=_CHAT_THREADPOOL_ENV_CAP,
        description=(
            "KERNEL_CHAT_THREADPOOL_WORKERS — dedicated thread pool size for chat turns; "
            "0 = use Starlette/anyio default thread offload; values are clamped to "
            f"{_CHAT_THREADPOOL_ENV_CAP} (same cap as RealTimeBridge)."
        ),
    )
    kernel_chat_json_offload: bool = Field(
        description=(
            "KERNEL_CHAT_JSON_OFFLOAD — when true (default), build WebSocket JSON "
            "(including optional KERNEL_LLM_MONOLOGUE) in a worker thread so the asyncio "
            "loop stays responsive. Set to 0 for debugging only."
        ),
    )
    kernel_chat_ws_max_message_bytes: int = Field(
        ge=64,
        le=32 * 1024 * 1024,
        description=(
            "KERNEL_CHAT_WS_MAX_MESSAGE_BYTES — max UTF-8 size of a single inbound WebSocket "
            "text frame (JSON) before parse; default 2 MiB, hard cap 32 MiB. Invalid/small values "
            "fall back to default."
        ),
    )

    @classmethod
    def from_env(cls) -> ChatServerSettings:
        return cls(
            chat_host=_env_str("CHAT_HOST", "127.0.0.1"),
            chat_port=_env_int("CHAT_PORT", 8765),
            kernel_api_docs=_env_truthy("KERNEL_API_DOCS", default_true=False),
            kernel_variability=_env_truthy("KERNEL_VARIABILITY", default_true=True),
            llm_mode=_env_optional_str("LLM_MODE"),
            kernel_chat_include_malabs_trace=_env_truthy(
                "KERNEL_CHAT_INCLUDE_MALABS_TRACE", default_true=True
            ),
            kernel_chat_turn_timeout_seconds=_env_optional_positive_float(
                "KERNEL_CHAT_TURN_TIMEOUT"
            ),
            kernel_chat_threadpool_workers=min(
                _CHAT_THREADPOOL_ENV_CAP,
                max(0, _env_int("KERNEL_CHAT_THREADPOOL_WORKERS", 0)),
            ),
            kernel_chat_json_offload=_env_truthy("KERNEL_CHAT_JSON_OFFLOAD", default_true=True),
            kernel_chat_async_llm_http=_env_truthy(
                "KERNEL_CHAT_ASYNC_LLM_HTTP", default_true=False
            ),
            kernel_chat_ws_max_message_bytes=_env_chat_ws_max_message_bytes(),
        )

    def model_dump_public(self) -> dict[str, Any]:
        """Operator-safe dict (for ``/health`` extensions or debugging)."""
        return {
            "chat_host": self.chat_host,
            "chat_port": self.chat_port,
            "kernel_api_docs": self.kernel_api_docs,
            "kernel_variability": self.kernel_variability,
            "llm_mode_set": self.llm_mode is not None,
            "kernel_chat_include_malabs_trace": self.kernel_chat_include_malabs_trace,
            "kernel_chat_turn_timeout_seconds": self.kernel_chat_turn_timeout_seconds,
            "kernel_chat_threadpool_workers": self.kernel_chat_threadpool_workers,
            "kernel_chat_json_offload": self.kernel_chat_json_offload,
            "kernel_chat_async_llm_http": self.kernel_chat_async_llm_http,
            "kernel_chat_ws_max_message_bytes": self.kernel_chat_ws_max_message_bytes,
        }


def chat_server_settings() -> ChatServerSettings:
    """Load from ``os.environ`` (no cross-request cache — tests may monkeypatch env)."""
    return ChatServerSettings.from_env()
