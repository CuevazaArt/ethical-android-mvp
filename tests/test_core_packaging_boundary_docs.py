"""
Regression tests for Issue #4 — documented core vs theater packaging boundary.

Locks invariants from ADR 0001, CORE_DECISION_CHAIN.md, and pyproject.toml so
integrators do not silently drift from the shipping story.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_text(rel: str) -> str:
    p = _REPO_ROOT / rel
    return p.read_text(encoding="utf-8")


def test_pyproject_matches_adr_0001_packaging_posture() -> None:
    raw = (_REPO_ROOT / "pyproject.toml").read_bytes()
    data = tomllib.loads(raw.decode("utf-8"))
    proj = data["project"]
    assert proj["name"] == "ethos-kernel"
    assert proj["version"] == "0.0.0"
    assert "theater" in proj["optional-dependencies"]
    assert proj["optional-dependencies"]["theater"] == []
    scripts = proj["scripts"]
    assert scripts["ethos"] == "src.ethos_cli:main"
    assert scripts["ethos-runtime"] == "src.chat_server:main"


def test_core_decision_chain_documents_final_action_ownership() -> None:
    doc = _read_text("docs/proposals/CORE_DECISION_CHAIN.md")
    assert "Who sets `final_action`?" in doc
    assert "WeightedEthicsScorer" in doc
    assert "AbsoluteEvilDetector" in doc
    assert "MockDAO" in doc


def test_adr_0001_references_canonical_chain_doc() -> None:
    doc = _read_text("docs/adr/0001-packaging-core-boundary.md")
    assert "Accepted" in doc
    assert "CORE_DECISION_CHAIN.md" in doc
    assert "theater" in doc.lower()
