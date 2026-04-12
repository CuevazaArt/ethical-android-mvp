"""
Central Pydantic model for **chat server** environment variables.

``chat_server.py`` reads booleans and bind addresses here so operators have a single schema
and field descriptions. Other modules may still read ``os.environ`` directly; migrating them
is incremental.

See also: ``README.md`` (Chat server environment), ``docs/proposals/KERNEL_ENV_POLICY.md``.
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
        }


def chat_server_settings() -> ChatServerSettings:
    """Load from ``os.environ`` (no cross-request cache — tests may monkeypatch env)."""
    return ChatServerSettings.from_env()
