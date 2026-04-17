"""Issue 7 — KERNEL_* rule validation and SUPPORTED_COMBOS partition (see src/validators/env_policy.py)."""

from __future__ import annotations

import logging
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.runtime_profiles import apply_runtime_profile, profile_names
from src.validators.env_policy import (
    SUPPORTED_COMBOS,
    all_supported_profile_names,
    collect_env_violations,
    default_env_validation_for_profile,
    validate_kernel_env,
    validate_supported_combo_partition,
)
from src.validators.kernel_public_env import KernelPublicEnv


def test_kernel_env_validation_defaults_to_strict_when_unset(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_ENV_VALIDATION", raising=False)
    assert KernelPublicEnv.from_environ().env_validation == "strict"


def test_default_env_validation_lab_vs_demo():
    assert default_env_validation_for_profile("perception_hardening_lab") == "warn"
    assert default_env_validation_for_profile("lan_operational") == "strict"
    assert default_env_validation_for_profile("baseline") == "strict"


def test_supported_combos_partition_matches_runtime_profiles():
    validate_supported_combo_partition()
    assert all_supported_profile_names() == frozenset(profile_names())
    overlap: set[str] = set()
    for _tier, names in SUPPORTED_COMBOS.items():
        inter = overlap & set(names)
        assert not inter, f"duplicate profile in tiers: {inter}"
        overlap |= set(names)


@pytest.mark.parametrize("profile_name", profile_names())
def test_nominal_profile_has_no_env_violations(monkeypatch: pytest.MonkeyPatch, profile_name: str):
    # Profiles only set overrides; clear flags that participate in cross-rules so host env
    # cannot make a nominal bundle look inconsistent (e.g. SEMANTIC=0 from shell + hub demo).
    monkeypatch.delenv("KERNEL_SEMANTIC_CHAT_GATE", raising=False)
    apply_runtime_profile(monkeypatch, profile_name)
    assert collect_env_violations() == []


def test_strict_rejects_judicial_mock_without_escalation(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_JUDICIAL_ESCALATION", raising=False)
    monkeypatch.setenv("KERNEL_JUDICIAL_MOCK_COURT", "1")
    with pytest.raises(ValueError, match="KERNEL_JUDICIAL_MOCK_COURT"):
        validate_kernel_env(mode="strict")


def test_strict_rejects_semantic_off_with_hub_dao_vote(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ETHOS_RUNTIME_PROFILE", raising=False)
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    with pytest.raises(ValueError, match="KERNEL_SEMANTIC_CHAT_GATE"):
        validate_kernel_env(mode="strict")


def test_strict_rejects_reality_flag_without_lighthouse(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_LIGHTHOUSE_KB_PATH", raising=False)
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION", "1")
    with pytest.raises(ValueError, match="KERNEL_LIGHTHOUSE_KB_PATH"):
        validate_kernel_env(mode="strict")


def test_validate_kernel_env_off_skips_checks(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_LIGHTHOUSE_KB_PATH", raising=False)
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION", "1")
    validate_kernel_env(mode="off")  # does not raise


def test_warn_logs_violations_without_raise(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    """mode=warn must log consistency issues but not raise (operator escape hatch)."""
    monkeypatch.delenv("KERNEL_JUDICIAL_ESCALATION", raising=False)
    monkeypatch.setenv("KERNEL_JUDICIAL_MOCK_COURT", "1")
    caplog.set_level(logging.WARNING)
    validate_kernel_env(mode="warn")
    assert not any(r.levelno >= logging.ERROR for r in caplog.records)
    assert any("KERNEL_* environment issues" in r.message for r in caplog.records)
