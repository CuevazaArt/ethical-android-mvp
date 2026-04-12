"""
Typed public surface for KERNEL_* variables used in env policy (Issue 7).

This is **not** a full migration of every ``os.environ`` read in the codebase — that remains
incremental. It **does** centralize the variables that participate in **consistency rules**
and startup validation so invalid combinations are **data**, not ad-hoc ``if`` chains.

See ``docs/proposals/KERNEL_ENV_TYPED_PUBLIC_API.md`` and ``KERNEL_ENV_POLICY.md``.
"""

from __future__ import annotations

import logging
import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..runtime_profiles import profile_names

logger = logging.getLogger(__name__)


def _truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _falsy_or_unset(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return True
    return v in ("0", "false", "no", "off")


def _parse_env_validation_mode() -> Literal["off", "warn", "strict"]:
    raw = os.environ.get("KERNEL_ENV_VALIDATION", "").strip().lower()
    if raw in ("", "warn", "warning"):
        return "warn"
    if raw in ("0", "false", "no", "off"):
        return "off"
    if raw in ("1", "true", "yes", "on", "strict"):
        return "strict"
    logger.warning("unknown KERNEL_ENV_VALIDATION=%r; defaulting to warn", raw)
    return "warn"


class KernelPublicEnv(BaseModel):
    """
    Parsed KERNEL_* subset relevant to **cross-flag consistency** (Issue 7).

    Other modules may still read ``os.environ`` directly; extend this model when a flag
    joins a documented rule or needs typed coercion at startup.
    """

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    env_validation: Literal["off", "warn", "strict"] = Field(
        description="KERNEL_ENV_VALIDATION — warn (default), strict (fail on violations), off.",
    )
    judicial_escalation: bool = Field(description="KERNEL_JUDICIAL_ESCALATION")
    judicial_mock_court: bool = Field(description="KERNEL_JUDICIAL_MOCK_COURT")
    chat_include_reality_verification: bool = Field(
        description="KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION",
    )
    lighthouse_kb_path: str | None = Field(
        default=None,
        description="KERNEL_LIGHTHOUSE_KB_PATH — optional path for lighthouse KB.",
    )
    ethos_runtime_profile: str | None = Field(
        default=None,
        description="ETHOS_RUNTIME_PROFILE — nominal bundle name (documentation / merge).",
    )

    @classmethod
    def from_environ(cls) -> KernelPublicEnv:
        """Build from the current process environment (for tests, monkeypatch ``os.environ``)."""
        lk = os.environ.get("KERNEL_LIGHTHOUSE_KB_PATH", "").strip()
        prof = os.environ.get("ETHOS_RUNTIME_PROFILE", "").strip()
        return cls(
            env_validation=_parse_env_validation_mode(),
            judicial_escalation=_truthy("KERNEL_JUDICIAL_ESCALATION"),
            judicial_mock_court=_truthy("KERNEL_JUDICIAL_MOCK_COURT"),
            chat_include_reality_verification=_truthy("KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION"),
            lighthouse_kb_path=lk if lk else None,
            ethos_runtime_profile=prof if prof else None,
        )

    def consistency_violations(self) -> list[str]:
        """Human-readable constraint violations (same semantics as legacy ``collect_env_violations``)."""
        out: list[str] = []
        if self.judicial_mock_court and not self.judicial_escalation:
            out.append(
                "KERNEL_JUDICIAL_MOCK_COURT is enabled but KERNEL_JUDICIAL_ESCALATION is off; "
                "mock court runs only when escalation is enabled (see judicial_escalation.py)."
            )
        if self.chat_include_reality_verification and not (self.lighthouse_kb_path or "").strip():
            out.append(
                "KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1 without KERNEL_LIGHTHOUSE_KB_PATH; "
                "reality verification may no-op (set a fixture path for demos)."
            )
        if self.ethos_runtime_profile and self.ethos_runtime_profile not in profile_names():
            out.append(
                f"ETHOS_RUNTIME_PROFILE={self.ethos_runtime_profile!r} is not a known nominal profile "
                "(see runtime_profiles.RUNTIME_PROFILES)."
            )
        return out

    def model_dump_operator_summary(self) -> dict[str, object]:
        """Safe subset for logs or ``/health`` (no secrets)."""
        return {
            "env_validation": self.env_validation,
            "judicial_escalation": self.judicial_escalation,
            "judicial_mock_court": self.judicial_mock_court,
            "chat_include_reality_verification": self.chat_include_reality_verification,
            "lighthouse_kb_path_set": bool(self.lighthouse_kb_path),
            "ethos_runtime_profile": self.ethos_runtime_profile,
        }
