"""
B3 — Environment variable coherence check (ADR 0016 Axis B3).

Validates that the currently active ``KERNEL_*`` environment variables form
a **coherent** configuration — i.e. that no pair of flags is contradictory
or would produce undefined behaviour at startup.

This module is *complementary* to the existing ``src/validators/env_policy.py``
(which checks individual flags). Here we detect **cross-flag** issues:
contradictions, combinations known to be unsafe or ineffective, and flags that
imply missing dependencies.

Usage::

    from src.modules.safety.env_coherence_check import check_env_coherence, CoherenceIssue
    issues = check_env_coherence()
    for issue in issues:
        print(issue.severity, issue.message)

Severity levels:
  ``"error"``   — the combination is unsafe or will crash at runtime.
  ``"warning"`` — the combination may produce unexpected results.
  ``"info"``    — informational note; no action required.
"""
# Status: SCAFFOLD

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class CoherenceIssue:
    """A single cross-flag coherence finding."""

    severity: Severity
    rule_id: str  # short identifier, e.g. "C-001"
    flags: tuple[str, ...]  # env vars involved
    message: str
    hint: str = ""


def _flag(name: str, default: str = "") -> str:
    """Read an env var, stripped and lowercased for boolean comparison."""
    return os.environ.get(name, default).strip().lower()


def _is_on(name: str) -> bool:
    return _flag(name) in ("1", "true", "yes", "on")


def _is_off(name: str) -> bool:
    v = _flag(name)
    return v in ("0", "false", "no", "off", "")


# ---------------------------------------------------------------------------
# Individual coherence rules
# ---------------------------------------------------------------------------


def _rule_semantic_gate_needs_embed(issues: list[CoherenceIssue]) -> None:
    """C-001: semantic chat gate enabled but hash fallback off and no embed URL."""
    if _is_on("KERNEL_SEMANTIC_CHAT_GATE") and _is_off("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK"):
        embed_url = _flag("KERNEL_SEMANTIC_EMBED_URL")
        if not embed_url:
            issues.append(
                CoherenceIssue(
                    severity="warning",
                    rule_id="C-001",
                    flags=(
                        "KERNEL_SEMANTIC_CHAT_GATE",
                        "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK",
                        "KERNEL_SEMANTIC_EMBED_URL",
                    ),
                    message=(
                        "KERNEL_SEMANTIC_CHAT_GATE=1 but no KERNEL_SEMANTIC_EMBED_URL and "
                        "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK=0. Semantic MalAbs will fail on "
                        "every embedding request."
                    ),
                    hint="Set KERNEL_SEMANTIC_EMBED_URL or enable KERNEL_SEMANTIC_EMBED_HASH_FALLBACK=1.",
                )
            )


def _rule_dual_vote_needs_model(issues: list[CoherenceIssue]) -> None:
    """C-002: dual perception vote enabled but no secondary model configured."""
    if _is_on("KERNEL_PERCEPTION_DUAL_VOTE"):
        dual_model = _flag("KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL")
        primary_model = _flag("OLLAMA_MODEL")
        if not dual_model and not primary_model:
            issues.append(
                CoherenceIssue(
                    severity="warning",
                    rule_id="C-002",
                    flags=("KERNEL_PERCEPTION_DUAL_VOTE", "KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL"),
                    message=(
                        "KERNEL_PERCEPTION_DUAL_VOTE=1 but KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL "
                        "and OLLAMA_MODEL are both unset. Dual vote will use the same default "
                        "model for both samples — no independent check."
                    ),
                    hint="Set KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL to a different model.",
                )
            )


def _rule_checkpoint_fernet_key_needed(issues: list[CoherenceIssue]) -> None:
    """C-003: encrypted checkpoint path set but no Fernet key."""
    checkpoint_path = _flag("KERNEL_CHECKPOINT_PATH")
    if checkpoint_path and not _flag("KERNEL_CHECKPOINT_FERNET_KEY"):
        issues.append(
            CoherenceIssue(
                severity="info",
                rule_id="C-003",
                flags=("KERNEL_CHECKPOINT_PATH", "KERNEL_CHECKPOINT_FERNET_KEY"),
                message=(
                    "KERNEL_CHECKPOINT_PATH is set but KERNEL_CHECKPOINT_FERNET_KEY is absent. "
                    "Checkpoint will be stored unencrypted."
                ),
                hint="Set KERNEL_CHECKPOINT_FERNET_KEY for encrypted persistence.",
            )
        )


def _rule_field_control_needs_token(issues: list[CoherenceIssue]) -> None:
    """C-004: field control enabled without pairing token."""
    if _is_on("KERNEL_FIELD_CONTROL"):
        token = _flag("KERNEL_FIELD_PAIRING_TOKEN")
        if not token:
            issues.append(
                CoherenceIssue(
                    severity="error",
                    rule_id="C-004",
                    flags=("KERNEL_FIELD_CONTROL", "KERNEL_FIELD_PAIRING_TOKEN"),
                    message=(
                        "KERNEL_FIELD_CONTROL=1 but KERNEL_FIELD_PAIRING_TOKEN is empty. "
                        "The phone pairing endpoint will be open to unauthenticated connections."
                    ),
                    hint="Set KERNEL_FIELD_PAIRING_TOKEN to a random secret before enabling field control.",
                )
            )


