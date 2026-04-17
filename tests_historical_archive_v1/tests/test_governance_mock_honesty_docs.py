"""
Doc drift guards for MODEL_CRITICAL_BACKLOG #4 / Issue #6 — MockDAO vs scalar policy.

Integration tests already assert `final_action` is scorer-driven (e.g. IT-06 in
``tests/integration/test_cross_tier_decisions.py``). These tests lock the **honest
framing** in canonical docs so operators and reviewers cannot silently regress the
narrative without updating proposals.
"""

from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (_REPO / rel).read_text(encoding="utf-8")


def test_mock_dao_simulation_limits_states_pipeline_independence():
    text = _read("docs/proposals/MOCK_DAO_SIMULATION_LIMITS.md")
    assert "MockDAO" in text
    assert "final_action" in text
    assert "does **not** read `MockDAO`" in text


def test_core_decision_chain_mockdao_not_final_action():
    text = _read("docs/proposals/CORE_DECISION_CHAIN.md")
    assert "MockDAO" in text
    assert "Who sets `final_action`?" in text
    assert "No:" in text or "Memory / weakness / DAO" in text


def test_governance_mockdao_and_l0_doc_exists():
    text = _read("docs/proposals/GOVERNANCE_MOCKDAO_AND_L0.md")
    assert "L0" in text
    assert "MockDAO" in text.lower() or "mock" in text.lower()
