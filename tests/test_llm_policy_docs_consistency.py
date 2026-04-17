"""
G-04 — legacy perception/verbal LLM backend policy keys stay visible to operators.

Ensures KERNEL_ENV_POLICY.md and kernel_env_operator families remain aligned with
PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md (unified degradation story).
"""

from __future__ import annotations

from pathlib import Path

from src.validators.kernel_env_operator import classify_env_key

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _policy_doc() -> str:
    return (_REPO_ROOT / "docs/proposals/KERNEL_ENV_POLICY.md").read_text(encoding="utf-8")


def test_kernel_env_policy_indexes_legacy_llm_backend_policies() -> None:
    text = _policy_doc()
    assert "KERNEL_PERCEPTION_BACKEND_POLICY" in text
    assert "KERNEL_VERBAL_LLM_BACKEND_POLICY" in text
    assert "KERNEL_LLM_GLOBAL_DEFAULT_POLICY" in text
    assert "KERNEL_PERCEPTIVE_LOBE_PROBE_URL" in text
    assert "PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md" in text


def test_classify_env_key_perception_backend_policy() -> None:
    assert classify_env_key("KERNEL_PERCEPTION_BACKEND_POLICY") == "Perception / sensors"


def test_classify_env_key_verbal_llm_backend_policy() -> None:
    assert classify_env_key("KERNEL_VERBAL_LLM_BACKEND_POLICY") == "LLM / variability / generative"


def test_classify_env_key_global_default_policy() -> None:
    assert classify_env_key("KERNEL_LLM_GLOBAL_DEFAULT_POLICY") == "LLM / variability / generative"
