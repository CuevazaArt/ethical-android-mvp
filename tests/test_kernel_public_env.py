"""KernelPublicEnv typed snapshot (Issue 7)."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.validators.env_policy import collect_env_violations
from src.validators.kernel_public_env import KernelPublicEnv


def test_consistency_violations_match_collect_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_JUDICIAL_MOCK_COURT", "1")
    monkeypatch.delenv("KERNEL_JUDICIAL_ESCALATION", raising=False)
    snap = KernelPublicEnv.from_environ()
    assert snap.consistency_violations() == collect_env_violations()


def test_kernel_public_env_includes_profile_and_validation_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ETHOS_RUNTIME_PROFILE", "lan_operational")
    monkeypatch.setenv("KERNEL_ENV_VALIDATION", "strict")
    snap = KernelPublicEnv.from_environ()
    assert snap.ethos_runtime_profile == "lan_operational"
    assert snap.env_validation == "strict"