def _rule_field_control_wan_warning(issues: list[CoherenceIssue]) -> None:
    """C-005: field control WAN allowed — security warning."""
    if _is_on("KERNEL_FIELD_CONTROL") and _is_on("KERNEL_FIELD_ALLOW_WAN"):
        issues.append(
            CoherenceIssue(
                severity="warning",
                rule_id="C-005",
                flags=("KERNEL_FIELD_CONTROL", "KERNEL_FIELD_ALLOW_WAN"),
                message=(
                    "KERNEL_FIELD_CONTROL=1 and KERNEL_FIELD_ALLOW_WAN=1. The phone relay "
                    "endpoint is accessible from non-LAN addresses. Only enable for controlled "
                    "environments with TLS and network firewall."
                ),
                hint="Set KERNEL_FIELD_ALLOW_WAN=0 unless you have TLS + firewall in place.",
            )
        )


def _rule_metrics_without_prometheus(issues: list[CoherenceIssue]) -> None:
    """C-006: metrics enabled but prometheus not importable (best-effort check)."""
    if _is_on("KERNEL_METRICS"):
        try:
            import prometheus_client  # noqa: F401
        except ImportError:
            issues.append(
                CoherenceIssue(
                    severity="warning",
                    rule_id="C-006",
                    flags=("KERNEL_METRICS",),
                    message=(
                        "KERNEL_METRICS=1 but 'prometheus_client' is not installed. "
                        "The /metrics endpoint will not be available."
                    ),
                    hint="pip install prometheus_client  or set KERNEL_METRICS=0.",
                )
            )


def _rule_judicial_mock_court_needs_dao(issues: list[CoherenceIssue]) -> None:
    """C-007: mock court needs DAO_VOTE enabled to function."""
    if _is_on("KERNEL_JUDICIAL_MOCK_COURT") and not _is_on("KERNEL_MORAL_HUB_DAO_VOTE"):
        issues.append(
            CoherenceIssue(
                severity="warning",
                rule_id="C-007",
                flags=("KERNEL_JUDICIAL_MOCK_COURT", "KERNEL_MORAL_HUB_DAO_VOTE"),
                message=(
                    "KERNEL_JUDICIAL_MOCK_COURT=1 but KERNEL_MORAL_HUB_DAO_VOTE=0. "
                    "The mock court simulates a DAO vote but the DAO WebSocket channel "
                    "is disabled — court verdicts will still run but cannot be queried "
                    "via WebSocket."
                ),
                hint="Set KERNEL_MORAL_HUB_DAO_VOTE=1 to expose DAO messages over WebSocket.",
            )
        )


def _rule_turn_timeout_vs_ollama_timeout(issues: list[CoherenceIssue]) -> None:
    """C-008: chat turn timeout shorter than Ollama timeout creates confusing UX."""
    chat_to_raw = _flag("KERNEL_CHAT_TURN_TIMEOUT")
    ollama_to_raw = _flag("OLLAMA_TIMEOUT")
    try:
        chat_to = float(chat_to_raw) if chat_to_raw else None
        ollama_to = float(ollama_to_raw) if ollama_to_raw else None
    except ValueError:
        return

    if chat_to is not None and ollama_to is not None and chat_to < ollama_to:
        issues.append(
            CoherenceIssue(
                severity="info",
                rule_id="C-008",
                flags=("KERNEL_CHAT_TURN_TIMEOUT", "OLLAMA_TIMEOUT"),
                message=(
                    f"KERNEL_CHAT_TURN_TIMEOUT={chat_to}s < OLLAMA_TIMEOUT={ollama_to}s. "
                    "The async wait will expire before the Ollama HTTP call does; "
                    "the worker thread continues running after the WebSocket timeout."
                ),
                hint="Set OLLAMA_TIMEOUT <= KERNEL_CHAT_TURN_TIMEOUT for clean cancellation "
                "(true async cancellation is future work — see ADR 0002).",
            )
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_ALL_RULES = [
    _rule_semantic_gate_needs_embed,
    _rule_dual_vote_needs_model,
    _rule_checkpoint_fernet_key_needed,
    _rule_field_control_needs_token,
    _rule_field_control_wan_warning,
    _rule_metrics_without_prometheus,
    _rule_judicial_mock_court_needs_dao,
    _rule_turn_timeout_vs_ollama_timeout,
]


def check_env_coherence() -> list[CoherenceIssue]:
    """
    Run all registered coherence rules against the current environment.

    Returns a list of :class:`CoherenceIssue` (may be empty if configuration
    is coherent). Issues are sorted by severity (errors first).
    """
    issues: list[CoherenceIssue] = []
    for rule in _ALL_RULES:
        rule(issues)

    _sev_order = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda i: _sev_order.get(i.severity, 9))
    return issues


def check_env_coherence_or_raise() -> None:
    """
    Run coherence checks and raise ``ValueError`` if any error-level issues
    are found. Warnings and info are logged only.

    Intended for startup validation in production deployments.
    """
    import logging

    logger = logging.getLogger(__name__)
    issues = check_env_coherence()
    errors = []

    for issue in issues:
        if issue.severity == "error":
            logger.error(
                "env coherence %s [%s]: %s  Hint: %s",
                issue.rule_id,
                ", ".join(issue.flags),
                issue.message,
                issue.hint,
            )
            errors.append(issue)
        elif issue.severity == "warning":
            logger.warning(
                "env coherence %s [%s]: %s  Hint: %s",
                issue.rule_id,
                ", ".join(issue.flags),
                issue.message,
                issue.hint,
            )
        else:
            logger.info("env coherence %s: %s", issue.rule_id, issue.message)

    if errors:
        msgs = "; ".join(f"[{e.rule_id}] {e.message}" for e in errors)
        raise ValueError(f"KERNEL env coherence errors (fix before starting): {msgs}")
