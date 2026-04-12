"""Issue 7 — KERNEL_* rule validation and SUPPORTED_COMBOS partition (see src/validators/env_policy.py)."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.runtime_profiles import apply_runtime_profile, profile_names
from src.validators.env_policy import (
    SUPPORTED_COMBOS,
    all_supported_profile_names,
    collect_env_violations,
    validate_kernel_env,
    validate_supported_combo_partition,
)


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
    apply_runtime_profile(monkeypatch, profile_name)
    assert collect_env_violations() == []


def test_strict_rejects_judicial_mock_without_escalation(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("KERNEL_JUDICIAL_ESCALATION", raising=False)
    monkeypatch.setenv("KERNEL_JUDICIAL_MOCK_COURT", "1")
    with pytest.raises(ValueError, match="KERNEL_JUDICIAL_MOCK_COURT"):
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
