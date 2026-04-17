"""docs/proposals/README.md placeholder stays present (full benchmarks doc may be restored from git)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "proposals" / "README.md"


def test_proposals_readme_exists():
    text = DOC.read_text(encoding="utf-8")
    assert "docs/proposals" in text.lower()
    assert "PROPOSAL_" in text or "proposal" in text.lower()
